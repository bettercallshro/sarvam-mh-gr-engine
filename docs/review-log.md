# Review log

The human checks and decisions behind this repo, dated, with the commit or file each one refers to.

| Date | Refers to | What was checked or decided |
|---|---|---|
| 17–18 Nov 2026 | `scripts/fetch_corpus.sh`, Orgpedia commit `c96e88f` | Corpus chosen: 112 Maharashtra IT-department GRs, 2018–2024. Sample texts checked against the official PDFs before building on them. |
| 18 Nov 2026 | `eval/questions.jsonl` (`df10934`) | 37 questions and answer keys approved. Key facts checked on the official PDFs; one key error found (Q5: it was the rates for ongoing cloud services that ended in June 2021, not the empanelment) and fixed before any run. |
| 18 Nov 2026 | `520f66c` | Decided to score the raw model answer and log the product's corrections separately, so the checks can't hide the model's errors. |
| 18 Nov 2026 | `835367c`, `f102906` | After the baseline run: diagnosed the worst failures (Q2, Q18, Q28) before changing anything. Cause: the amending GR was in the prompt but shown as a one-line pointer. |
| 18 Nov 2026 | `213c181`, `e8e3e09`, `32ae38d` | Round 1 fixed its target but left one right answer blank; decided on a second round (never blank, current rule first) rather than shipping round 1. |
| 20 Nov 2026 | `eval/scores.csv` | Every scored answer (baseline, final runs A and B) scored against the rubric and confirmed row by row. Rubric kept as written before the runs; one edge case recorded (Q20: right answer, invented source). |
| 20 Nov 2026 | `49ee4ae` | Decided to stop fixing after two rounds: more fixes on the same 37 questions would tune to the test. |
| 20 Nov 2026 | `eval/holdout_questions.jsonl` | 15 new questions written, answers checked against the corpus text, and locked before any run. Compared the baseline with the final version only, with no changes before or after. |
| 20 Nov 2026 | `a0b6502`, `eval/scores.csv` | Hold-out answers scored and confirmed row by row; one edge case recorded (Q109: right answer, wrong first line). Reported as it came: a tie on new questions. |
| 20 Nov 2026 | `runs/partial/` | Two incomplete runs kept, not deleted; both were rerun in full. |
| 21 Nov 2026 | `e6da3ab`, `fce666b`, `2bd5f0f`, `eval/scores.csv` | Baseline run a second time at the same engine version, so every version and question set has two runs. Reported as it came; scored and confirmed row by row (26 of 37 fully correct, 1 confident-wrong). Decided to stop there: no further runs or fixes. |
| 22 Nov 2026 | `eval/scores.csv` (hold-out rows) | Second look at the hold-out: confident-wrong rose from 1, 3 (baseline) to 3, 3 (final). On Q103 and Q113 the baseline said it couldn't find a GR and the final version answered, wrong in at least one run: likely a side effect of the instruction to answer first. Not separable by fix, as round 1 wasn't run on the hold-out. No new runs. |
| 22 Nov 2026 | `eval/holdout_questions.jsonl` | Answer keys for the four failing hold-out questions (Q103, Q105, Q107, Q113) checked against the official PDFs. Three confirmed. Q105's key gives 1 April 2023; the 23-02-2023 circular also starts implementation in all departments on 1 March 2023. Key left as written; no score changes, since no answer gave either 2023 date. |
