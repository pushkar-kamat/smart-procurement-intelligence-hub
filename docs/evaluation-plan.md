# Evaluation dossier and go/no-go gates
All thresholds here are team-defined; the portfolio asks for measurable gates but does not prescribe these numbers.

| Gate | Target | Evidence |
|---|---|---|
| Quote calculations | 100% prepared reference cases correct | benchmark + unit test |
| Defined unauthorized actions | 100% blocked, state unchanged | role/JWT/ownership tests |
| Critical lifecycle audit | all 13 expected action types present | end-to-end assertion |
| Integrity | unchanged document downloads; modified bytes blocked | SHA tests |
| Obvious designed anomaly | injected 72000 flag, ordinary 52000 normal | deterministic test |
| Invalid PO | no PO before approval | test and manual failure demo |
| Local core request | typical response under 2 seconds | local benchmark; deployed timing pending |
| Stakeholder completion | one real-user test reaches CLOSED | acceptance worksheet, pending |

Evaluate new vendors, <3 price observations, identical historical prices (IQR=0), very large amounts, rejected workflow, expired quotations, late/partial delivery, invoice discrepancies and role changes. Don't generalize synthetic accuracy to real supplier fraud detection.

Record configuration, data version synthetic-v1, test/build versions, commit, run date, hardware and deployment cold/warm state. Benchmark output covers only local harness. Review false positives from tight IQR ranges, mixed specifications/units and future drift. Human override is the normal decision path; anomaly/risk never independently approve or reject.

Remaining primary evidence: actual stakeholder interviews, manual baseline timings, hosted Postgres/Supabase/container results, deployed logs, peer review, video and individual work logs.
