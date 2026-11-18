# Before/after across runs

Automatic measures only; they are proxies, not the hand scores. "Raw" is the model's own output; "checked" is after the product checks (repairs, drops, metadata).

| Run | Log | Prompt |
|---|---|---|
| F1 | `runs/2026-11-18-baseline.jsonl` | answer_v2 |
| r1a | `runs/2026-11-18-v3-run1.jsonl` | answer_v3 |
| r1b | `runs/2026-11-18-v3-run2-2.jsonl` | answer_v3 |
| r2a | `runs/2026-11-18-v4-run1-2.jsonl` | answer_v4 |
| r2b | `runs/2026-11-18-v4-run2.jsonl` | answer_v4 |

## Runs

| Label | Round | Log | Prompt | Cost |
|---|---|---|---|---|
| F1 | baseline | `runs/2026-11-18-baseline.jsonl` | answer_v2 | Rs 4.66 |
| r1a, r1b | round 1 (layout, answer first, plumbing) | `v3-run1`, `v3-run2-2` | answer_v3 | Rs 6.82, Rs 1.77 |
| r2a, r2b | round 2 (this round) | `v4-run1-2`, `v4-run2` | answer_v4 | Rs 6.35, Rs 2.78 |

`runs/2026-11-18-v4-run1.jsonl` is a first attempt at r2a. It stopped after Q1 because the
run-cost projection was made from one question (Rs 0.56 × 37 = Rs 20.88). Since commit
`767eb54` the run stops when the actual spend passes the cap, and projects only after 5
questions. Spent today: Rs 24.88. Both round-2 runs were far below the Rs 20 stop line.

## What changed in round 2 (commits `32ae38d`, `767eb54`)

1. **Never blank the product.** A reply that fails format is sanitised: malformed items are
   dropped, and a missing status is derived from the answer, each logged as a
   `format_repair` correction. The product checks then run on it, and it is marked
   `format_repaired`.
2. **Current rule first** (prompt `answer_v4` plus a code check). When `newer` holds an
   amending or replacing GR, the first sentence must name the newest such GR's date, or a
   value or distinctive term from its change that the original GR and the question don't
   contain. If not, the reply is retried once, and flagged if still wrong. The check does
   not apply to `not_found` answers.
3. **Simpler review format.** A review item needs only `code` and `effect`; `reason` is
   optional.
4. **Q22:** see `q22_diagnosis.md`. The corrigendum was retrieved at rank 1 with its full
   text, so this is model reading, not retrieval or layout. No fix was made.

## Findings

- **The product is never blank now:** 37/37 in both round-2 runs (F1 32, round 1: 35 and
  31). Format failures themselves did not go down: 5 and 7, against 5 in F1 and 2 and 6
  in round 1. They are now shown as format-repaired answers instead of nothing.
- **Current rule first, measured by the same code check on every run's scored reply:**
  F1 8 of 12 where it applies; round 1: 10 of 20 and 12 of 20; round 2: 16 of 19 and
  17 of 21.
  - Q2, Q18 and Q28 now lead with the current rule in both round-2 runs: 31.03.2020 via
    19-06-2019; ACS/PS/Secretary via 19-03-2021; Group C and D.
- **Remaining current-rule flags (5) are mostly not order mistakes:**
  - Q18 (r2a) and Q28 (r2b): the first sentence is correct and names the corrigendum.
    The flag comes from the model marking a later GR as changing the asked-for GR: the
    05-10-2023 re-empanelment as `replaces` in Q18, and a 21-01-2021 vendor GR as
    `amends` in Q28. The check then demands that GR's date. The check is only as good as
    the model's reviews.
  - Q24 (both runs) and Q19 (r2b): yes/no questions answered "it amended it" without the
    amending GR's date in the first sentence.
