# frozen_string_literal: true

# Healthcare VOC Compliance Calculator — Ruby Engine
#
# Calculates VOC exposure concentration per cleaning cycle based on product
# VOC content, dilution ratio, coverage rate, room geometry, and ventilation.
#
# Reference:
# - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
# - ASHRAE 62.1-2022 (healthcare ventilation rates)

module HealthcareVocCompliance
  VERSION = "0.1.0"

  OSHA_TVOC_PEL = 300.0
  SQFT_TO_SQM = 0.09290304
  FT_TO_M = 0.3048

  ASHRAE_HEALTHCARE_ACH = {
    "patient_room" => 6,
    "operating_room" => 20,
    "icu" => 12,
    "corridor" => 4,
    "waiting_room" => 6,
    "exam_room" => 6,
    "laboratory" => 12,
    "pharmacy" => 8,
    "dietary_kitchen" => 10,
    "laundry" => 10,
    "soiled_utility" => 10,
    "clean_utility" => 4,
    "bathroom" => 10,
    "janitor_closet" => 10,
    "general_office" => 4,
  }.freeze

  CalculationResult = Struct.new(
    :room_volume_m3, :product_voc_g_per_l, :effective_voc_g_per_l,
    :product_applied_l, :total_voc_released_g, :total_voc_released_mg,
    :initial_concentration_mg_per_m3, :steady_state_concentration_mg_per_m3,
    :osha_pel_percent, :time_to_safe_reentry_minutes,
    :annual_voc_load_g, :annual_voc_load_kg, :air_changes_per_hour,
    :warnings,
    keyword_init: true
  )

  # Calculate VOC exposure for a single cleaning cycle.
  #
  # @param room_sqft [Float] Room floor area in square feet
  # @param ceiling_height_ft [Float] Ceiling height in feet (default: 9.0)
  # @param product_voc_g_per_l [Float] Product VOC content in g/L
  # @param dilution_ratio [Float] Concentrate fraction (1.0=RTU)
  # @param coverage_sqft_per_l [Float] Coverage per litre applied
  # @param air_changes_per_hour [Float] Ventilation rate (ACH)
  # @param cleaning_frequency_per_year [Integer] Cleaning cycles per year
  # @param space_type [String] Healthcare space type for ASHRAE ref
  # @return [CalculationResult]
  def self.calculate(
    room_sqft:,
    ceiling_height_ft: 9.0,
    product_voc_g_per_l:,
    dilution_ratio: 1.0,
    coverage_sqft_per_l: 400.0,
    air_changes_per_hour: 6.0,
    cleaning_frequency_per_year: 365,
    space_type: "patient_room"
  )
    warnings = []

    room_sqm = room_sqft * SQFT_TO_SQM
    ceiling_m = ceiling_height_ft * FT_TO_M
    room_volume = room_sqm * ceiling_m

    effective_voc = product_voc_g_per_l * dilution_ratio
    product_applied = room_sqft / coverage_sqft_per_l
    total_voc_g = effective_voc * product_applied
    total_voc_mg = total_voc_g * 1000.0

    initial_conc = total_voc_mg / room_volume

    cleaning_duration_hr = 0.5
    emission_rate = total_voc_mg / cleaning_duration_hr
    vent_rate = air_changes_per_hour * room_volume

    steady_state = if vent_rate > 0
                     emission_rate / vent_rate
                   else
                     warnings << "Zero ventilation — VOC will accumulate"
                     initial_conc
                   end

    osha_pct = (steady_state / OSHA_TVOC_PEL) * 100.0

    target = OSHA_TVOC_PEL * 0.10
    reentry = if steady_state <= target
                0.0
              elsif air_changes_per_hour > 0
                ratio = steady_state / target
                (Math.log(ratio) / air_changes_per_hour) * 60.0
              else
                -1.0
              end

    annual_g = total_voc_g * cleaning_frequency_per_year

    ashrae_min = ASHRAE_HEALTHCARE_ACH[space_type] || 4
    if air_changes_per_hour < ashrae_min
      warnings << "Ventilation (#{air_changes_per_hour} ACH) below ASHRAE minimum for #{space_type} (#{ashrae_min} ACH)"
    end

    warnings << "Steady-state VOC exceeds 50% of OSHA PEL" if osha_pct > 50.0
    warnings << "CRITICAL: Steady-state VOC exceeds OSHA PEL" if osha_pct > 100.0

    CalculationResult.new(
      room_volume_m3: room_volume.round(2),
      product_voc_g_per_l: product_voc_g_per_l,
      effective_voc_g_per_l: effective_voc.round(4),
      product_applied_l: product_applied.round(4),
      total_voc_released_g: total_voc_g.round(4),
      total_voc_released_mg: total_voc_mg.round(2),
      initial_concentration_mg_per_m3: initial_conc.round(2),
      steady_state_concentration_mg_per_m3: steady_state.round(2),
      osha_pel_percent: osha_pct.round(2),
      time_to_safe_reentry_minutes: reentry.round(1),
      annual_voc_load_g: annual_g.round(2),
      annual_voc_load_kg: (annual_g / 1000.0).round(4),
      air_changes_per_hour: air_changes_per_hour,
      warnings: warnings,
    )
  end
end

if __FILE__ == $PROGRAM_NAME
  result = HealthcareVocCompliance.calculate(
    room_sqft: 200.0,
    product_voc_g_per_l: 8.0,
    dilution_ratio: 1.0 / 65.0,
    coverage_sqft_per_l: 400.0,
    air_changes_per_hour: 6.0,
    cleaning_frequency_per_year: 365
  )

  puts "Healthcare VOC Compliance Calculator — Ruby Engine"
  puts "=" * 55
  puts "Room volume:                #{result.room_volume_m3} m³"
  puts "Product VOC (concentrate):  #{result.product_voc_g_per_l} g/L"
  puts "Effective VOC (diluted):    #{result.effective_voc_g_per_l} g/L"
  puts "Steady-state concentration: #{result.steady_state_concentration_mg_per_m3} mg/m³"
  puts "OSHA PEL usage:             #{result.osha_pel_percent}%"
  puts "Annual VOC load:            #{result.annual_voc_load_kg} kg/year"
end
