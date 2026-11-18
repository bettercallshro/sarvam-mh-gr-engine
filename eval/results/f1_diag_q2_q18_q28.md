# F1 diagnosis: Q2, Q18, Q28 (was the amending GR in the model's context?)

Source: `runs/2026-11-18-baseline.jsonl`. No model calls were made for this diagnosis.

## Short answer

Yes, in all three. The amending GR was **retrieved** (rank 3, 2, 2) with its full text in
the prompt, and it was **listed as a newer-GR candidate of the asked-for GR**. Because its
text was already above, the candidate line said only "Its text is above among the
retrieved GRs." The model **said nothing about it**: it is absent from
`candidates_reviewed`, `newer`, `cited` and `answer`. In each case the model answered from
the original GR alone. The check flagged it each time ("candidates of the asked-for GR not
reviewed").

## Per question

### Q2: What is the deadline for moving existing department applications to the cloud?

Gold: 31-03-2020, set by the 19-06-2019 addendum (the original said 30-10-2018).

| | |
|---|---|
| Amending GR | 19-06-2019 `201906191741481211` |
| Retrieved | Yes, **rank 3**, full text in the prompt |
| Given as candidate | Yes, of the asked-for GR 29-01-2018. Evidence `same_file` (candidate only): "- 201906191741481211 (19-06-2019) cites 201801291824268911 [29-01-2018]; evidence: same_file; hops: 1. Only a shared file number links them; this alone proves nothing. Its text is above among the retrieved GRs." |
| asked_for_code | 201801291824268911 (29-01-2018) |
| What the model said about it | **Nothing.** It reviewed 5 candidates (23-04-2021, 08-03-2019, 04-08-2018, 19-05-2018, 16-10-2018), all `cites_only`. All five are candidates whose text appeared in the candidates section. |
| Answer (raw) | "According to GR 201801291824268911 dated 29-01-2018, existing applications ... must be migrated to cloud on or before 30.10.2018 ..." |
| Flags | candidates not reviewed: 04-08-2018, 16-05-2018, **05-07-2019, 19-06-2019**; date 30-10-2018 matches no cited GR (it occurs in the texts) |

Also, one `candidates_reviewed` item is malformed: an extra nested object keyed by a code.
It passed validation, because only the required keys are checked.

### Q18: Whose concurrence is needed for a consultant's scope of work?

Gold: the department's ACS/PS/Secretary, not DIT (corrigendum 19-03-2021).

| | |
|---|---|
| Amending GR | 19-03-2021 `202103191753279311` |
| Retrieved | Yes, **rank 2**, full text in the prompt |
| Given as candidate | Yes, of the asked-for GR 20-03-2018. Evidence **`date+order`** (the strongest): "- 202103191753279311 (19-03-2021) cites 201803201319308011 [20-03-2018]; evidence: date+order, same_file; hops: 1. Its text is above among the retrieved GRs." |
| asked_for_code | 201803201319308011 (20-03-2018) |
| What the model said about it | **Nothing.** It reviewed 4 candidates (24-04-2023, 05-03-2024, 15-12-2023, 27-10-2023), all `unrelated`. All four had their text in the candidates section. |
| Answer (raw) | "According to the Government Resolution dated 20-03-2018, departments need to finalize the scope of work for consultancy with the concurrence of DIT." This is the superseded rule, stated as current. |
| Flags | candidates not reviewed: 05-10-2023, **19-03-2021** |

### Q28: Which groups does the Maha-Pariksha GR of 20 February 2020 apply to?

Gold: Group C and Group D (the corrigendum of 24-02-2020 corrected "Group B and C").

| | |
|---|---|
| Amending GR | 24-02-2020 `202002241155355511` |
| Retrieved | Yes, **rank 2**, full text in the prompt |
| Given as candidate | Yes, of the asked-for GR 20-02-2020. Evidence **`date+order`**: "- 202002241155355511 (24-02-2020) cites 202002201713214911 [20-02-2020]; evidence: date+order, same_file; hops: 1. Its text is above among the retrieved GRs." |
| asked_for_code | 202002201713214911 (20-02-2020) |
| What the model said about it | **Nothing.** It reviewed 2 candidates (21-01-2021, 04-03-2021), both `cites_only`. Both had their text in the candidates section. |
| Answer (raw) | "... applies to Group-B and Group-C category recruitment examinations ... No newer GR in the corpus amends, replaces, stays, extends or clarifies this GR." This is the uncorrected preamble, and it wrongly says no newer GR exists. |
| Flags | candidates not reviewed: **24-02-2020** |

## Across all 37

Of the 74 candidates of the asked-for GR (across questions where the model named one):

| Where the candidate's text was | Reviewed | Not reviewed |
|---|---|---|
| In the candidates section (new text) | 34 | 4 |
| Only above, among the retrieved GRs ("Its text is above") | 22 | **14** |

Unreviewed already-retrieved candidates that are gold GRs: **Q2 (19-06-2019), Q15
(05-10-2023), Q18 (19-03-2021), Q28 (24-02-2020)**.

## Reading

The failure is in how the context is laid out, not in retrieval or the graph. When an
amending GR is also a top-5 search result, the candidates section gives it only a one-line
pointer, and the model tends to skip it. It reviews only the candidates whose text sits in
the candidates section. Here this hit the strongest-evidence amendments (`date+order` in
Q18 and Q28). No fix has been applied yet.