- **Q22** is correct in r2b ("did not change any benefit; it only corrected … to 'Unified
  payment Interface (UPI)'") but still "I couldn't find" in r2a. So this varies between
  runs, not a fixed failure.
- **Format errors are now mostly missing fields and malformed `cited`/`newer` items**, not
  the review format. "Review item malformed" fell from 13 attempts (round 1 run 2) to 12
  and 4, and "no review for listed candidates" to 6 and 6. In r2b, 8 replies hit the
  length limit.
- **Quotes not found went up** (17 and 13, against 10 and 8 in round 1), and the checks
  made more corrections (35 and 39). More retries means more replies, more citations and
  more chances to misquote.

## Totals (37 questions)

| Measure | F1 | r1a | r1b | r2a | r2b |
|---|---|---|---|---|---|
| Format | failed 5, ok 25, retried_ok 7 | failed 2, ok 24, retried_ok 11 | failed 6, ok 23, retried_ok 8 | failed 5, ok 20, repaired 1, retried_ok 11 | failed 7, ok 21, retried_ok 9 |
| Format failures | 5 | 2 | 6 | 5 | 7 |
| Product answer shown (checked) | 32/37 | 35/37 | 31/37 | 37/37 | 37/37 |
| …of which format repaired | 0 | 0 | 0 | 5 | 7 |
| Status as expected (raw) | 32/37 | 34/37 | 35/37 | 36/37 | 36/37 |
| Any gold GR cited or newer (raw) | 29/37 | 34/37 | 35/37 | 35/37 | 34/37 |
| Any gold GR cited or newer (checked) | 26/37 | 33/37 | 29/37 | 35/37 | 34/37 |
| All gold GRs cited or newer (raw) | 20/37 | 29/37 | 29/37 | 28/37 | 29/37 |
| All gold GRs cited or newer (checked) | 20/37 | 28/37 | 24/37 | 28/37 | 29/37 |
| Questions with a gold GR left unreviewed | 4 | 0 | 0 | 0 | 1 |
| Current rule first: holds / applies (code check, all runs) | 8/12 | 10/20 | 12/20 | 16/19 | 17/21 |
| Current-rule-first flags in the log (round 2 only) | 0 | 0 | 0 | 2 | 3 |
| Answer-first flags | 0 | 2 | 0 | 0 | 1 |
| Quotes not found | 14 | 10 | 8 | 17 | 13 |
| Corrections by checks | 20 | 34 | 21 | 35 | 39 |
| Calls | - | 51 | 51 | 56 | 63 |
| Cost (Rs) | 4.66 | 6.82 | 1.77 | 6.35 | 2.78 |

## Per question

Each cell: format · status as expected · any gold GR (raw/checked) · gold GR left unreviewed.

| Q | case | F1 | r1a | r1b | r2a | r2b |
|---|---|---|---|---|---|---|
| 1 | AM | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✓ | failed · ✓ · ✓/✓ |
| 2 | AM | ok · ✓ · ✗/✗ · unreviewed 201906191741481211 | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 3 | AM | ok · ✗ · ✗/✗ | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✗ · ✓/✓ |
| 4 | AM | failed · ✗ · ✓/✗ | retried_ok · ✓ · ✓/✓ | failed · ✗ · ✓/✗ | failed · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 5 | ST | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 6 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 7 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✓ · unreviewed 202304131657547811 |
| 8 | ST | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 9 | MI | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 10 | DV | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 11 | ST | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 12 | ST | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 13 | ST | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 14 | AM | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | failed · ✓ · ✓/✓ | failed · ✓ · ✓/✓ |
| 15 | AM | ok · ✓ · ✓/✓ · unreviewed 202310041905383211 | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 16 | MI | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✓ |
| 17 | AM | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 18 | AM | ok · ✓ · ✗/✗ · unreviewed 202103191753279311 | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 19 | DU,AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 20 | AM | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 21 | AM | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✓ |
| 22 | TY | retried_ok · ✓ · ✗/✗ | ok · ✗ · ✗/✗ | retried_ok · ✗ · ✗/✗ | repaired · ✗ · ✗/✗ | ok · ✓ · ✗/✗ |
| 23 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 24 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 25 | DU | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 26 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 27 | AM | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 28 | AM | ok · ✓ · ✓/✓ · unreviewed 202002241155355511 | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | failed · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 29 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 30 | CO | ok · ✓ · ✓/✓ | retried_ok · ✗ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | failed · ✓ · ✗/✗ |
| 31 | CO | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 32 | CO | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 33 | CO | ok · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 34 | CO | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | failed · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 35 | CO | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 36 | MI | ok · ✓ · ✗/✗ | retried_ok · ✓ · ✗/✗ | ok · ✓ · ✗/✗ | ok · ✓ · ✗/✗ | retried_ok · ✓ · ✗/✗ |
| 37 | MI | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✓ |

## First sentence of the raw answer

**Q1.** Is the 29 January 2018 cloud computing circular still current?  
*Gold:* Not as issued. Deadline moved to 31-03-2020 (19-06-2019); data archival and review rules added (05-07-2019); cloud empanelment ended 30-04-2021 and buying moved to GeM (23-04-2021). Latest: 23-04-2021
- F1: The 29 January 2018 cloud computing circular is no longer current in force.
- r1a: No, the 29 January 2018 cloud computing circular is not still current.
- r1b: No, the 29 January 2018 cloud computing circular is not currently current because the 23 April 2021 GR ended the empanelment and rates under the related 2018 circulars and required all departments to procure cloud services through the GeM portal.
- r2a: No, the 29 January 2018 cloud computing circular is not current; it was superseded by a newer Government Circular on 23 April 2021, which ended the empanelment and rates under the 16 May 2018 circular on 30 April 2021 and directed all future cloud service purchases to be made through the GeM portal.
- r2b: No, the 29 January 2018 cloud computing circular is not current as a standalone instrument; it was superseded by later instructions.

**Q2.** What is the deadline for moving existing department applications to the cloud?  
*Gold:* 31-03-2020, set by the 19-06-2019 addendum (the original said 30-10-2018)
- F1: According to GR 201801291824268911 dated 29-01-2018, existing applications not hosted in a cloud environment must be migrated to cloud on or before 30.10.2018, and all Departments must review their existing software applications to ensure they are cloud ready in time for that migration.
- r1a: The deadline for migrating existing department applications to the cloud was originally 30.10.2018, but it was extended to 31.03.2020 by GR dated 19-06-2019.
- r1b: The deadline for migrating existing department applications to the cloud was initially 30-10-2018 under GR 201801291824268911, but it was amended to 31-03-2020 by GR 201906191741481211.
- r2a: The deadline for migrating existing department applications to the cloud was extended to 31.03.2020 by the GR dated 19-06-2019.
- r2b: The deadline for migrating existing department applications to the cloud is 31.03.2020, as extended by GR dated 19-06-2019.

**Q3.** There was a cloud policy circular a couple of years ago, something about migration. Which GR?  
*Gold:* The cloud policy of 29-01-2018 (not recent), plus its later changes; latest is 23-04-2021
- F1: I couldn't find a GR matching a specific date described as "a couple of years ago" in the question among the given texts, but the corpus contains several cloud policy circulars on migration.
- r1a: I couldn't find a GR on this in the corpus
- r1b: The GR dated 19-06-2019 (code 201906191741481211, number GAD-IT-060/3/2017) is the cloud policy circular about migration, setting a migration deadline of 31.03.2020 for existing applications not hosted in a cloud environment.
- r2a: The GR dated 19-06-2019 (201906191741481211), which is an addendum to GAD-IT-060/3/2017, extended the cloud migration deadline for existing applications to 31-03-2020 and made security audits mandatory before going live.
- r2b: I couldn’t find a GR on this in the corpus.

**Q4.** A file cites the State cloud policy dated 19/01/2018. Is that current?  
*Gold:* Same policy (the corpus dates it 29-01-2018; another GR cites 17.1.2018). Not current as issued; see Q1
- F1: The corpus does not contain a GR dated 19/01/2018.
- r1a: No newer GR found in this corpus that revokes or supersedes the State cloud policy dated 19/01/2018; the corpus only cites that date and notes that all remaining provisions of the IT Department GR dated 19/01/2018 shall remain in force as they are.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: No newer GR found in this corpus directly changes the State cloud policy dated 19/01/2018, but the 23-04-2021 GR (M/s 2021/3/060) replaced the earlier cloud empanelment and rate structure with GeM portal procurement, ending the 3-year empanelment on 30-04-2021.
- r2b: No newer GR found in this corpus that changes the 19/01/2018 State cloud policy directly; the policy remains referenced as still applicable in the 19 July 2024 GR, which states that all remaining provisions in the IT Department's 19/01/2018 GR shall continue unchanged.

**Q5.** Can my department still buy cloud services from the empanelled cloud providers?  
*Gold:* No. The empanelment and its rates ended 30-04-2021; departments were to buy through GeM within 45 days; the rates for ongoing cloud services expired 15-06-2021
- F1: Yes, departments can still buy cloud services from the empanelled cloud providers under the earlier GRs, but the 2021 GR ends that empanelment and requires all future cloud service purchases to be made through the GeM portal.
- r1a: No, departments cannot still buy cloud services from the empanelled cloud providers under the earlier GR because the 23-04-2021 GR ended the empanelment and rates on 30-04-2021 and directed that all further cloud services be purchased through the GeM portal.
- r1b: No, departments can no longer buy cloud services from the empanelled cloud providers, because the 2021 GR ended that empanelment on 30.04.2021 and directed all future cloud service purchases to be made through the GeM portal.
- r2a: No, departments can no longer buy cloud services from the empanelled cloud providers as per the 2018-2021 empanelment; from 23-04-2021, all government departments must purchase cloud services through the GeM portal.
- r2b: No, departments can no longer buy cloud services from the previously empanelled cloud providers because the 23-04-2021 GR ended the empanelment and rates on 30-04-2021 and directed that all future cloud services must be procured via the GeM portal.

**Q6.** What did the July 2019 cloud GR change?  
*Gold:* Added rules on which data moves to cloud, archival and periodic review. No deadline or amount change
- F1: The July 2019 cloud GR (201907051642210511, dated 05-07-2019) issued instructions to all government departments, sub-ordinate offices, public sector undertakings, urban and rural local bodies, and other state-established bodies to define and communicate cloud-hosted data and time periods to DIT in writing, confirm data to archive, verify datasets for automated removal, ensure pre-migration review for existing applications, and periodically review cloud applications and data for efficiency.
- r1a: The July 2019 cloud GR (060/3/2017, dated 05-07-2019) instructed all departments to define and communicate in writing the data to be migrated or hosted on the cloud and the time period, and to confirm data to be archived and verify datasets for automated removal.
- r1b: The July 2019 cloud GR (05-07-2019) issued instructions to departments on hosting IT applications on cloud, including data migration, archiving, and periodic review, and cited the E-Governance policy para 7.13.
- r2a: The July 2019 cloud GR instructed all government departments to define and communicate data for migration to cloud, confirm archived data, verify automated data removal, ensure pre-migration review for existing applications, and periodically review applications on cloud.
- r2b: The 2021-04-23 GR amends the July 2019 cloud GR by requiring all government departments to procure cloud services through the GeM portal, ending the previous empanelment on 30-04-2021, and mandating migration to a new cloud within 46 days with the empanelment rate expiring on 15-06-2021.

**Q7.** What is the maximum spend on a laptop or tablet for an IAS, IPS or IFS officer?  
*Gold:* Rs 1,20,000 (12-04-2023). Earlier cap Rs 85,000 (24-12-2019)
- F1: The maximum spend on a laptop or tablet for an IAS, IPS or IFS officer is Rs. 120,000, as set by the 2023 GR which superseded the 2019 GR that had Rs. 85,000.
- r1a: The maximum spend on a laptop or tablet for an IAS, IPS, or IFS officer is Rs. 120,000, as set by the newer GR dated 12-04-2023 which amended the earlier limit of Rs. 85,000.
- r1b: The maximum spend on a laptop or tablet for an IAS, IPS or IFS officer is Rs. 1,20,000, as set by the 2023 GR.
- r2a: The current maximum spend on a laptop or tablet for an IAS, IPS, or IFS officer is Rs. 120,000, as set by the GR dated 12-04-2023.
- r2b: The maximum spend on a laptop or tablet for an IAS, IPS or IFS officer is Rs. 120,000, as set by the GR dated 12-04-2023.

**Q8.** Is the 24 December 2019 laptop corrigendum still in force?  
*Gold:* No. Superseded by the 12-04-2023 corrigendum, which replaces paragraph 1
- F1: The 24 December 2019 laptop corrigendum is not in force because the 12 April 2023 GR supersedes it; the newer GR raises the maximum purchase limit from Rs. 85,000 to Rs. 120,000.
- r1a: No, the 24 December 2019 laptop corrigendum is not still in force because a newer GR dated 12-04-2023 superseded it.
- r1b: No, the 24 December 2019 laptop corrigendum is not in force because it has been superseded by the 12 April 2023 GR, which also raised the maximum purchase limit to Rs. 120,000.
- r2a: No, the 24 December 2019 laptop corrigendum is not still in force; it was superseded by the GR dated 12-04-2023, which also raised the purchase limit to Rs 1,20,000.
- r2b: The 24 December 2019 laptop corrigendum is no longer in force because it was superseded by the GR dated 12-04-2023, which replaced it and raised the maximum purchase limit to Rs. 120,000.

**Q9.** Show me the 24 February 2015 GR on laptops for officers.  
*Gold:* Not in this corpus. Its paragraph 1 was amended in 2019 and again in 2023 (cap now Rs 1,20,000)
- F1: I couldn't find a GR on this in the corpus (dated 24-02-2015).
- r1a: I couldn't find a GR on this in the corpus for 24-02-2015.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: I couldn't find a GR on this in the corpus for 24 February 2015.
- r2b: I couldn't find a GR on 24 February 2015 in the corpus; it is cited in later GRs as Governance Resolution No. मातंस ३८१४/प्र.क्र.१७४/३९, दि.

**Q10.** मातंस ३८१४/प्र.क्र.१७४/३९: what is the current limit?  
*Gold:* Rs 1,20,000 (12-04-2023)
- F1: (no answer)
- r1a: The current maximum purchase limit is Rs. 120,000, as set by the GR dated 12-04-2023.
- r1b: The current limit is Rs. 120,000.
- r2a: The current limit for purchase is Rs. 120,000, as set by the GR dated 12-04-2023.
- r2b: The current limit under the latest applicable GR is Rs. 1,20,000, as set by the GR dated 12-04-2023.

**Q11.** Is the 26 November 2020 GR on the computer qualification certificate in force?  
*Gold:* No. Stayed until further orders by the GR of 27-11-2020, which reinstated the orders under the 20-11-2018 letter
- F1: The 26-11-2020 GR on the computer qualification certificate is stayed by the 27-11-2020 GR, which puts it on hold till further orders and restores the 20-11-2018 letter orders.
- r1a: No, the 26 November 2020 GR is not in force because the 27 November 2020 GR stayed it until further orders.
- r1b: No newer GR found in this corpus that keeps the 26 November 2020 GR in force; instead, a GR dated 27 November 2020 stayed it till further orders.
- r2a: No, the 26 November 2020 GR is not in force because it was stayed on 27 November 2020 until further orders.
- r2b: The 26 November 2020 GR is not in force because the 27 November 2020 GR stays it until further orders.

**Q12.** Will excess salary be recovered from staff who were late with the computer certificate?  
*Gold:* The recovery order of 26-11-2020 was stayed on 27-11-2020; no newer order in this corpus
- F1: The 26 November 2020 GR (202011261535430611) decided that excess salary paid because increments were not withheld from staff who failed to submit the computer certificate on time should be recovered.
- r1a: Yes, the GR dated 26-11-2020 directed that excess salary paid to staff who did not submit the computer qualification certificate within the prescribed time must be recovered.
- r1b: Yes, excess salary was to be recovered from staff who were late with the computer certificate, but a later stay order suspended that recovery until further orders.
- r2a: No, excess salary will not be recovered from staff who were late with the computer certificate because the 27-11-2020 GR stayed the recovery decision of the 26-11-2020 GR until further orders and restored the earlier 20-11-2018 letter orders.
- r2b: Yes, excess salary will be recovered from staff who were late with the computer certificate, but the 27-11-2020 stay order puts that recovery rule on hold until further orders.

**Q13.** Is the 2018 empanelment of IT consultants still valid?  
*Gold:* No. It expired 19-03-2023, was extended to 19-09-2023 (24-04-2023), and was replaced by a new empanelment from 20-09-2023 to 19-09-2028 (05-10-2023)
- F1: The 2018 empanelment is no longer valid because the 2023 GR (dated 05-10-2023) states it expired on 19th September 2023 and replaced it with a new 5-year empanelment from 20th September 2023 to 19th September 2028.
- r1a: No, the 2018 empanelment is no longer valid.
- r1b: No, the 2018 empanelment is not still valid.
- r2a: The 2018 empanelement of IT consultants is no longer valid; it was replaced by a new GR dated 05-10-2023 which empaneled firms for a period from 20-09-2023 to 19-09-2028.
- r2b: No, the 2018 empanelment is no longer valid; it was superseded by a new empanelment issued on 05-10-2023 effective from 20-09-2023 to 19-09-2028.

**Q14.** From what date do the new IT consultant rates apply?  
*Gold:* 20-09-2023, per the 15-12-2023 clarification (not the 05-10-2023 GR date)
- F1: The new IT consultant rates apply from 20th September 2023, as clarified by the circular dated 15-12-2023.
- r1a: The new IT consultant rates apply from 20th September 2023, as clarified by the 15-12-2023 circular and set by the 05-10-2023 GR for work orders issued from its date.
- r1b: The new IT consultant rates apply from 20th September 2023, as clarified by the 15-12-2023 circular, and the 2023 GR (dated 05-10-2023) states that its rates apply for all work orders issued from its date of issue.
- r2a: The new IT consultant rates apply from 20th September 2023, as set by the GR dated 05-10-2023 (202310041905383211), which replaced the earlier 2018 GR.
- r2b: The new IT consultant rates apply from 20th September 2023, as clarified in the Government Circular dated 15-12-2023 (code 202312151508137711).

**Q15.** What is the monthly rate for a Principal Consultant?  
*Gold:* Rs 4,54,000 excluding taxes (05-10-2023). The 2018 rate was Rs 3,24,000
- F1: The monthly rate for a Principal Consultant under the 20-03-2018 GR is INR 3,24,000 per month per person (excluding taxes).
- r1a: The monthly rate for a Principal Consultant under the 2018 GR is 3,24,000 INR per month per person (excluding taxes) for >15 years of experience.
- r1b: The monthly rate for a Principal Consultant under the 2018 GR was 3,24,000 INR per month (excluding taxes), but the 2023 GR replaced it with a rate of 4,54,000 INR per month (excluding taxes) for consultants with more than 13 years of experience.
- r2a: The current monthly rate for a Principal Consultant is 454,000 INR per month per person (excluding taxes), as set by the Government Resolution dated 05-10-2023.
- r2b: The current monthly rate for a Principal Consultant is INR 454,000 (excluding taxes), applicable for more than 13 years of experience, under the GR dated 05-10-2023.

**Q16.** What did the 9 May 2019 IT consultant GR say?  
*Gold:* Not in this corpus, though later GRs cite it
- F1: I couldn't find a GR on 9 May 2019 in the corpus.
- r1a: I couldn't find a GR on this in the corpus.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: I couldn't find a GR on this in the corpus.
- r2b: I couldn't find a GR on this in the corpus.

**Q17.** Can a department change the qualifications it asks of empanelled consultants?  
*Gold:* Yes for the profile of personnel, through change orders (RFP 24.19); not the years of experience (05-03-2024)
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 201803201319308011 GR on consultant qualifications.
- r1a: Yes, a department can change the qualifications it asks of empanelled consultants by using clauses under Section 24.19 of the RFP (Change Orders) to change the Profile of Personnel required for the engagement, but it cannot change the Years of Experience mentioned in the GR for the Category of resources required for the engagement.
- r1b: Yes, a department can change the qualifications it asks of empanelled consultants by altering the profile of personnel through clauses under Section 24.19 of the RFP (Change Orders), but it cannot change the years of experience mentioned in the GR for the category of resources required for the engagement.
- r2a: Yes, a department can change the qualifications it asks of empanelled consultants by using clauses under Section 24.19 of the RFP (Change Orders) to change the 'Profile of Personnel' required for the engagement, but it may not change the 'Years of Experience' mentioned in the GR for the category of resources required.
- r2b: Yes, a department can change the qualifications it asks of empanelled consultants by using clauses under Section 24.19 of the RFP (Change Orders) to change the Profile of Personnel, as clarified by the GR dated 05-03-2024.

**Q18.** Whose concurrence is needed for a consultant's scope of work?  
*Gold:* The department's ACS/PS/Secretary, not DIT (corrigendum 19-03-2021). Not changed by a later GR in this corpus
- F1: According to the Government Resolution dated 20-03-2018, departments need to finalize the scope of work for consultancy with the concurrence of DIT.
- r1a: Yes, concurrence is needed for a consultant's scope of work.
- r1b: The 2018 GR requires concurrence of DIT to finalize the scope of work for consultancy.
- r2a: The current rule, as amended by the GR dated 19-03-2021, requires the concurrence of the ACS / PS / Secretary of the concerned Department for finalizing the Scope of work for consultancy.
- r2b: The current rule is that departments must finalize the scope of work for consultancy with the concurrence of the ACS / PS / Secretary of the concerned Department, as amended by the GR dated 19-03-2021.

**Q19.** Has the Maha DBT disbursement GR of 12 October 2018 been changed?  
*Gold:* Yes. Paragraphs 8 and 9 amended 30-11-2021. The English and Marathi copies of 12-10-2018 are one GR
- F1: Yes, the Maha DBT disbursement GR of 12-10-2018 has been amended.
- r1a: Yes, the Maha DBT disbursement GR of 12-10-2018 has been amended.
- r1b: Yes, the Maha DBT disbursement GR of 12 October 2018 has been amended.
- r2a: Yes, the Maha DBT disbursement GR of 12 October 2018 has been amended by the GR dated 30 November 2021.
- r2b: Yes, the Maha DBT disbursement GR of 12-10-2018 has been changed.

**Q20.** Which bank must hold a scheme's Maha DBT Central Pool Account?  
*Gold:* State Bank of India (30-11-2021)
- F1: The 2021 GR amends the 2018 GR to require that each department open its scheme-wise Central Pool Account in State Bank of India, because that bank is linked to both the MahaDBT portal and PFMS.
- r1a: The bank that must hold a scheme's Maha DBT Central Pool Account is State Bank of India.
- r1b: The State Bank of India must hold a scheme's Maha DBT Central Pool Account.
- r2a: The scheme's Maha DBT Central Pool Account must be held by State Bank of India.
- r2b: State Bank of India must hold the scheme's Maha DBT Central Pool Account.

**Q21.** What rent support does the Fintech policy give start-ups?  
*Gold:* Up to Rs 4 lakh a year for 3 years for early-stage start-ups, added by the addendum of 30-11-2018
- F1: The Fintech policy provides rent reimbursement for early stage Fintech start-ups up to an upper limit of Rs. 4 lakh per year for a total period of 3 years.
- r1a: The Fintech policy (Government Resolution DIT-2018/C.R-17/D-1/39 dated 16 February 2018) does not itself contain a rent reimbursement provision in its original text; it is added by the later Government Addendum dated 30 November 2018.
- r1b: The Fintech policy gives start-ups rent reimbursement for office space, capped at Rs. 4 Lakh per year for a total period of 3 years, and allows co-working space rent adjustment at source if the co-working site is a partner with Mumbai Fintech Hub.
- r2a: The Fintech policy reimburses rent for office space paid by early stage Fintech start-ups, subject to an upper limit of Rs. 4 Lakh per year for a total period of 3 years; Fintech start-ups operating out of co-working spaces can adjust the co-working space rent at source if the co-working site is a partner with Mumbai Fintech Hub.
- r2b: The Fintech policy gives start-ups rent reimbursement for office space up to Rs. 4 Lakh per year for a total of 3 years, and co-working space rent can be adjusted at source if the co-working site is a partner with Mumbai Fintech Hub.

**Q22.** Did the 30 November 2018 Fintech corrigendum change any benefit?  
*Gold:* No. It only corrects United payments Interface to Unified payment Interface
- F1: The corpus does not contain any newer GR that amends, replaces, stays, extends or clarifies the 30 November 2018 corrigendum (code 201811301240117211).
- r1a: I couldn't find a GR on this in the corpus.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: I couldn't find a GR on this in the corpus.
- r2b: The 30 November 2018 Fintech corrigendum (code 201811301240117211) did not change any benefit; it only corrected a typographical error in the 16 February 2018 GR, changing "United payments Interface (UPI)" to "Unified payment Interface (UPI)".

**Q23.** Who represents the National Health Mission on the blockchain health-records working group?  
*Gold:* The Additional Director, NHM (corrigendum 04-10-2019), not the Director
- F1: The National Health Mission is represented by the Additional Mission Director, National Health Mission, Mumbai-1, on the blockchain health-records working group, as clarified by the corrigendum dated 04-10-2019.
- r1a: The Additional Mission Director, National Health Mission, Mumbai-1 represents the National Health Mission on the blockchain health-records working group.
- r1b: The National Health Mission is represented on the blockchain health-records working group by the Additional Mission Director, National Health Mission, Mumbai-1, as amended by the 04-10-2019 corrigendum.
- r2a: The Additional Mission Director, National Health Mission, Mumbai-1 represents the National Health Mission on the blockchain health-records working group, as amended by the 04-10-2019 corrigendum.
- r2b: The Additional Mission Director, National Health Mission, Mumbai-1 represents the National Health Mission on the blockchain health-records working group, as amended by the 04-10-2019 corrigendum.

**Q24.** Did the April 2019 Urban MahaNet GR replace the September 2018 GR?  
*Gold:* No. It adds three items (statewide ROW waiver, smart poles, 5-year total contract); the 2018 GR stands
- F1: The 10-04-2019 GR amends the 28-09-2018 GR rather than replacing it.
- r1a: No, the April 2019 Urban MahaNet GR did not replace the September 2018 GR.
- r1b: No, the April 2019 Urban MahaNet GR did not replace the September 2018 GR; it amended it.
- r2a: The April 2019 Urban MahaNet GR does not replace the September 2018 GR; it amends it.
- r2b: Yes, the April 2019 GR amended the September 2018 GR rather than replacing it.

**Q25.** Find the Urban MahaNet GR of 28 September 2018.  
*Gold:* One GR with English and Marathi copies; later amended 10-04-2019
- F1: The Urban MahaNet GR of 28 September 2018 is code 201809281811031811, titled 'Implementation of Urban MahaNet project and Delivery of E-Governance Services'.
- r1a: The Urban MahaNet GR dated 28-09-2018 (code 201809281811031811) was found in the corpus.
- r1b: The Urban MahaNet GR dated 28-09-2018 (code 201809281811031811) is found in the corpus.
- r2a: The Urban MahaNet GR dated 28-09-2018 was amended by the GR dated 10-04-2019 to waive ROW fees, allow Smart Pole installations, and extend the TSP contract to 5 years.
- r2b: The current rule for the Urban MahaNet project, as amended on 10-04-2019, waives right of way fees across the state, allows the TSP to install Smart Poles and Wi-Fi provisioning, and sets the total contract period with the TSP at 5 years.

**Q26.** Within how many days must a department pay MahaIT's Urban MahaNet invoice?  
*Gold:* 15 days from the invoice date (24-12-2018)
- F1: The department or office must pay MahaIT's Urban MahaNet invoice within 15 days from the date of issuance, as per the 24-12-2018 GR.
- r1a: A department must pay MahalT's Urban MahaNet invoice within 15 days from the date of invoice issuance.
- r1b: Departments must pay MahaIT's Urban MahaNet invoice within 15 days from the date of invoice issuance.
- r2a: The current rule requires departments to pay MahaIT's Urban MahaNet invoice within 15 days from the date of invoice issuance, as set by the 24-12-2018 GR.
- r2b: Departments must pay MahaIT's Urban MahaNet invoice within 15 days from the date of invoice issuance, as per GR dated 24-12-2018.

**Q27.** Which university is responsible for the Academic module of the IUMS project?  
*Gold:* S.N.D.T. Women's University (corrigendum 18-04-2019); earlier Dr. Babasaheb Ambedkar Technological University, Lonere (12-12-2018)
- F1: (no answer)
- r1a: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project according to the 18-04-2019 GR.
- r1b: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project according to the 18-04-2019 Government Resolution.
- r2a: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project as per the 18-04-2019 GR.
- r2b: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project as per the 18-04-2019 GR.

**Q28.** Which groups does the Maha-Pariksha GR of 20 February 2020 apply to?  
*Gold:* Group C and Group D. The preamble said Group B and C; the corrigendum of 24-02-2020 corrected it to Group C and D
- F1: The Maha-Pariksha GR of 20-02-2020 applies to Group-B and Group-C category recruitment examinations conducted through the Maha-Pariksha portal in all administrative departments and their subordinate offices of the Government of Maharashtra.
- r1a: The Maha-Pariksha GR of 20 February 2020 applies to Group-B and Group-C category posts in all administrative departments and their subordinate offices across the state.
- r1b: The Maha-Pariksha GR of 20-02-2020 applies to Group-C and Group-D divisional posts in all administrative departments and their subordinate offices of the Government in the State.
- r2a: The Maha-Pariksha GR of 20-02-2020 applies to Group-C and Group-D recruitment in all administrative departments and their subordinate offices of the Government in the State.
- r2b: The Maha-Pariksha GR of 20-02-2020 applies to Group-C and Group-D posts in all administrative departments and their subordinate offices of the Government in Maharashtra, as amended by the supplementary GR of 24-02-2020 which changed the preamble from Group-B and Group-C to Group-C and Group-D. Earlier, the 2020 GR stated that it applied to Group-B and Group-C posts.

**Q29.** What did the 19 July 2021 corrigendum change in the 6 April 2021 disability-reservation GR?  
*Gold:* It deleted the sentence in para 2 saying senior and junior scientific officer posts were left out because an earlier GR (18-02-2021) covers them. The rest of para 2 is unchanged
- F1: The 19 July 2021 corrigendum removed the sentence in paragraph 2 of the 6 April 2021 GR that had excluded two posts (Senior Scientist/Junior Scientist) at the Rajiv Gandhi Science and Technology Commission from this decision because they were already covered in a prior SE-1 government decision.
- r1a: The 19 July 2021 corrigendum deleted the sentence in paragraph 2 of the 6 April 2021 GR that excluded two posts (senior scientist/junior scientist) in the Rajiv Gandhi Science and Technology Commission because they were already covered in an SE-1 GR, thereby including those posts.
- r1b: The 19-07-2021 corrigendum amends the 06-04-2021 GR by deleting the exclusion sentence in paragraph 2, so that the two posts of Senior Scientist and Junior Scientist in the Rajiv Gandhi Science and Technology Commission are now included in the disability reservation.
- r2a: The 19 July 2021 corrigendum amends the 6 April 2021 GR by removing the sentence from paragraph 2 that excluded two posts (Senior Scientist/Junior Scientist) in the Rajiv Gandhi Science and Technology Commission because they had already been included elsewhere.
- r2b: The 19-07-2021 corrigendum amended the 06-04-2021 GR by removing the sentence in paragraph 2 that excluded two posts in the Rajiv Gandhi Science and Technology Commission because they were covered by a separate SE-1 government decision.

**Q30.** Is the e-Tenders GR of 11 May 2021 still the latest on e-tendering?  
*Gold:* No newer GR found in this corpus (covers 2018 to 2024)
- F1: The asked-for GR dated 11-05-2021 (Implementation of E-Tenders) is not amended, replaced, stayed, extended, or clarified by any newer GR in the corpus.
- r1a: I couldn't find a GR on this in the corpus.
- r1b: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the e-Tenders GR of 11 May 2021.
- r2a: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends or clarifies the e-Tenders GR of 11 May 2021.
- r2b: No newer GR found in this corpus (covers 2018 to 2024) changes the e-Tenders GR of 11-05-2021 (202105111646307611).

**Q31.** Has the model RFP GR of September 2019 been updated?  
*Gold:* No newer GR found in this corpus
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 20-09-2019 Model RFP GR.
- r1a: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the Maharashtra Model RFP GR of 20-09-2019.
- r1b: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the Model RFP GR of 20-09-2019.
- r2a: No newer GR found in this corpus (covers 2018 to 2024) has updated the model RFP GR of 20-09-2019.
- r2b: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays or extends the September 2019 Model RFP GR.

**Q32.** What is the latest GR on the State Data Center as critical information infrastructure?  
*Gold:* 05-10-2019; no newer GR found in this corpus
- F1: The latest GR in the corpus on declaring the Maharashtra State Data Center as Critical Information Infrastructure (CII) is dated 05-10-2019 (Government Circular No. H – DIT2019/CR 34/3/39).
- r1a: The latest GR in the corpus on the State Data Center as critical information infrastructure is dated 05-10-2019 (GR H – DIT2019/CR 34/3/39), which declares the Maharashtra State Data Center as Critical Information Infrastructure (CII).
- r1b: The latest GR in the corpus on the State Data Center as critical information infrastructure is dated 05-10-2019.
- r2a: The latest GR on the State Data Center as critical information infrastructure is the 2019 GR dated 05-10-2019, which declares the Maharashtra State Data Center as Critical Information Infrastructure (CII).
- r2b: The latest GR in the corpus declaring the Maharashtra State Data Center as Critical Information Infrastructure is dated 05-10-2019 (GR H – DIT2019/CR 34/3/39).

**Q33.** What is the latest GR on the Maharashtra Unified Citizen Data Hub?  
*Gold:* 04-02-2022; no newer GR found in this corpus
- F1: I couldn't find a GR on this in the corpus.
- r1a: The latest GR on the Maharashtra Unified Citizen Data Hub in the corpus is dated 04-02-202022.
- r1b: The latest GR on the Maharashtra Unified Citizen Data Hub in this corpus is dated 04-02-2022.
- r2a: The latest GR on the Maharashtra Unified Citizen Data Hub is the one dated 04-02-2022, which establishes the scheme and allocates Rs 294.02 crore for its implementation.
- r2b: The latest GR in the corpus on the Maharashtra Unified Citizen Data Hub is dated 04-02-2022 (GR 202202042136207511), which approves the implementation of the hub for digitalization of government services with an administrative approval and allocation of Rs 294.02 crore for the project.

**Q34.** Is there a GR on a 5G task force, and has it changed?  
*Gold:* 27-03-2023; no newer GR found in this corpus
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 5G task force GR (202303301831230311 dated 27-03-2023).
- r1a: Yes, there is a GR on a 5G task force in the corpus: GR number मातंसं-११० ९ ०/प्र.क्र .२/२०२० dated 27-03-2023 titled Regarding setting up a task force to launch and implement 5G services in the state.
- r1b: Yes, there is a GR on a 5G task force: GR 202303301831230311 dated 27-03-2023, which establishes a task force committee to launch and implement 5G services in the state and defines its members and functions.
- r2a: Yes, there is a GR on a 5G task force: GR 202303301831230311 dated 27-03-2023 sets up a Task Force Committee to launch and implement 5G services in the state.
- r2b: Yes, there is a GR on a 5G task force in the corpus.

**Q35.** What is the latest GR on the Setu Kendra tender process?  
*Gold:* 19-07-2024; no newer GR found in this corpus
- F1: The latest GR on the Setu Kendra tender process is dated 19-07-2024 (code 202407191742379111), titled Regarding the tender process of Setu Kendra in the collector and tehsil offices of the state.....
- r1a: The latest GR on the Setu Kendra tender process in the corpus is dated 19-07-2024 (code 202407191742379111).
- r1b: The latest GR on the Setu Kendra tender process in this corpus is dated 19-07-2024 and requires all Setu Kendras at district headquarters and tehsil offices to remain operational, with the tender process to be completed within three months where it has expired or centres are closed.
- r2a: The latest GR on the Setu Kendra tender process is the one dated 19-07-2024, which requires all Setu Kendras at district headquarters and tehsil offices to remain operational and the tender process to be completed within 3 months.
- r2b: The latest GR on the Setu Kendra tender process is dated 19-07-2024 and mandates that all Setu Kendras at district headquarters and tahsil offices must remain operational, with tendering completed within three months where agency terms have expired.

**Q36.** Is the 2022 GR on generative AI use in government offices in force?  
*Gold:* No such 2022 GR in this corpus. Closest: the circular of 03-03-2020 on AI, Marathi language technology and NLP in government work; a good answer names it without claiming it is the GR asked for
- F1: I couldn't find a GR on the use of generative AI in government offices in the corpus.
- r1a: I couldn't find a GR on this in the corpus.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: I couldn't find a GR on this in the corpus.
- r2b: I couldn't find a GR on this in the corpus.

**Q37.** What did the 19 September 2017 Maha-Pariksha GR say?  
*Gold:* Not in this corpus. It was superseded by the GR of 20-02-2020
- F1: I couldn't find a GR on this in the corpus.
- r1a: I couldn't find a GR on this in the corpus, because the corpus does not contain the 19 September 2017 Maha-Pariksha GR itself.
- r1b: I couldn't find a GR on this in the corpus.
- r2a: I couldn't find a GR on this in the corpus.
- r2b: I couldn't find a GR on this in the corpus.

