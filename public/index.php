<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Healthcare VOC Compliance Calculator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fafaf8; color: #141414; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem 1rem; }
        h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .subtitle { color: #7a7168; margin-bottom: 2rem; }
        form { background: #fff; border: 1px solid #d4d0c8; border-radius: 8px; padding: 1.5rem; }
        label { display: block; font-weight: 600; margin-top: 1rem; font-size: 0.9rem; }
        input, select { width: 100%; padding: 0.5rem; border: 1px solid #d4d0c8; border-radius: 4px; font-size: 1rem; margin-top: 0.25rem; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        button { margin-top: 1.5rem; background: #E87A2D; color: #fff; border: none; padding: 0.75rem 2rem; border-radius: 4px; font-size: 1rem; cursor: pointer; }
        button:hover { background: #D06A22; }
        #results { margin-top: 2rem; background: #fff; border: 1px solid #d4d0c8; border-radius: 8px; padding: 1.5rem; display: none; }
        #results h2 { font-size: 1.2rem; margin-bottom: 1rem; color: #D06A22; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #f0ede8; }
        td:first-child { color: #7a7168; }
        td:last-child { font-weight: 600; text-align: right; }
        .warning { color: #b91c1c; font-size: 0.9rem; margin-top: 0.5rem; }
        footer { margin-top: 3rem; text-align: center; color: #7a7168; font-size: 0.85rem; }
        footer a { color: #E87A2D; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Healthcare VOC Compliance Calculator</h1>
        <p class="subtitle">Calculate VOC exposure and regulatory compliance for healthcare facility cleaning products.</p>

        <form id="vocForm">
            <div class="row">
                <div>
                    <label for="room_sqft">Room Area (sqft)</label>
                    <input type="number" id="room_sqft" value="200" min="1" step="1">
                </div>
                <div>
                    <label for="ceiling_ft">Ceiling Height (ft)</label>
                    <input type="number" id="ceiling_ft" value="9" min="1" step="0.5">
                </div>
            </div>
            <div class="row">
                <div>
                    <label for="product_voc">Product VOC (g/L concentrate)</label>
                    <input type="number" id="product_voc" value="8" min="0" step="0.1">
                </div>
                <div>
                    <label for="dilution">Dilution Ratio</label>
                    <select id="dilution">
                        <option value="1">RTU (undiluted)</option>
                        <option value="0.0588">1:16</option>
                        <option value="0.0303">1:32</option>
                        <option value="0.015625" selected>1:64</option>
                        <option value="0.0078">1:128</option>
                        <option value="0.0039">1:256</option>
                    </select>
                </div>
            </div>
            <div class="row">
                <div>
                    <label for="coverage">Coverage (sqft/L)</label>
                    <input type="number" id="coverage" value="400" min="1" step="10">
                </div>
                <div>
                    <label for="ach">Air Changes/Hour (ACH)</label>
                    <input type="number" id="ach" value="6" min="0" step="0.5">
                </div>
            </div>
            <div class="row">
                <div>
                    <label for="freq">Cleaning Frequency (per year)</label>
                    <input type="number" id="freq" value="365" min="1" step="1">
                </div>
                <div>
                    <label for="space_type">Space Type</label>
                    <select id="space_type">
                        <option value="patient_room">Patient Room (6 ACH min)</option>
                        <option value="icu">ICU (12 ACH min)</option>
                        <option value="operating_room">Operating Room (20 ACH min)</option>
                        <option value="exam_room">Exam Room (6 ACH min)</option>
                        <option value="corridor">Corridor (4 ACH min)</option>
                        <option value="dietary_kitchen">Dietary Kitchen (10 ACH min)</option>
                        <option value="bathroom">Bathroom (10 ACH min)</option>
                        <option value="janitor_closet">Janitor Closet (10 ACH min)</option>
                    </select>
                </div>
            </div>
            <button type="submit">Calculate</button>
        </form>

        <div id="results">
            <h2>Results</h2>
            <table id="resultsTable"></table>
            <div id="warnings"></div>
        </div>

        <footer>
            <p>Open-source tool by Dave Cook — <a href="https://www.binx.ca/commercial.php">Binx Professional Cleaning</a></p>
            <p>Source: <a href="https://github.com/DaveCookVectorLabs/healthcare-voc-compliance">GitHub</a></p>
        </footer>
    </div>

    <script>
    document.getElementById('vocForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const SQFT_TO_SQM = 0.09290304;
        const FT_TO_M = 0.3048;
        const OSHA_PEL = 300.0;

        const sqft = parseFloat(document.getElementById('room_sqft').value);
        const ceilFt = parseFloat(document.getElementById('ceiling_ft').value);
        const voc = parseFloat(document.getElementById('product_voc').value);
        const dilution = parseFloat(document.getElementById('dilution').value);
        const coverage = parseFloat(document.getElementById('coverage').value);
        const ach = parseFloat(document.getElementById('ach').value);
        const freq = parseInt(document.getElementById('freq').value);

        const vol = sqft * SQFT_TO_SQM * ceilFt * FT_TO_M;
        const effVoc = voc * dilution;
        const applied = sqft / coverage;
        const totalMg = effVoc * applied * 1000;
        const emission = totalMg / 0.5;
        const vent = ach * vol;
        const ss = vent > 0 ? emission / vent : totalMg / vol;
        const pelPct = (ss / OSHA_PEL) * 100;

        const target = OSHA_PEL * 0.1;
        let reentry = 0;
        if (ss > target && ach > 0) reentry = Math.log(ss / target) / ach * 60;
        else if (ss > target) reentry = -1;

        const annualKg = (effVoc * applied * freq) / 1000;

        const rows = [
            ['Room volume', vol.toFixed(1) + ' m³'],
            ['Effective VOC (diluted)', effVoc.toFixed(4) + ' g/L'],
            ['Product applied', applied.toFixed(3) + ' L'],
            ['Total VOC released', totalMg.toFixed(1) + ' mg'],
            ['Steady-state concentration', ss.toFixed(2) + ' mg/m³'],
            ['OSHA PEL usage', pelPct.toFixed(2) + '%'],
            ['Time to safe reentry', reentry >= 0 ? reentry.toFixed(1) + ' min' : 'N/A'],
            ['Annual VOC load', annualKg.toFixed(4) + ' kg/year'],
        ];

        const table = document.getElementById('resultsTable');
        table.innerHTML = rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('');

        const warnings = [];
        if (pelPct > 100) warnings.push('CRITICAL: Steady-state VOC exceeds OSHA PEL');
        else if (pelPct > 50) warnings.push('Steady-state VOC exceeds 50% of OSHA PEL');
        if (ach === 0) warnings.push('Zero ventilation — VOC will accumulate');

        document.getElementById('warnings').innerHTML = warnings.map(w => `<p class="warning">⚠ ${w}</p>`).join('');
        document.getElementById('results').style.display = 'block';
    });
    </script>
</body>
</html>
