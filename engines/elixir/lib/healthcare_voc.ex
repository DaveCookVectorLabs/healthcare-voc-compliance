defmodule HealthcareVoc do
  @moduledoc """
  Healthcare VOC Compliance Calculator — Elixir Engine

  Calculates VOC exposure concentration per cleaning cycle based on product
  VOC content, dilution ratio, coverage rate, room geometry, and ventilation.

  Reference:
  - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
  - ASHRAE 62.1-2022 (healthcare ventilation rates)
  - EPA 40 CFR Part 59 Subpart C
  - Canada SOR/2021-268
  """

  @osha_tvoc_pel 300.0
  @sqft_to_sqm 0.09290304
  @ft_to_m 0.3048

  @ashrae_healthcare_ach %{
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
    "general_office" => 4
  }

  @doc """
  Calculate VOC exposure for a single healthcare cleaning cycle.

  ## Parameters
  - `room_sqft` - Room floor area in square feet
  - `ceiling_height_ft` - Ceiling height in feet
  - `product_voc_g_per_l` - Product VOC content (concentrate) in g/L
  - `dilution_ratio` - Concentrate fraction (1.0 = RTU, 0.015625 = 1:64)
  - `coverage_sqft_per_l` - Coverage area per litre of applied solution
  - `air_changes_per_hour` - Ventilation rate (ACH)
  - `cleaning_frequency_per_year` - Number of cleaning cycles per year
  - `space_type` - Healthcare space type for ASHRAE reference

  ## Returns
  Map with calculation results and compliance data.
  """
  def calculate(opts \\ []) do
    room_sqft = Keyword.get(opts, :room_sqft, 200.0)
    ceiling_height_ft = Keyword.get(opts, :ceiling_height_ft, 9.0)
    product_voc = Keyword.get(opts, :product_voc_g_per_l, 8.0)
    dilution_ratio = Keyword.get(opts, :dilution_ratio, 1.0)
    coverage = Keyword.get(opts, :coverage_sqft_per_l, 400.0)
    ach = Keyword.get(opts, :air_changes_per_hour, 6.0)
    freq = Keyword.get(opts, :cleaning_frequency_per_year, 365)
    space_type = Keyword.get(opts, :space_type, "patient_room")

    room_sqm = room_sqft * @sqft_to_sqm
    ceiling_m = ceiling_height_ft * @ft_to_m
    room_volume = room_sqm * ceiling_m

    effective_voc = product_voc * dilution_ratio
    product_applied = room_sqft / coverage
    total_voc_g = effective_voc * product_applied
    total_voc_mg = total_voc_g * 1000.0

    initial_conc = total_voc_mg / room_volume

    cleaning_duration_hr = 0.5
    emission_rate = total_voc_mg / cleaning_duration_hr
    vent_rate = ach * room_volume

    {steady_state, warnings} =
      if vent_rate > 0 do
        {emission_rate / vent_rate, []}
      else
        {initial_conc, ["Zero ventilation — VOC will accumulate"]}
      end

    osha_pct = steady_state / @osha_tvoc_pel * 100.0

    target = @osha_tvoc_pel * 0.10
    reentry =
      cond do
        steady_state <= target -> 0.0
        ach > 0 -> :math.log(steady_state / target) / ach * 60.0
        true -> -1.0
      end

    annual_g = total_voc_g * freq

    ashrae_min = Map.get(@ashrae_healthcare_ach, space_type, 4)
    warnings =
      if ach < ashrae_min do
        warnings ++ ["Ventilation (#{ach} ACH) below ASHRAE minimum for #{space_type} (#{ashrae_min} ACH)"]
      else
        warnings
      end

    warnings =
      cond do
        osha_pct > 100.0 -> warnings ++ ["CRITICAL: Steady-state VOC exceeds OSHA PEL"]
        osha_pct > 50.0 -> warnings ++ ["Steady-state VOC exceeds 50% of OSHA PEL"]
        true -> warnings
      end

    %{
      room_volume_m3: Float.round(room_volume, 2),
      product_voc_g_per_l: product_voc,
      effective_voc_g_per_l: Float.round(effective_voc, 4),
      product_applied_l: Float.round(product_applied, 4),
      total_voc_released_g: Float.round(total_voc_g, 4),
      total_voc_released_mg: Float.round(total_voc_mg, 2),
      initial_concentration_mg_per_m3: Float.round(initial_conc, 2),
      steady_state_concentration_mg_per_m3: Float.round(steady_state, 2),
      osha_pel_percent: Float.round(osha_pct, 2),
      time_to_safe_reentry_minutes: Float.round(reentry, 1),
      annual_voc_load_g: Float.round(annual_g, 2),
      annual_voc_load_kg: Float.round(annual_g / 1000.0, 4),
      air_changes_per_hour: ach,
      warnings: warnings
    }
  end
end
