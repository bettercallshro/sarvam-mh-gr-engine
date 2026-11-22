# sarvam-mh-gr-engine

By Shro ([bettercallshro.com](https://www.bettercallshro.com))

A question-answering engine for Government Resolutions (GRs) of the Maharashtra
Information Technology department, 2018 to 2024. It answers two kinds of question:

1. **Is this GR still in force?**
2. **What is the latest GR on a topic, and what changed?**

The GRs are in Marathi and English. Every answer cites the GR it rests on (date, code,
official PDF link, quote from the original text). It flags any newer GR that amends,
replaces or stays it, and says "I couldn't find a GR on this in the corpus" when the
evidence is thin. Answers are written by Sarvam's `sarvam-105b`; search and indexing run
locally.

Independent case study, not affiliated with Sarvam.

## How to read this repo (10 minutes)

1. [Results](#results): the two tables below.
2. [`eval/scores.csv`](eval/scores.csv): the hand score behind every number, one row per
   question and run.
3. [`eval/results/f1_diag_q2_q18_q28.md`](eval/results/f1_diag_q2_q18_q28.md): how the
   baseline's worst failures were traced before anything was changed.
4. [`eval/results/holdout_before_after.md`](eval/results/holdout_before_after.md): the 15
   new questions, baseline and final side by side.
5. [`docs/review-log.md`](docs/review-log.md): the human checks and decisions, dated.

## Results

Scored on the raw model answer against the rubric below. "Fully correct" means right
answer, right citation, newest change named, and no confident error.

On the website: Round 0 = baseline, Round 1 = round 1, Round 2 = final; runs A and B = runs 1 and 2.

**37 evaluation questions** (`eval/questions.jsonl`)

| Version | Fully correct | Confident-wrong |
|---|---|---|
| Baseline, run 1 | 25 / 37 | 5 |
| Baseline, run 2 | 26 / 37 | 1 |
| Final, run A | 33 / 37 | 0 |
| Final, run B | 31 / 37 | 2 |

**Hold-out: 15 new questions** (`eval/holdout_questions.jsonl`), written and locked after
the fixes, with no changes before or after. Baseline and final versions, two runs each:

| Version | Fully correct (run 1, run 2) | Confident-wrong (run 1, run 2) |
|---|---|---|
| Baseline | 10, 8 | 1, 3 |
| Final | 11, 9 | 3, 3 |

The fixes held where an amending GR cites the one it changes, not where it doesn't.
Confident-wrong rose (1, 3 → 3, 3): on Q103 and Q113 the baseline said it couldn't find a GR and the final version answered, wrong in at least one run.

Per-question scores: [`eval/scores.csv`](eval/scores.csv). Reports for each step:
[`eval/results/`](eval/results/).

## How it works

1. **Search.** BM25 over ~120-word passages of both text files of each GR (original
   language and English version), with titles added. It also looks up a date or GR number
   in the question directly. When a question names a date that no GR in the corpus has,
   search returns the GRs that cite that date. English and Marathi copies of the same GR
   count as one.
2. **Citation graph.** Each GR is linked to the earlier GRs it cites, matched by date and
   by GR number (Marathi and English forms, OCR noise and Devanagari digits normalised).
   Each link records its evidence, strongest first: date and number, number only, date
   only, shared file number. A link means "cites", not "changes". It only proposes
   newer-GR candidates.
3. **Answer step.** `sarvam-105b` gets the full text of the top 5 retrieved GRs and of
   every newer-GR candidate. It must review each candidate from its text (amends, replaces,
   stays, cites only, …), lead with the rule as it stands now, quote the original language
   word for word, and reply in a fixed JSON format. An invalid reply is retried once.
4. **Checks.** Before the product shows an answer, the checks:
   - drop GR codes the model wasn't given, and repair mistyped ones;
   - take dates, titles and links from the metadata;
   - find each quote in the text to set its page;
   - flag wording problems and dates that match nothing.

   Every change is logged against the raw model answer, which is what gets scored.

**Versions** (each run's commit; the results were committed afterwards)

| Version | Run at | Results added | Prompt | What changed |
|---|---|---|---|---|
| Baseline | `2b41877` | `835367c` | answer_v2 | Search, citation graph, full texts in the prompt, JSON mode, checks, one retry for invalid replies. |
| Baseline, run 2 | `835367c` (same engine code as `2b41877`) | `e6da3ab` (run), `2bd5f0f` (scores) | answer_v2 | Nothing: the same version run again on 21-11-2026. |
| Round 1 | `213c181`; run B rerun at `e8e3e09` | `1e28879` | answer_v3 | Every newer-GR candidate gets its own full-text block and must be reviewed; the first sentence answers directly. |
| Final | `767eb54` | `49ee4ae` | answer_v4 | The current rule comes first (checked in code, one retry); a failed reply still gets a shown answer; simpler review format. |

The hold-out ran the baseline at `835367c` (same engine code as `2b41877`) and the final
version at `49ee4ae`.

## Scoring rubric

Each answer is scored on four things:

| Measure | Values |
|---|---|
| Answer | 2 right, 1 partly right, 0 wrong |
| Citation | pass if the right GR is named and no GR is invented |
| Latest | pass if the newest changing GR is named; n/a if there is none |
| Confident-wrong | yes if a wrong answer or an invented source is stated without hedging |

**Fully correct** = answer 2, citation pass, latest pass or n/a, confident-wrong no.
Scored against the rubric and confirmed row by row by the author, on the raw model answer
(before the checks). The checks and decisions behind the scoring are in
[`docs/review-log.md`](docs/review-log.md).

## How to run

Requires Python 3.10+. Standard library only. The corpus ships in `corpus/`.

```bash
python -m grengine.build_index     # builds data/index/ from corpus/ and prints a report
python -m grengine.eval_retrieval  # retrieval check on the 37 questions (no API calls)
python -m unittest discover -s tests
```

Answer step (needs a Sarvam API key in `SARVAM_API_KEY`; `.env` is git-ignored):

```bash
python -m grengine.run --name smoke --ids 1,7,11,30,36
python -m grengine.run --name baseline --csv     # all 37, plus a scoring CSV
```

Guards:
- Spend caps: `DAILY_SPEND_CAP_INR` (default 50) and `RUN_SPEND_CAP_INR` (default 20).
- Rate limit: 30 requests a minute.
- Errors: a 402 (no credits) stops the run; 429 and 5xx are retried with backoff.

A full run of the 37 cost Rs 2 to 7 at Sarvam's introductory pricing.

## Repository layout

```
grengine/          the engine
  corpus.py        load the GRs from corpus/
  normalize.py     Devanagari digits, OCR spacing
  dates.py         dates in English and Marathi text
  orders.py        GR numbers across scripts and OCR forms
  twins.py         English/Marathi copies of one GR
  citations.py     citation graph, newer-GR candidates
  build_index.py   builds data/index/
  search.py        retrieval
  answer.py        answer step and checks
  prompts/         answer prompts (answer_v1 to answer_v4)
  sarvam.py        Sarvam API client, spend and rate guards
  run.py           runs questions, logs, scoring CSV
  eval_retrieval.py, compare_runs.py   evaluation helpers
corpus/            the 112 GRs, copied unchanged from orgpedia/mahGRs
eval/              questions, hold-out questions, hand scores, step reports
runs/              run logs and scoring sheets (see runs/README.md)
replay/            logged runs exported for the website (see replay/README.md)
docs/              review log
scripts/           fetch_corpus.sh (re-fetch the corpus), export_replay.py (rebuild replay/)
tests/
```

Replay data for the website: [`replay/`](replay/) (logged runs, not live answers; see [`replay/README.md`](replay/README.md)).

## Data source and licence

The GR texts and metadata come from [orgpedia/mahGRs](https://github.com/orgpedia/mahGRs)
by the Orgpedia Foundation, used under the MIT licence. The folder
`GRs/Information_Technology_Department/` is copied unchanged into `corpus/` at commit
`c96e88f`; see [`corpus/README.md`](corpus/README.md). Orgpedia's licence notice is in
[`LICENSES/mahGRs-LICENSE.txt`](LICENSES/mahGRs-LICENSE.txt). `scripts/fetch_corpus.sh`
re-fetches the folder.

The code is under the MIT licence: see [`LICENSE`](LICENSE).

## Limits

- Search was tuned while looking at the 37 evaluation questions.
- One person wrote the questions and scored the answers.
- Small samples: 37 questions (two runs per version) and 15 hold-out
  questions (two runs per version). Results vary between runs: 13 of 37 changed between the two baseline runs, 6 of 37 between the two final runs.
- Nearly half of the citation links (53 of 116) rest only on a shared file number. The
  model has to decide from the text whether a linked GR changes anything.
- The corpus covers IT-department GRs from 2018 to 2024 only. A GR missing from it is
  reported as not found, not as non-existent.
