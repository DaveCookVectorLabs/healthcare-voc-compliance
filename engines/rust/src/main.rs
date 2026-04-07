use std::collections::HashMap;
use std::io::{BufRead, BufReader};
use std::net::TcpListener;
use std::fs::File;
use std::path::PathBuf;

/// Healthcare VOC Compliance Calculator — Rust Engine
///
/// Calculates VOC exposure concentration per cleaning cycle.
/// Exposes /calculate (POST) and /health (GET) endpoints.
///
/// Reference:
/// - OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
/// - ASHRAE 62.1-2022 (healthcare ventilation rates)

const OSHA_TVOC_PEL: f64 = 300.0;
const SQFT_TO_SQM: f64 = 0.09290304;
const FT_TO_M: f64 = 0.3048;
const VERSION: &str = "0.1.0";

#[derive(Debug)]
struct CalculateRequest {
    room_sqft: f64,
    ceiling_height_ft: f64,
    product_voc_g_per_l: f64,
    dilution_ratio: f64,
    coverage_sqft_per_l: f64,
    air_changes_per_hour: f64,
    cleaning_frequency_per_year: u32,
    product_category: String,
}

#[derive(Debug)]
struct CalculateResult {
    room_volume_m3: f64,
    product_voc_g_per_l: f64,
    effective_voc_g_per_l: f64,
    product_applied_l: f64,
    total_voc_released_g: f64,
    total_voc_released_mg: f64,
    initial_concentration_mg_per_m3: f64,
    steady_state_concentration_mg_per_m3: f64,
    osha_pel_percent: f64,
    time_to_safe_reentry_minutes: f64,
    annual_voc_load_g: f64,
    annual_voc_load_kg: f64,
    air_changes_per_hour: f64,
    compliant_count: usize,
    non_compliant_count: usize,
    warnings: Vec<String>,
}

fn calculate(req: &CalculateRequest, limits: &HashMap<(String, String), f64>) -> CalculateResult {
    let room_sqm = req.room_sqft * SQFT_TO_SQM;
    let ceiling_m = req.ceiling_height_ft * FT_TO_M;
    let room_volume_m3 = room_sqm * ceiling_m;

    let effective_voc = req.product_voc_g_per_l * req.dilution_ratio;
    let product_applied_l = req.room_sqft / req.coverage_sqft_per_l;
    let total_voc_g = effective_voc * product_applied_l;
    let total_voc_mg = total_voc_g * 1000.0;

    let initial_conc = total_voc_mg / room_volume_m3;

    let cleaning_duration_hr = 0.5;
    let emission_rate = total_voc_mg / cleaning_duration_hr;
    let vent_rate = req.air_changes_per_hour * room_volume_m3;

    let mut warnings = Vec::new();

    let steady_state = if vent_rate > 0.0 {
        emission_rate / vent_rate
    } else {
        warnings.push("Zero ventilation — VOC will accumulate".to_string());
        initial_conc
    };

    let osha_pct = (steady_state / OSHA_TVOC_PEL) * 100.0;

    let target = OSHA_TVOC_PEL * 0.10;
    let reentry = if steady_state <= target {
        0.0
    } else if req.air_changes_per_hour > 0.0 {
        let ratio = steady_state / target;
        (ratio.ln() / req.air_changes_per_hour) * 60.0
    } else {
        -1.0
    };

    let annual_g = total_voc_g * req.cleaning_frequency_per_year as f64;

    let mut compliant = 0usize;
    let mut non_compliant = 0usize;
    for ((_, cat), limit) in limits.iter() {
        if cat == &req.product_category {
            if req.product_voc_g_per_l <= *limit {
                compliant += 1;
            } else {
                non_compliant += 1;
            }
        }
    }

    if osha_pct > 50.0 {
        warnings.push("Steady-state VOC exceeds 50% of OSHA PEL".to_string());
    }

    CalculateResult {
        room_volume_m3: (room_volume_m3 * 100.0).round() / 100.0,
        product_voc_g_per_l: req.product_voc_g_per_l,
        effective_voc_g_per_l: (effective_voc * 10000.0).round() / 10000.0,
        product_applied_l: (product_applied_l * 10000.0).round() / 10000.0,
        total_voc_released_g: (total_voc_g * 10000.0).round() / 10000.0,
        total_voc_released_mg: (total_voc_mg * 100.0).round() / 100.0,
        initial_concentration_mg_per_m3: (initial_conc * 100.0).round() / 100.0,
        steady_state_concentration_mg_per_m3: (steady_state * 100.0).round() / 100.0,
        osha_pel_percent: (osha_pct * 100.0).round() / 100.0,
        time_to_safe_reentry_minutes: (reentry * 10.0).round() / 10.0,
        annual_voc_load_g: (annual_g * 100.0).round() / 100.0,
        annual_voc_load_kg: (annual_g / 1000.0 * 10000.0).round() / 10000.0,
        air_changes_per_hour: req.air_changes_per_hour,
        compliant_count: compliant,
        non_compliant_count: non_compliant,
        warnings,
    }
}

