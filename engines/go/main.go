// Healthcare VOC Compliance Calculator — Go Engine
//
// Calculates VOC exposure concentration per cleaning cycle based on product
// VOC content, dilution ratio, coverage rate, room geometry, and ventilation.
//
// Reference:
// - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
// - ASHRAE 62.1-2022 (healthcare ventilation rates)
// - EPA 40 CFR Part 59 Subpart C
// - Canada SOR/2021-268
//
// Guide: https://www.binx.ca/guides/healthcare-voc-compliance-guide.pdf
// Maintainer: Dave Cook, Binx Professional Cleaning — https://www.binx.ca/commercial.php
package main

import (
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"os"
)

const (
	OshaTvocPEL = 300.0
	SqftToSqm   = 0.09290304
	FtToM        = 0.3048
	Version      = "0.1.0"
)

var ashraeHealthcareACH = map[string]float64{
	"patient_room":    6,
	"operating_room":  20,
	"icu":             12,
	"corridor":        4,
	"waiting_room":    6,
	"exam_room":       6,
	"laboratory":      12,
	"pharmacy":        8,
	"dietary_kitchen": 10,
	"laundry":         10,
	"soiled_utility":  10,
	"clean_utility":   4,
	"bathroom":        10,
	"janitor_closet":  10,
	"general_office":  4,
}

// CalculateRequest holds input parameters for VOC calculation.
type CalculateRequest struct {
	RoomSqft               float64 `json:"room_sqft"`
	CeilingHeightFt        float64 `json:"ceiling_height_ft"`
	ProductVocGPerL        float64 `json:"product_voc_g_per_L"`
	DilutionRatio          float64 `json:"dilution_ratio"`
	CoverageSqftPerL       float64 `json:"coverage_sqft_per_L"`
	AirChangesPerHour      float64 `json:"air_changes_per_hour"`
	CleaningFreqPerYear    int     `json:"cleaning_frequency_per_year"`
	SpaceType              string  `json:"space_type"`
}

// CalculateResult holds the output of a VOC exposure calculation.
type CalculateResult struct {
	RoomVolumeM3                     float64  `json:"room_volume_m3"`
	ProductVocGPerL                  float64  `json:"product_voc_g_per_L"`
	EffectiveVocGPerL                float64  `json:"effective_voc_g_per_L"`
	ProductAppliedL                  float64  `json:"product_applied_L"`
	TotalVocReleasedG                float64  `json:"total_voc_released_g"`
	TotalVocReleasedMg               float64  `json:"total_voc_released_mg"`
	InitialConcentrationMgPerM3      float64  `json:"initial_concentration_mg_per_m3"`
	SteadyStateConcentrationMgPerM3  float64  `json:"steady_state_concentration_mg_per_m3"`
	OshaPelPercent                   float64  `json:"osha_pel_percent"`
	TimeToSafeReentryMinutes         float64  `json:"time_to_safe_reentry_minutes"`
	AnnualVocLoadG                   float64  `json:"annual_voc_load_g"`
	AnnualVocLoadKg                  float64  `json:"annual_voc_load_kg"`
	AirChangesPerHour                float64  `json:"air_changes_per_hour"`
	Warnings                         []string `json:"warnings"`
}

