# Manual baseline and system comparison
Baseline: emails to suppliers, spreadsheet quotation arithmetic and manual approval tracking. This describes the comparison method; it is not a claim that users were observed.

The benchmark dataset has 3 identical-specification laptop offers, quantity 2, 18% tax and no discount. Expected totals are independently prepared arithmetic: 51500×2×1.18=121540; 54000×2×1.18=127440; 72000×2×1.18=169920. The script checks the API output against those values and records response timings on the local test harness.

Run from `backend`: `python ../scripts/run_baseline_benchmark.py`. Output defaults to `docs/evidence/baseline-benchmark.json`. Supply `--manual-seconds` and `--system-seconds` only after actually timing the identical human workflow.

| Metric | Manual email/spreadsheet | System evidence |
|---|---|---|
| Arithmetic accuracy | Calculate three totals; count correct/3 | Deterministic API totals vs reference |
| Comparison preparation time | Stopwatch from opening offers to completed matrix | Stopwatch same task in UI; API latency separately |
| Approval traceability | Count identifiable decisions and timestamps in emails | DB approval + audit events |
| Document integrity | Note available mechanism; don't assume none in every process | SHA-256 at upload + verified download |
| Unusual-price visibility | Ask participant to identify outlier/reason | Persisted median/IQR/percentage explanation |
| Vendor-risk visibility | Record factors actually considered | Five measured rates and weighted contributions |
| Unauthorized action prevention | Describe actual process safeguards | Defined security tests |
| End-to-end cycle time | Time comparable steps, excluding vendor waiting equally | Time same sequence with separate roles |

**Manual timing and cycle-time reduction remain unmeasured.** API response time is not human task time and must not be presented as a time-saving percentage. Formula once collected: (manual_seconds - system_seconds) / manual_seconds × 100. Use at least three comparable runs, report median/range, note learning effects and warm/cold conditions. Never count upload/auth network time on only one side.
