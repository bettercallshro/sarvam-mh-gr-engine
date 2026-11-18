# sarvam-mh-gr-engine

An engine that answers questions about Maharashtra Information Technology department
Government Resolutions (GRs), 2018 to 2024, with citations. It handles two kinds of question:

1. "Is this GR still in force?"
2. "What is the latest GR on a topic, and what changed?"

Every answer cites the GR it rests on (date, number, official PDF link) and flags any newer
GR in the corpus that amends, replaces or stays it. When the evidence is thin, it says it
couldn't find a GR on this in the corpus. It is scored on a fixed set of 37 questions
(`eval/questions.jsonl`).

Independent case study, not affiliated with Sarvam.

## Status

| Step | What | State |
|---|---|---|
| E1 | Corpus, index, twin detection, citation graph | done |
| E2 | Retrieval and retrieval check on the 37 questions | not started |
| E3–E6 | Answer step (`sarvam-105b`), logging, key handling, smoke test | not started |
| F1 | Baseline run of all 37 | not started |

## How to run

Requires Python 3.10+ and git. E1 uses only the standard library.

```bash
./scripts/fetch_corpus.sh          # sparse clone of the IT-department GRs into data/mahGRs
python -m grengine.build_index     # writes data/index/ and prints a report
python -m unittest discover -s tests
```

## Layout

```
grengine/
  normalize.py     Devanagari digits to ASCII, whitespace, OCR spacing in numbers
  dates.py         dates in English and Marathi text, as dd-mm-yyyy
  orders.py        GR numbers reduced to a (file, case) key across scripts and OCR forms
  corpus.py        load GRs.json and the per-GR text files, split pages
  twins.py         English/Marathi copies of one GR (different codes)
  citations.py     citation graph and newer-GR candidates
  build_index.py   E1 entry point
scripts/fetch_corpus.sh
eval/questions.jsonl
tests/
```

## How the corpus is handled

- **Dates** come from the `date` field in `GRs.json`, never from the code (the code is an
  upload timestamp).
- **Digits.** Marathi text writes numbers as ०–९. Matching runs on an ASCII-digit copy.
  Quotes always come from the original text.
- **Twins.** Some GRs were issued as an English and a Marathi PDF with different codes.
  They count as one GR when deciding which GR is latest. A pair is a twin when it has the
  same date, a different original language, the same GR number, and English-version text
  cosine similarity ≥ 0.8.
- **Citation graph.** Each GR is linked to the earlier corpus GRs it cites, matched by
  date and by GR number. A reference reads "No. X, dated D", so the number just before a
  date decides which GR the date points to. A cited date with a different number is kept
  as an *unresolved* reference: a GR the corpus doesn't hold. It is never treated as one
  that doesn't exist. An edge means "cites". Whether the later GR changes the earlier one
  has to be read from its text. Edge evidence, strongest first: `date+order`, `order`,
  `date`, `same_file` (only the shared file number in the header).
- **`order_type`** in the metadata is sometimes wrong, so nothing depends on it.

## Corpus credit

The GR texts and metadata come from [orgpedia/mahGRs](https://github.com/orgpedia/mahGRs)
by the Orgpedia Foundation, used under the MIT licence. Their licence notice is kept in
[`LICENSES/mahGRs-LICENSE.txt`](LICENSES/mahGRs-LICENSE.txt). Only
`GRs/Information_Technology_Department/` is used, pinned to commit `c96e88f` in
`scripts/fetch_corpus.sh`. The corpus is fetched, not copied into this repository.