// Calculate computes VOC exposure for a single healthcare cleaning cycle.
func Calculate(req CalculateRequest) CalculateResult {
	warnings := []string{}

	if req.CeilingHeightFt <= 0 {
		req.CeilingHeightFt = 9.0
	}
	if req.DilutionRatio <= 0 {
		req.DilutionRatio = 1.0
	}
	if req.CoverageSqftPerL <= 0 {
		req.CoverageSqftPerL = 400.0
	}
	if req.AirChangesPerHour < 0 {
		req.AirChangesPerHour = 6.0
	}
	if req.CleaningFreqPerYear <= 0 {
		req.CleaningFreqPerYear = 365
	}
	if req.SpaceType == "" {
		req.SpaceType = "patient_room"
	}

	roomSqm := req.RoomSqft * SqftToSqm
	ceilingM := req.CeilingHeightFt * FtToM
	roomVolume := roomSqm * ceilingM

	effectiveVoc := req.ProductVocGPerL * req.DilutionRatio
	productApplied := req.RoomSqft / req.CoverageSqftPerL
	totalVocG := effectiveVoc * productApplied
	totalVocMg := totalVocG * 1000.0

	initialConc := totalVocMg / roomVolume

	cleaningDurationHr := 0.5
	emissionRate := totalVocMg / cleaningDurationHr
	ventRate := req.AirChangesPerHour * roomVolume

	var steadyState float64
	if ventRate > 0 {
		steadyState = emissionRate / ventRate
	} else {
		steadyState = initialConc
		warnings = append(warnings, "Zero ventilation — VOC will accumulate")
	}

	oshaPct := (steadyState / OshaTvocPEL) * 100.0

	target := OshaTvocPEL * 0.10
	var reentry float64
	if steadyState <= target {
		reentry = 0.0
	} else if req.AirChangesPerHour > 0 {
		ratio := steadyState / target
		reentry = (math.Log(ratio) / req.AirChangesPerHour) * 60.0
	} else {
		reentry = -1.0
	}

	annualG := totalVocG * float64(req.CleaningFreqPerYear)

	ashraeMin, ok := ashraeHealthcareACH[req.SpaceType]
	if !ok {
		ashraeMin = 4
	}
	if req.AirChangesPerHour < ashraeMin {
		warnings = append(warnings, fmt.Sprintf(
			"Ventilation (%.0f ACH) below ASHRAE minimum for %s (%.0f ACH)",
			req.AirChangesPerHour, req.SpaceType, ashraeMin))
	}

	if oshaPct > 50.0 {
		warnings = append(warnings, "Steady-state VOC exceeds 50% of OSHA PEL")
	}
	if oshaPct > 100.0 {
		warnings = append(warnings, "CRITICAL: Steady-state VOC exceeds OSHA PEL")
	}

	return CalculateResult{
		RoomVolumeM3:                    math.Round(roomVolume*100) / 100,
		ProductVocGPerL:                 req.ProductVocGPerL,
		EffectiveVocGPerL:               math.Round(effectiveVoc*10000) / 10000,
		ProductAppliedL:                 math.Round(productApplied*10000) / 10000,
		TotalVocReleasedG:               math.Round(totalVocG*10000) / 10000,
		TotalVocReleasedMg:              math.Round(totalVocMg*100) / 100,
		InitialConcentrationMgPerM3:     math.Round(initialConc*100) / 100,
		SteadyStateConcentrationMgPerM3: math.Round(steadyState*100) / 100,
		OshaPelPercent:                  math.Round(oshaPct*100) / 100,
		TimeToSafeReentryMinutes:        math.Round(reentry*10) / 10,
		AnnualVocLoadG:                  math.Round(annualG*100) / 100,
		AnnualVocLoadKg:                 math.Round(annualG/1000*10000) / 10000,
		AirChangesPerHour:               req.AirChangesPerHour,
		Warnings:                        warnings,
	}
}

func handleCalculate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req CalculateRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result := Calculate(req)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"status":"ok","engine":"go","version":"%s"}`, Version)
}

func main() {
	port := "8001"
	for i, arg := range os.Args {
		if arg == "--port" && i+1 < len(os.Args) {
			port = os.Args[i+1]
		}
	}

	if len(os.Args) > 1 && os.Args[1] == "--cli" {
		req := CalculateRequest{
			RoomSqft:            200.0,
			CeilingHeightFt:     9.0,
			ProductVocGPerL:     8.0,
			DilutionRatio:       1.0 / 65.0,
			CoverageSqftPerL:    400.0,
			AirChangesPerHour:   6.0,
			CleaningFreqPerYear: 365,
			SpaceType:           "patient_room",
		}
		result := Calculate(req)
		fmt.Println("Healthcare VOC Compliance Calculator — Go Engine")
		fmt.Println("=======================================================")
		fmt.Printf("Room volume:                %.2f m³\n", result.RoomVolumeM3)
		fmt.Printf("Product VOC (concentrate):  %.1f g/L\n", result.ProductVocGPerL)
		fmt.Printf("Effective VOC (diluted):    %.4f g/L\n", result.EffectiveVocGPerL)
		fmt.Printf("Steady-state concentration: %.2f mg/m³\n", result.SteadyStateConcentrationMgPerM3)
		fmt.Printf("OSHA PEL usage:             %.2f%%\n", result.OshaPelPercent)
		fmt.Printf("Annual VOC load:            %.4f kg/year\n", result.AnnualVocLoadKg)
		return
	}

	http.HandleFunc("/calculate", handleCalculate)
	http.HandleFunc("/health", handleHealth)
	fmt.Printf("Healthcare VOC Calculator (Go) listening on port %s\n", port)
	http.ListenAndServe(":"+port, nil)
}