fn result_to_json(r: &CalculateResult) -> String {
    let warnings_json: Vec<String> = r.warnings.iter().map(|w| format!("\"{}\"", w)).collect();
    format!(
        r#"{{"room_volume_m3":{},"product_voc_g_per_L":{},"effective_voc_g_per_L":{},"product_applied_L":{},"total_voc_released_g":{},"total_voc_released_mg":{},"initial_concentration_mg_per_m3":{},"steady_state_concentration_mg_per_m3":{},"osha_pel_percent":{},"time_to_safe_reentry_minutes":{},"annual_voc_load_g":{},"annual_voc_load_kg":{},"air_changes_per_hour":{},"compliant_jurisdiction_count":{},"non_compliant_jurisdiction_count":{},"warnings":[{}]}}"#,
        r.room_volume_m3, r.product_voc_g_per_l, r.effective_voc_g_per_l,
        r.product_applied_l, r.total_voc_released_g, r.total_voc_released_mg,
        r.initial_concentration_mg_per_m3, r.steady_state_concentration_mg_per_m3,
        r.osha_pel_percent, r.time_to_safe_reentry_minutes,
        r.annual_voc_load_g, r.annual_voc_load_kg, r.air_changes_per_hour,
        r.compliant_count, r.non_compliant_count, warnings_json.join(",")
    )
}

fn load_limits(datasets_dir: &PathBuf) -> HashMap<(String, String), f64> {
    let mut limits = HashMap::new();
    let csv_path = datasets_dir.join("voc_regulatory_limits.csv");
    if let Ok(file) = File::open(&csv_path) {
        let reader = BufReader::new(file);
        let mut lines = reader.lines();
        let _header = lines.next(); // skip header
        for line in lines {
            if let Ok(line) = line {
                let fields: Vec<&str> = line.split(',').collect();
                if fields.len() >= 8 {
                    let jcode = fields[2].to_string();
                    let category = fields[6].to_string();
                    if let Ok(limit) = fields[7].parse::<f64>() {
                        limits.insert((jcode, category), limit);
                    }
                }
            }
        }
    }
    limits
}

fn main() {
    let port: u16 = std::env::args()
        .position(|a| a == "--port")
        .and_then(|i| std::env::args().nth(i + 1))
        .and_then(|p| p.parse().ok())
        .unwrap_or(8001);

    let exe_path = std::env::current_exe().unwrap_or_default();
    let datasets_dir = exe_path
        .parent().unwrap()
        .parent().unwrap()
        .parent().unwrap()
        .parent().unwrap()
        .join("datasets");

    let limits = load_limits(&datasets_dir);
    println!("Loaded {} regulatory limits", limits.len());

    let listener = TcpListener::bind(format!("0.0.0.0:{}", port)).expect("Failed to bind");
    println!("Healthcare VOC Calculator (Rust) listening on port {}", port);

    for stream in listener.incoming() {
        if let Ok(mut stream) = stream {
            use std::io::{Read, Write};
            let mut buf = [0u8; 4096];
            let n = stream.read(&mut buf).unwrap_or(0);
            let request = String::from_utf8_lossy(&buf[..n]).to_string();

            if request.starts_with("GET /health") {
                let body = format!(
                    r#"{{"status":"ok","engine":"rust","version":"{}","regulatory_limits_loaded":{}}}"#,
                    VERSION, limits.len()
                );
                let response = format!(
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
                    body.len(), body
                );
                let _ = stream.write_all(response.as_bytes());
            } else if request.starts_with("POST /calculate") {
                // Extract JSON body
                let body_start = request.find("\r\n\r\n").unwrap_or(n) + 4;
                let json_body = &request[body_start..];

                // Minimal JSON parsing
                let get_f64 = |key: &str| -> f64 {
                    json_body.find(&format!("\"{}\"", key))
                        .and_then(|i| {
                            let after = &json_body[i + key.len() + 3..];
                            let end = after.find(|c: char| c != '.' && c != '-' && !c.is_ascii_digit()).unwrap_or(after.len());
                            after[..end].parse().ok()
                        })
                        .unwrap_or(0.0)
                };

                let req = CalculateRequest {
                    room_sqft: get_f64("room_sqft"),
                    ceiling_height_ft: if get_f64("ceiling_height_ft") > 0.0 { get_f64("ceiling_height_ft") } else { 9.0 },
                    product_voc_g_per_l: get_f64("product_voc_g_per_L"),
                    dilution_ratio: if get_f64("dilution_ratio") > 0.0 { get_f64("dilution_ratio") } else { 1.0 },
                    coverage_sqft_per_l: if get_f64("coverage_sqft_per_L") > 0.0 { get_f64("coverage_sqft_per_L") } else { 400.0 },
                    air_changes_per_hour: if get_f64("air_changes_per_hour") > 0.0 { get_f64("air_changes_per_hour") } else { 6.0 },
                    cleaning_frequency_per_year: get_f64("cleaning_frequency_per_year") as u32,
                    product_category: "General Purpose Cleaner".to_string(),
                };

                let result = calculate(&req, &limits);
                let body = result_to_json(&result);
                let response = format!(
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
                    body.len(), body
                );
                let _ = stream.write_all(response.as_bytes());
            } else {
                let response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n";
                let _ = stream.write_all(response.as_bytes());
            }
        }
    }
}
