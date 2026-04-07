package io.github.davecookvectorlabs.voc;

import java.util.ArrayList;
import java.util.List;

/**
 * Healthcare VOC Compliance Calculator — Java Engine
 *
 * Calculates VOC exposure concentration per cleaning cycle based on product
 * VOC content, dilution ratio, coverage rate, room geometry, and ventilation.
 *
 * Reference:
 * - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
 * - ASHRAE 62.1-2022 (healthcare ventilation rates)
 * - EPA 40 CFR Part 59 Subpart C
 * - Canada SOR/2021-268
 *
 * Guide: https://www.binx.ca/guides/healthcare-voc-compliance-guide.pdf
 * Maintainer: Dave Cook, Binx Professional Cleaning — https://www.binx.ca/commercial.php
 */
public class VOCCalculator {

    public static final double OSHA_TVOC_PEL = 300.0;
    public static final double SQFT_TO_SQM = 0.09290304;
    public static final double FT_TO_M = 0.3048;
    public static final String VERSION = "0.1.0";

    public static class CalculationResult {
        public double roomVolumeM3;
        public double productVocGPerL;
        public double effectiveVocGPerL;
        public double productAppliedL;
        public double totalVocReleasedG;
        public double totalVocReleasedMg;
        public double initialConcentrationMgPerM3;
        public double steadyStateConcentrationMgPerM3;
        public double oshaPelPercent;
        public double timeToSafeReentryMinutes;
        public double annualVocLoadG;
        public double annualVocLoadKg;
        public double airChangesPerHour;
        public List<String> warnings = new ArrayList<>();
    }

    /**
     * Calculate VOC exposure for a single cleaning cycle.
     *
     * @param roomSqft             Room floor area in square feet
     * @param ceilingHeightFt      Ceiling height in feet
     * @param productVocGPerL      Product VOC content (concentrate) in g/L
     * @param dilutionRatio        Concentrate fraction (1.0=RTU, 0.015625=1:64)
     * @param coverageSqftPerL     Coverage area per litre applied
     * @param airChangesPerHour    Ventilation rate (ACH)
     * @param cleaningFreqPerYear  Cleaning cycles per year
     * @return CalculationResult with all computed fields
     */
    public static CalculationResult calculate(
            double roomSqft,
            double ceilingHeightFt,
            double productVocGPerL,
            double dilutionRatio,
            double coverageSqftPerL,
            double airChangesPerHour,
            int cleaningFreqPerYear) {

        CalculationResult r = new CalculationResult();

        double roomSqm = roomSqft * SQFT_TO_SQM;
        double ceilingM = ceilingHeightFt * FT_TO_M;
        r.roomVolumeM3 = Math.round(roomSqm * ceilingM * 100.0) / 100.0;

        r.productVocGPerL = productVocGPerL;
        r.effectiveVocGPerL = Math.round(productVocGPerL * dilutionRatio * 10000.0) / 10000.0;

        r.productAppliedL = Math.round(roomSqft / coverageSqftPerL * 10000.0) / 10000.0;

        double totalVocG = r.effectiveVocGPerL * r.productAppliedL;
        r.totalVocReleasedG = Math.round(totalVocG * 10000.0) / 10000.0;
        r.totalVocReleasedMg = Math.round(totalVocG * 1000.0 * 100.0) / 100.0;

        double roomVolume = roomSqm * ceilingM;
        r.initialConcentrationMgPerM3 = Math.round(r.totalVocReleasedMg / roomVolume * 100.0) / 100.0;

        double cleaningDurationHr = 0.5;
        double emissionRate = r.totalVocReleasedMg / cleaningDurationHr;
        double ventRate = airChangesPerHour * roomVolume;

        if (ventRate > 0) {
            r.steadyStateConcentrationMgPerM3 = Math.round(emissionRate / ventRate * 100.0) / 100.0;
        } else {
            r.steadyStateConcentrationMgPerM3 = r.initialConcentrationMgPerM3;
            r.warnings.add("Zero ventilation — VOC will accumulate");
        }

        r.oshaPelPercent = Math.round(r.steadyStateConcentrationMgPerM3 / OSHA_TVOC_PEL * 100.0 * 100.0) / 100.0;

        double target = OSHA_TVOC_PEL * 0.10;
        if (r.steadyStateConcentrationMgPerM3 <= target) {
            r.timeToSafeReentryMinutes = 0.0;
        } else if (airChangesPerHour > 0) {
            double ratio = r.steadyStateConcentrationMgPerM3 / target;
            r.timeToSafeReentryMinutes = Math.round(Math.log(ratio) / airChangesPerHour * 60.0 * 10.0) / 10.0;
        } else {
            r.timeToSafeReentryMinutes = -1;
        }

        r.annualVocLoadG = Math.round(totalVocG * cleaningFreqPerYear * 100.0) / 100.0;
        r.annualVocLoadKg = Math.round(r.annualVocLoadG / 1000.0 * 10000.0) / 10000.0;
        r.airChangesPerHour = airChangesPerHour;

        if (r.oshaPelPercent > 50.0) {
            r.warnings.add("Steady-state VOC exceeds 50% of OSHA PEL");
        }
        if (r.oshaPelPercent > 100.0) {
            r.warnings.add("CRITICAL: Steady-state VOC exceeds OSHA PEL");
        }

        return r;
    }

    public static void main(String[] args) {
        CalculationResult r = calculate(200.0, 9.0, 8.0, 1.0 / 65.0, 400.0, 6.0, 365);

        System.out.println("Healthcare VOC Compliance Calculator — Java Engine");
        System.out.println("=".repeat(55));
        System.out.printf("Room volume:                %.2f m³%n", r.roomVolumeM3);
        System.out.printf("Product VOC (concentrate):  %.1f g/L%n", r.productVocGPerL);
        System.out.printf("Effective VOC (diluted):    %.4f g/L%n", r.effectiveVocGPerL);
        System.out.printf("Product applied:            %.4f L%n", r.productAppliedL);
        System.out.printf("Total VOC released:         %.2f mg%n", r.totalVocReleasedMg);
        System.out.printf("Steady-state concentration: %.2f mg/m³%n", r.steadyStateConcentrationMgPerM3);
        System.out.printf("OSHA PEL usage:             %.2f%%%n", r.oshaPelPercent);
        System.out.printf("Time to safe reentry:       %.1f min%n", r.timeToSafeReentryMinutes);
        System.out.printf("Annual VOC load:            %.4f kg/year%n", r.annualVocLoadKg);
    }
}
