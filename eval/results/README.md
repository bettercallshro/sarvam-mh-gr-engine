# Reports

In the order the work happened. Hand scores for the scored runs are in `../scores.csv`.

1. `e2_retrieval.md` (+ `.json`): retrieval check on the 37 questions, before any model call; a right GR was in the top 5 for all 37.
2. `e3_stopped.md`: the first answer-step call stopped on HTTP 402 (no credits); state of the code at that point.
3. `e3_answer_step.md`: the answer step, how it was set up, and the development calls on Q7.
4. `e4_logging.md`: what each run log records.
5. `e5_guards.md`: key handling, spend caps and rate limit, with live demos that made no paid call.
6. `e6_smoke.md`: smoke test on questions 1, 7, 11, 30 and 36, with the answers in full.
7. `f1_baseline.md`: baseline run of all 37: format, checks and flags.
8. `f1_diag_q2_q18_q28.md`: why the amending GR was missed in Q2, Q18 and Q28 even though it was in the prompt.
9. `v3_before_after.md` (+ `.csv`): round 1 (layout, answer first, plumbing), two runs, against the baseline.
10. `v4_before_after.md` (+ `.csv`): round 2 (never blank, current rule first), two runs, against the baseline and round 1.
11. `q22_diagnosis.md`: why Q22 said "couldn't find" although the corrigendum was retrieved first.
12. `holdout_before_after.md`: 15 new questions, baseline and final versions, two runs each, raw answers side by side.
13. `q6_diagnosis.md`: why final run B said a 2021 GR amended the July 2019 GR.
14. `baseline_run2.md`: run notes for a second run of the baseline on the 37 questions, to measure run-to-run variation.
