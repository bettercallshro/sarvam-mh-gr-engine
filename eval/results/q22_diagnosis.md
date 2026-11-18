# Q22: why the answer says "couldn't find"

**Question:** "Did the 30 November 2018 Fintech corrigendum change any benefit?"

**Gold:** No. It only corrects "United payments Interface" to "Unified payment Interface".
The gold GR is `201811301240117211`.

## Was the corrigendum in the context?

Yes, in all three runs (F1, round 1 run 1, round 1 run 2):

| | |
|---|---|
| Retrieval | Rank **1** (text score 1.0, plus an exact date match). Rank 2 was the same-day Fintech addendum `201811301239595811`. |
| Date facts | "30-11-2018: corpus GR(s) with this date: 201811301239595811 …; 201811301240117211 …" |
| Text given | Full text, first block of the prompt. It is short and explicit: *"Government Corrigendum … In the Government Resolution No. DIT-2018/C.R-17/D-1/39 dated 16th February 2018 in paragraph 2 in line no 3 for the words "United payments Interface (UPI)" read the words "Unified payment Interface (UPI)"."* |
| Candidates | None: no corpus GR cites the corrigendum |

## What the model said

| Run | asked_for_code | status | answer |
|---|---|---|---|
| F1 | 201811301240117211 | answered | "The corpus does not contain any newer GR that amends … the 30 November 2018 corrigendum … No newer GR found in this corpus." (It answers a different question: whether the corrigendum was itself changed.) |
| Round 1 run 1 | null | not_found | "I couldn't find a GR on this in the corpus." |
| Round 1 run 2 | 201811301240117211 | not_found | "I couldn't find a GR on this in the corpus." |

## Conclusion

This is **not retrieval and not layout**. The right GR was ranked first and its full text was
in the prompt. The model did not tie "the 30 November 2018 Fintech corrigendum" to that text,
and in run 2 it named the right GR and still said it couldn't find it. One possible
contributor is that both 30-11-2018 GRs have the same metadata title and number, and the
title doesn't say "corrigendum"; only the text does.

Per the instruction, no fix was made for Q22. A possible later change is to show the
document type, read from the text's first lines (corrigendum or addendum), in each GR's
header in the prompt. This would be a layout aid, not a retrieval change.
