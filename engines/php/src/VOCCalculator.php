<?php
/**
 * Healthcare VOC Compliance Calculator — PHP Engine
 *
 * Calculates VOC exposure concentration per cleaning cycle based on product
 * VOC content, dilution ratio, coverage rate, room geometry, and ventilation.
 *
 * Reference:
 * - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
 * - ASHRAE 62.1-2022 (healthcare ventilation rates)
 * - EPA 40 CFR Part 59 Subpart C
 * - Canada SOR/2021-268
 */

namespace DaveCook\HealthcareVocCompliance;

class VOCCalculator
{
    const OSHA_TVOC_PEL = 300.0;
    const SQFT_TO_SQM = 0.09290304;
    const FT_TO_M = 0.3048;
    const VERSION = '0.1.0';

    const ASHRAE_HEALTHCARE_ACH = [
        'patient_room' => 6,
        'operating_room' => 20,
        'icu' => 12,
        'corridor' => 4,
        'waiting_room' => 6,
        'exam_room' => 6,
        'laboratory' => 12,
        'pharmacy' => 8,
        'dietary_kitchen' => 10,
        'laundry' => 10,
        'soiled_utility' => 10,
        'clean_utility' => 4,
        'bathroom' => 10,
        'janitor_closet' => 10,
        'general_office' => 4,
    ];

    /**
     * Calculate VOC exposure for a single cleaning cycle.
     *
     * @param float $roomSqft            Room floor area in square feet
     * @param float $ceilingHeightFt      Ceiling height in feet
     * @param float $productVocGPerL      Product VOC content (concentrate) in g/L
     * @param float $dilutionRatio        Concentrate fraction (1.0=RTU)
     * @param float $coverageSqftPerL     Coverage area per litre applied
     * @param float $airChangesPerHour    Ventilation rate (ACH)
     * @param int   $cleaningFreqPerYear  Cleaning cycles per year
     * @param string $spaceType           Healthcare space type
     * @return array Calculation results
     */
    public static function calculate(
        float $roomSqft,
        float $ceilingHeightFt = 9.0,
        float $productVocGPerL = 8.0,
        float $dilutionRatio = 1.0,
        float $coverageSqftPerL = 400.0,
        float $airChangesPerHour = 6.0,
        int $cleaningFreqPerYear = 365,
        string $spaceType = 'patient_room'
    ): array {
        $warnings = [];

        $roomSqm = $roomSqft * self::SQFT_TO_SQM;
        $ceilingM = $ceilingHeightFt * self::FT_TO_M;
        $roomVolume = $roomSqm * $ceilingM;

        $effectiveVoc = $productVocGPerL * $dilutionRatio;
        $productApplied = $roomSqft / $coverageSqftPerL;
        $totalVocG = $effectiveVoc * $productApplied;
        $totalVocMg = $totalVocG * 1000.0;

        $initialConc = $totalVocMg / $roomVolume;

        $cleaningDurationHr = 0.5;
        $emissionRate = $totalVocMg / $cleaningDurationHr;
        $ventRate = $airChangesPerHour * $roomVolume;

        if ($ventRate > 0) {
            $steadyState = $emissionRate / $ventRate;
        } else {
            $steadyState = $initialConc;
            $warnings[] = 'Zero ventilation — VOC will accumulate';
        }

        $oshaPct = ($steadyState / self::OSHA_TVOC_PEL) * 100.0;

        $target = self::OSHA_TVOC_PEL * 0.10;
        if ($steadyState <= $target) {
            $reentry = 0.0;
        } elseif ($airChangesPerHour > 0) {
            $ratio = $steadyState / $target;
            $reentry = (log($ratio) / $airChangesPerHour) * 60.0;
        } else {
            $reentry = -1.0;
        }

        $annualG = $totalVocG * $cleaningFreqPerYear;

        $ashraeMin = self::ASHRAE_HEALTHCARE_ACH[$spaceType] ?? 4;
        if ($airChangesPerHour < $ashraeMin) {
            $warnings[] = "Ventilation ({$airChangesPerHour} ACH) below ASHRAE minimum for {$spaceType} ({$ashraeMin} ACH)";
        }

        if ($oshaPct > 50.0) {
            $warnings[] = 'Steady-state VOC exceeds 50% of OSHA PEL';
        }
        if ($oshaPct > 100.0) {
            $warnings[] = 'CRITICAL: Steady-state VOC exceeds OSHA PEL';
        }

        return [
            'room_volume_m3' => round($roomVolume, 2),
            'product_voc_g_per_L' => $productVocGPerL,
            'effective_voc_g_per_L' => round($effectiveVoc, 4),
            'product_applied_L' => round($productApplied, 4),
            'total_voc_released_g' => round($totalVocG, 4),
            'total_voc_released_mg' => round($totalVocMg, 2),
            'initial_concentration_mg_per_m3' => round($initialConc, 2),
            'steady_state_concentration_mg_per_m3' => round($steadyState, 2),
            'osha_pel_percent' => round($oshaPct, 2),
            'time_to_safe_reentry_minutes' => round($reentry, 1),
            'annual_voc_load_g' => round($annualG, 2),
            'annual_voc_load_kg' => round($annualG / 1000.0, 4),
            'air_changes_per_hour' => $airChangesPerHour,
            'warnings' => $warnings,
        ];
    }
}

// CLI mode
if (php_sapi_name() === 'cli' && realpath($argv[0] ?? '') === realpath(__FILE__)) {
    $result = VOCCalculator::calculate(200.0, 9.0, 8.0, 1.0 / 65.0, 400.0, 6.0, 365);
    echo "Healthcare VOC Compliance Calculator — PHP Engine\n";
    echo str_repeat('=', 55) . "\n";
    printf("Room volume:                %.2f m³\n", $result['room_volume_m3']);
    printf("Product VOC (concentrate):  %.1f g/L\n", $result['product_voc_g_per_L']);
    printf("Effective VOC (diluted):    %.4f g/L\n", $result['effective_voc_g_per_L']);
    printf("Steady-state concentration: %.2f mg/m³\n", $result['steady_state_concentration_mg_per_m3']);
    printf("OSHA PEL usage:             %.2f%%\n", $result['osha_pel_percent']);
    printf("Annual VOC load:            %.4f kg/year\n", $result['annual_voc_load_kg']);
}
