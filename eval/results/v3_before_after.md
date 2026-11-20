# Before/after: F1 vs the fixed engine (two runs)

Automatic measures only; they are proxies, not the hand scores. "Raw" is the model's own output; "checked" is after the product checks (repairs, drops, metadata).

| Run | Log | Prompt |
|---|---|---|
| F1 | `runs/2026-11-18-baseline.jsonl` | answer_v2 |
| run1 | `runs/2026-11-18-v3-run1.jsonl` | answer_v3 |
| run2 | `runs/2026-11-18-v3-run2-2.jsonl` | answer_v3 |

## What changed (commits `213c181`, `e8e3e09`)

1. **Layout:** every newer-GR candidate of the top retrieved GRs gets its own full-text
   block, even when it is also a retrieved GR. One review entry is required per listed
   candidate; if any is missing, the reply is retried once (logged).
2. **Answer first (prompt `answer_v3`):** the first sentence answers directly and agrees
   with status. Logged flags if it doesn't, or if the answer says "couldn't find" while
   citing the asked-for GR.
3. **Plumbing:**
   - Empty replies are retried.
   - A length-limit reply is retried with a compact context.
   - Two format slips are repaired and logged.
   - The least-broken reply is scored when none is valid.
   - NUMBER FACTS for GR numbers in the question.
   - A reply is never lost on a processing error.

The product checks are unchanged. Q1 and Q36 prompts are untouched (baseline failures,
for later).

## Run notes

- **Run 1:** `runs/2026-11-18-v3-run1.jsonl`, CSV `runs/2026-11-18-v3-run1.csv`. Rs 6.82,
  51 calls.
- **Run 2:** `runs/2026-11-18-v3-run2-2.jsonl`, CSV `runs/2026-11-18-v3-run2-2.csv`.
  Rs 1.77, 51 calls; 97% of prompt tokens were cached. It was rerun in full after the
  first attempt (`runs/partial/2026-11-18-v3-run2.jsonl`, CSV `runs/partial/2026-11-18-v3-run2.csv`)
  stopped at Q16 on a bug in reply processing (fixed in `e8e3e09`; Rs 0.62).
- **Total spent today:** Rs 15.18. No run came near the Rs 20 stop line.

## Key findings

- **The amending GR is now reviewed in every case.** The four cases from F1 (Q2
  19-06-2019, Q15 05-10-2023, Q18 19-03-2021, Q28 24-02-2020) are reviewed as
  `amends` or `replaces` and listed in `newer` in both runs. Questions with a gold GR
  left unreviewed: F1 4, run 1 0, run 2 0.
- **The answer does not always lead with the current position.** Q2 is now right in
  both runs (31-03-2020 via 19-06-2019). In Q18 (run 2) and Q28 (run 1) the first
  sentence states the original rule (DIT; Group B and C) and the second gives the
  correction. That is an answer-first slip the flags don't catch (they only check
  "couldn't find" against status).
- **Q10 and Q27 now get answers** in both runs: Rs 1,20,000; S.N.D.T. Women's
  University (18-04-2019).
- **Format failures vary a lot between runs: 2 vs 6** (F1: 5).
  - The new review requirement adds a failure mode: "no review for listed candidates"
    was the commonest error in run 1 (8 attempts) and the second commonest in run 2 (11).
  - Malformed review items (13) and cited items without codes come next.
  - Q28 in run 2 had the right answer (Group C and D) but failed format: the retry had
    a duplicate key and a broken `newer` item. So the product showed nothing.
- **"Checked" can be below "raw"** because a format failure gives no product answer,
  while its raw reply can still cite a gold GR.

## Totals (37 questions)

| Measure | F1 | run1 | run2 |
|---|---|---|---|
| Format | failed 5, ok 25, retried_ok 7 | failed 2, ok 24, retried_ok 11 | failed 6, ok 23, retried_ok 8 |
| Format failures | 5 | 2 | 6 |
| Status as expected (raw) | 32/37 | 34/37 | 35/37 |
| Any gold GR cited or newer (raw) | 29/37 | 34/37 | 35/37 |
| Any gold GR cited or newer (checked) | 26/37 | 33/37 | 29/37 |
| All gold GRs cited or newer (raw) | 20/37 | 29/37 | 29/37 |
| All gold GRs cited or newer (checked) | 20/37 | 28/37 | 24/37 |
| Questions with a gold GR left unreviewed | 4 | 0 | 0 |
| Answer-first flags | 0 | 2 | 0 |
| Quotes not found | 14 | 10 | 8 |
| Corrections by checks | 20 | 34 | 21 |
| Calls | - | 51 | 51 |
| Cost (Rs) | 4.66 | 6.82 | 1.77 |

## Per question

Each cell: format · status as expected · any gold GR (raw/checked) · gold GR left unreviewed.

| Q | case | F1 | run1 | run2 |
|---|---|---|---|---|
| 1 | AM | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 2 | AM | ok · ✓ · ✗/✗ · unreviewed 201906191741481211 | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 3 | AM | ok · ✗ · ✗/✗ | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ |
| 4 | AM | failed · ✗ · ✓/✗ | retried_ok · ✓ · ✓/✓ | failed · ✗ · ✓/✗ |
| 5 | ST | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 6 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 7 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 8 | ST | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 9 | MI | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 10 | DV | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 11 | ST | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 12 | ST | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 13 | ST | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ |
| 14 | AM | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ |
| 15 | AM | ok · ✓ · ✓/✓ · unreviewed 202310041905383211 | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 16 | MI | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 17 | AM | failed · ✓ · ✓/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 18 | AM | ok · ✓ · ✗/✗ · unreviewed 202103191753279311 | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 19 | DU,AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 20 | AM | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 21 | AM | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ | retried_ok · ✓ · ✓/✓ |
| 22 | TY | retried_ok · ✓ · ✗/✗ | ok · ✗ · ✗/✗ | retried_ok · ✗ · ✗/✗ |
| 23 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 24 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 25 | DU | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 26 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 27 | AM | failed · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 28 | AM | ok · ✓ · ✓/✓ · unreviewed 202002241155355511 | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ |
| 29 | AM | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ |
| 30 | CO | ok · ✓ · ✓/✓ | retried_ok · ✗ · ✓/✓ | retried_ok · ✓ · ✓/✓ |
| 31 | CO | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 32 | CO | ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 33 | CO | ok · ✗ · ✗/✗ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 34 | CO | retried_ok · ✓ · ✓/✓ | retried_ok · ✓ · ✓/✓ | failed · ✓ · ✓/✗ |
| 35 | CO | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |
| 36 | MI | ok · ✓ · ✗/✗ | retried_ok · ✓ · ✗/✗ | ok · ✓ · ✗/✗ |
| 37 | MI | retried_ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ | ok · ✓ · ✓/✓ |

## First sentence of the raw answer

**Q1.** Is the 29 January 2018 cloud computing circular still current?  
*Gold:* Not as issued. Deadline moved to 31-03-2020 (19-06-2019); data archival and review rules added (05-07-2019); cloud empanelment ended 30-04-2021 and buying moved to GeM (23-04-2021). Latest: 23-04-2021
- F1: The 29 January 2018 cloud computing circular is no longer current in force.
- run1: No, the 29 January 2018 cloud computing circular is not still current.
- run2: No, the 29 January 2018 cloud computing circular is not currently current because the 23 April 2021 GR ended the empanelment and rates under the related 2018 circulars and required all departments to procure cloud services through the GeM portal.

**Q2.** What is the deadline for moving existing department applications to the cloud?  
*Gold:* 31-03-2020, set by the 19-06-2019 addendum (the original said 30-10-2018)
- F1: According to GR 201801291824268911 dated 29-01-2018, existing applications not hosted in a cloud environment must be migrated to cloud on or before 30.10.2018, and all Departments must review their existing software applications to ensure they are cloud ready in time for that migration.
- run1: The deadline for migrating existing department applications to the cloud was originally 30.10.2018, but it was extended to 31.03.2020 by GR dated 19-06-2019.
- run2: The deadline for migrating existing department applications to the cloud was initially 30-10-2018 under GR 201801291824268911, but it was amended to 31-03-2020 by GR 201906191741481211.

**Q3.** There was a cloud policy circular a couple of years ago, something about migration. Which GR?  
*Gold:* The cloud policy of 29-01-2018 (not recent), plus its later changes; latest is 23-04-2021
- F1: I couldn't find a GR matching a specific date described as "a couple of years ago" in the question among the given texts, but the corpus contains several cloud policy circulars on migration.
- run1: I couldn't find a GR on this in the corpus
- run2: The GR dated 19-06-2019 (code 201906191741481211, number GAD-IT-060/3/2017) is the cloud policy circular about migration, setting a migration deadline of 31.03.2020 for existing applications not hosted in a cloud environment.

**Q4.** A file cites the State cloud policy dated 19/01/2018. Is that current?  
*Gold:* Same policy (the corpus dates it 29-01-2018; another GR cites 17.1.2018). Not current as issued; see Q1
- F1: The corpus does not contain a GR dated 19/01/2018.
- run1: No newer GR found in this corpus that revokes or supersedes the State cloud policy dated 19/01/2018; the corpus only cites that date and notes that all remaining provisions of the IT Department GR dated 19/01/2018 shall remain in force as they are.
- run2: I couldn't find a GR on this in the corpus.

**Q5.** Can my department still buy cloud services from the empanelled cloud providers?  
*Gold:* No. The empanelment and its rates ended 30-04-2021; departments were to buy through GeM within 45 days; the rates for ongoing cloud services expired 15-06-2021
- F1: Yes, departments can still buy cloud services from the empanelled cloud providers under the earlier GRs, but the 2021 GR ends that empanelment and requires all future cloud service purchases to be made through the GeM portal.
- run1: No, departments cannot still buy cloud services from the empanelled cloud providers under the earlier GR because the 23-04-2021 GR ended the empanelment and rates on 30-04-2021 and directed that all further cloud services be purchased through the GeM portal.
- run2: No, departments can no longer buy cloud services from the empanelled cloud providers, because the 2021 GR ended that empanelment on 30.04.2021 and directed all future cloud service purchases to be made through the GeM portal.

**Q6.** What did the July 2019 cloud GR change?  
*Gold:* Added rules on which data moves to cloud, archival and periodic review. No deadline or amount change
- F1: The July 2019 cloud GR (201907051642210511, dated 05-07-2019) issued instructions to all government departments, sub-ordinate offices, public sector undertakings, urban and rural local bodies, and other state-established bodies to define and communicate cloud-hosted data and time periods to DIT in writing, confirm data to archive, verify datasets for automated removal, ensure pre-migration review for existing applications, and periodically review cloud applications and data for efficiency.
- run1: The July 2019 cloud GR (060/3/2017, dated 05-07-2019) instructed all departments to define and communicate in writing the data to be migrated or hosted on the cloud and the time period, and to confirm data to be archived and verify datasets for automated removal.
- run2: The July 2019 cloud GR (05-07-2019) issued instructions to departments on hosting IT applications on cloud, including data migration, archiving, and periodic review, and cited the E-Governance policy para 7.13.

**Q7.** What is the maximum spend on a laptop or tablet for an IAS, IPS or IFS officer?  
*Gold:* Rs 1,20,000 (12-04-2023). Earlier cap Rs 85,000 (24-12-2019)
- F1: The maximum spend on a laptop or tablet for an IAS, IPS or IFS officer is Rs. 120,000, as set by the 2023 GR which superseded the 2019 GR that had Rs. 85,000.
- run1: The maximum spend on a laptop or tablet for an IAS, IPS, or IFS officer is Rs. 120,000, as set by the newer GR dated 12-04-2023 which amended the earlier limit of Rs. 85,000.
- run2: The maximum spend on a laptop or tablet for an IAS, IPS or IFS officer is Rs. 1,20,000, as set by the 2023 GR.

**Q8.** Is the 24 December 2019 laptop corrigendum still in force?  
*Gold:* No. Superseded by the 12-04-2023 corrigendum, which replaces paragraph 1
- F1: The 24 December 2019 laptop corrigendum is not in force because the 12 April 2023 GR supersedes it; the newer GR raises the maximum purchase limit from Rs. 85,000 to Rs. 120,000.
- run1: No, the 24 December 2019 laptop corrigendum is not still in force because a newer GR dated 12-04-2023 superseded it.
- run2: No, the 24 December 2019 laptop corrigendum is not in force because it has been superseded by the 12 April 2023 GR, which also raised the maximum purchase limit to Rs. 120,000.

**Q9.** Show me the 24 February 2015 GR on laptops for officers.  
*Gold:* Not in this corpus. Its paragraph 1 was amended in 2019 and again in 2023 (cap now Rs 1,20,000)
- F1: I couldn't find a GR on this in the corpus (dated 24-02-2015).
- run1: I couldn't find a GR on this in the corpus for 24-02-2015.
- run2: I couldn't find a GR on this in the corpus.

**Q10.** मातंस ३८१४/प्र.क्र.१७४/३९: what is the current limit?  
*Gold:* Rs 1,20,000 (12-04-2023)
- F1: (no answer)
- run1: The current maximum purchase limit is Rs. 120,000, as set by the GR dated 12-04-2023.
- run2: The current limit is Rs. 120,000.

**Q11.** Is the 26 November 2020 GR on the computer qualification certificate in force?  
*Gold:* No. Stayed until further orders by the GR of 27-11-2020, which reinstated the orders under the 20-11-2018 letter
- F1: The 26-11-2020 GR on the computer qualification certificate is stayed by the 27-11-2020 GR, which puts it on hold till further orders and restores the 20-11-2018 letter orders.
- run1: No, the 26 November 2020 GR is not in force because the 27 November 2020 GR stayed it until further orders.
- run2: No newer GR found in this corpus that keeps the 26 November 2020 GR in force; instead, a GR dated 27 November 2020 stayed it till further orders.

**Q12.** Will excess salary be recovered from staff who were late with the computer certificate?  
*Gold:* The recovery order of 26-11-2020 was stayed on 27-11-2020; no newer order in this corpus
- F1: The 26 November 2020 GR (202011261535430611) decided that excess salary paid because increments were not withheld from staff who failed to submit the computer certificate on time should be recovered.
- run1: Yes, the GR dated 26-11-2020 directed that excess salary paid to staff who did not submit the computer qualification certificate within the prescribed time must be recovered.
- run2: Yes, excess salary was to be recovered from staff who were late with the computer certificate, but a later stay order suspended that recovery until further orders.

**Q13.** Is the 2018 empanelment of IT consultants still valid?  
*Gold:* No. It expired 19-03-2023, was extended to 19-09-2023 (24-04-2023), and was replaced by a new empanelment from 20-09-2023 to 19-09-2028 (05-10-2023)
- F1: The 2018 empanelment is no longer valid because the 2023 GR (dated 05-10-2023) states it expired on 19th September 2023 and replaced it with a new 5-year empanelment from 20th September 2023 to 19th September 2028.
- run1: No, the 2018 empanelment is no longer valid.
- run2: No, the 2018 empanelment is not still valid.

**Q14.** From what date do the new IT consultant rates apply?  
*Gold:* 20-09-2023, per the 15-12-2023 clarification (not the 05-10-2023 GR date)
- F1: The new IT consultant rates apply from 20th September 2023, as clarified by the circular dated 15-12-2023.
- run1: The new IT consultant rates apply from 20th September 2023, as clarified by the 15-12-2023 circular and set by the 05-10-2023 GR for work orders issued from its date.
- run2: The new IT consultant rates apply from 20th September 2023, as clarified by the 15-12-2023 circular, and the 2023 GR (dated 05-10-2023) states that its rates apply for all work orders issued from its date of issue.

**Q15.** What is the monthly rate for a Principal Consultant?  
*Gold:* Rs 4,54,000 excluding taxes (05-10-2023). The 2018 rate was Rs 3,24,000
- F1: The monthly rate for a Principal Consultant under the 20-03-2018 GR is INR 3,24,000 per month per person (excluding taxes).
- run1: The monthly rate for a Principal Consultant under the 2018 GR is 3,24,000 INR per month per person (excluding taxes) for >15 years of experience.
- run2: The monthly rate for a Principal Consultant under the 2018 GR was 3,24,000 INR per month (excluding taxes), but the 2023 GR replaced it with a rate of 4,54,000 INR per month (excluding taxes) for consultants with more than 13 years of experience.

**Q16.** What did the 9 May 2019 IT consultant GR say?  
*Gold:* Not in this corpus, though later GRs cite it
- F1: I couldn't find a GR on 9 May 2019 in the corpus.
- run1: I couldn't find a GR on this in the corpus.
- run2: I couldn't find a GR on this in the corpus.

**Q17.** Can a department change the qualifications it asks of empanelled consultants?  
*Gold:* Yes for the profile of personnel, through change orders (RFP 24.19); not the years of experience (05-03-2024)
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 201803201319308011 GR on consultant qualifications.
- run1: Yes, a department can change the qualifications it asks of empanelled consultants by using clauses under Section 24.19 of the RFP (Change Orders) to change the Profile of Personnel required for the engagement, but it cannot change the Years of Experience mentioned in the GR for the Category of resources required for the engagement.
- run2: Yes, a department can change the qualifications it asks of empanelled consultants by altering the profile of personnel through clauses under Section 24.19 of the RFP (Change Orders), but it cannot change the years of experience mentioned in the GR for the category of resources required for the engagement.

**Q18.** Whose concurrence is needed for a consultant's scope of work?  
*Gold:* The department's ACS/PS/Secretary, not DIT (corrigendum 19-03-2021). Not changed by a later GR in this corpus
- F1: According to the Government Resolution dated 20-03-2018, departments need to finalize the scope of work for consultancy with the concurrence of DIT.
- run1: Yes, concurrence is needed for a consultant's scope of work.
- run2: The 2018 GR requires concurrence of DIT to finalize the scope of work for consultancy.

**Q19.** Has the Maha DBT disbursement GR of 12 October 2018 been changed?  
*Gold:* Yes. Paragraphs 8 and 9 amended 30-11-2021. The English and Marathi copies of 12-10-2018 are one GR
- F1: Yes, the Maha DBT disbursement GR of 12-10-2018 has been amended.
- run1: Yes, the Maha DBT disbursement GR of 12-10-2018 has been amended.
- run2: Yes, the Maha DBT disbursement GR of 12 October 2018 has been amended.

**Q20.** Which bank must hold a scheme's Maha DBT Central Pool Account?  
*Gold:* State Bank of India (30-11-2021)
- F1: The 2021 GR amends the 2018 GR to require that each department open its scheme-wise Central Pool Account in State Bank of India, because that bank is linked to both the MahaDBT portal and PFMS.
- run1: The bank that must hold a scheme's Maha DBT Central Pool Account is State Bank of India.
- run2: The State Bank of India must hold a scheme's Maha DBT Central Pool Account.

**Q21.** What rent support does the Fintech policy give start-ups?  
*Gold:* Up to Rs 4 lakh a year for 3 years for early-stage start-ups, added by the addendum of 30-11-2018
- F1: The Fintech policy provides rent reimbursement for early stage Fintech start-ups up to an upper limit of Rs. 4 lakh per year for a total period of 3 years.
- run1: The Fintech policy (Government Resolution DIT-2018/C.R-17/D-1/39 dated 16 February 2018) does not itself contain a rent reimbursement provision in its original text; it is added by the later Government Addendum dated 30 November 2018.
- run2: The Fintech policy gives start-ups rent reimbursement for office space, capped at Rs. 4 Lakh per year for a total period of 3 years, and allows co-working space rent adjustment at source if the co-working site is a partner with Mumbai Fintech Hub.

**Q22.** Did the 30 November 2018 Fintech corrigendum change any benefit?  
*Gold:* No. It only corrects United payments Interface to Unified payment Interface
- F1: The corpus does not contain any newer GR that amends, replaces, stays, extends or clarifies the 30 November 2018 corrigendum (code 201811301240117211).
- run1: I couldn't find a GR on this in the corpus.
- run2: I couldn't find a GR on this in the corpus.

**Q23.** Who represents the National Health Mission on the blockchain health-records working group?  
*Gold:* The Additional Director, NHM (corrigendum 04-10-2019), not the Director
- F1: The National Health Mission is represented by the Additional Mission Director, National Health Mission, Mumbai-1, on the blockchain health-records working group, as clarified by the corrigendum dated 04-10-2019.
- run1: The Additional Mission Director, National Health Mission, Mumbai-1 represents the National Health Mission on the blockchain health-records working group.
- run2: The National Health Mission is represented on the blockchain health-records working group by the Additional Mission Director, National Health Mission, Mumbai-1, as amended by the 04-10-2019 corrigendum.

**Q24.** Did the April 2019 Urban MahaNet GR replace the September 2018 GR?  
*Gold:* No. It adds three items (statewide ROW waiver, smart poles, 5-year total contract); the 2018 GR stands
- F1: The 10-04-2019 GR amends the 28-09-2018 GR rather than replacing it.
- run1: No, the April 2019 Urban MahaNet GR did not replace the September 2018 GR.
- run2: No, the April 2019 Urban MahaNet GR did not replace the September 2018 GR; it amended it.

**Q25.** Find the Urban MahaNet GR of 28 September 2018.  
*Gold:* One GR with English and Marathi copies; later amended 10-04-2019
- F1: The Urban MahaNet GR of 28 September 2018 is code 201809281811031811, titled 'Implementation of Urban MahaNet project and Delivery of E-Governance Services'.
- run1: The Urban MahaNet GR dated 28-09-2018 (code 201809281811031811) was found in the corpus.
- run2: The Urban MahaNet GR dated 28-09-2018 (code 201809281811031811) is found in the corpus.

**Q26.** Within how many days must a department pay MahaIT's Urban MahaNet invoice?  
*Gold:* 15 days from the invoice date (24-12-2018)
- F1: The department or office must pay MahaIT's Urban MahaNet invoice within 15 days from the date of issuance, as per the 24-12-2018 GR.
- run1: A department must pay MahalT's Urban MahaNet invoice within 15 days from the date of invoice issuance.
- run2: Departments must pay MahaIT's Urban MahaNet invoice within 15 days from the date of invoice issuance.

**Q27.** Which university is responsible for the Academic module of the IUMS project?  
*Gold:* S.N.D.T. Women's University (corrigendum 18-04-2019); earlier Dr. Babasaheb Ambedkar Technological University, Lonere (12-12-2018)
- F1: (no answer)
- run1: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project according to the 18-04-2019 GR.
- run2: The S.N.D.T. Women's University, Mumbai is responsible for the Academic module of the IUMS project according to the 18-04-2019 Government Resolution.

**Q28.** Which groups does the Maha-Pariksha GR of 20 February 2020 apply to?  
*Gold:* Group C and Group D. The preamble said Group B and C; the corrigendum of 24-02-2020 corrected it to Group C and D
- F1: The Maha-Pariksha GR of 20-02-2020 applies to Group-B and Group-C category recruitment examinations conducted through the Maha-Pariksha portal in all administrative departments and their subordinate offices of the Government of Maharashtra.
- run1: The Maha-Pariksha GR of 20 February 2020 applies to Group-B and Group-C category posts in all administrative departments and their subordinate offices across the state.
- run2: The Maha-Pariksha GR of 20-02-2020 applies to Group-C and Group-D divisional posts in all administrative departments and their subordinate offices of the Government in the State.

**Q29.** What did the 19 July 2021 corrigendum change in the 6 April 2021 disability-reservation GR?  
*Gold:* It deleted the sentence in para 2 saying senior and junior scientific officer posts were left out because an earlier GR (18-02-2021) covers them. The rest of para 2 is unchanged
- F1: The 19 July 2021 corrigendum removed the sentence in paragraph 2 of the 6 April 2021 GR that had excluded two posts (Senior Scientist/Junior Scientist) at the Rajiv Gandhi Science and Technology Commission from this decision because they were already covered in a prior SE-1 government decision.
- run1: The 19 July 2021 corrigendum deleted the sentence in paragraph 2 of the 6 April 2021 GR that excluded two posts (senior scientist/junior scientist) in the Rajiv Gandhi Science and Technology Commission because they were already covered in an SE-1 GR, thereby including those posts.
- run2: The 19-07-2021 corrigendum amends the 06-04-2021 GR by deleting the exclusion sentence in paragraph 2, so that the two posts of Senior Scientist and Junior Scientist in the Rajiv Gandhi Science and Technology Commission are now included in the disability reservation.

**Q30.** Is the e-Tenders GR of 11 May 2021 still the latest on e-tendering?  
*Gold:* No newer GR found in this corpus (covers 2018 to 2024)
- F1: The asked-for GR dated 11-05-2021 (Implementation of E-Tenders) is not amended, replaced, stayed, extended, or clarified by any newer GR in the corpus.
- run1: I couldn't find a GR on this in the corpus.
- run2: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the e-Tenders GR of 11 May 2021.

**Q31.** Has the model RFP GR of September 2019 been updated?  
*Gold:* No newer GR found in this corpus
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 20-09-2019 Model RFP GR.
- run1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the Maharashtra Model RFP GR of 20-09-2019.
- run2: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the Model RFP GR of 20-09-2019.

**Q32.** What is the latest GR on the State Data Center as critical information infrastructure?  
*Gold:* 05-10-2019; no newer GR found in this corpus
- F1: The latest GR in the corpus on declaring the Maharashtra State Data Center as Critical Information Infrastructure (CII) is dated 05-10-2019 (Government Circular No. H – DIT2019/CR 34/3/39).
- run1: The latest GR in the corpus on the State Data Center as critical information infrastructure is dated 05-10-2019 (GR H – DIT2019/CR 34/3/39), which declares the Maharashtra State Data Center as Critical Information Infrastructure (CII).
- run2: The latest GR in the corpus on the State Data Center as critical information infrastructure is dated 05-10-2019.

**Q33.** What is the latest GR on the Maharashtra Unified Citizen Data Hub?  
*Gold:* 04-02-2022; no newer GR found in this corpus
- F1: I couldn't find a GR on this in the corpus.
- run1: The latest GR on the Maharashtra Unified Citizen Data Hub in the corpus is dated 04-02-202022.
- run2: The latest GR on the Maharashtra Unified Citizen Data Hub in this corpus is dated 04-02-2022.

**Q34.** Is there a GR on a 5G task force, and has it changed?  
*Gold:* 27-03-2023; no newer GR found in this corpus
- F1: No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 5G task force GR (202303301831230311 dated 27-03-2023).
- run1: Yes, there is a GR on a 5G task force in the corpus: GR number मातंसं-११० ९ ०/प्र.क्र .२/२०२० dated 27-03-2023 titled Regarding setting up a task force to launch and implement 5G services in the state.
- run2: Yes, there is a GR on a 5G task force: GR 202303301831230311 dated 27-03-2023, which establishes a task force committee to launch and implement 5G services in the state and defines its members and functions.

**Q35.** What is the latest GR on the Setu Kendra tender process?  
*Gold:* 19-07-2024; no newer GR found in this corpus
- F1: The latest GR on the Setu Kendra tender process is dated 19-07-2024 (code 202407191742379111), titled Regarding the tender process of Setu Kendra in the collector and tehsil offices of the state.....
- run1: The latest GR on the Setu Kendra tender process in the corpus is dated 19-07-2024 (code 202407191742379111).
- run2: The latest GR on the Setu Kendra tender process in this corpus is dated 19-07-2024 and requires all Setu Kendras at district headquarters and tehsil offices to remain operational, with the tender process to be completed within three months where it has expired or centres are closed.

**Q36.** Is the 2022 GR on generative AI use in government offices in force?  
*Gold:* No such 2022 GR in this corpus. Closest: the circular of 03-03-2020 on AI, Marathi language technology and NLP in government work; a good answer names it without claiming it is the GR asked for
- F1: I couldn't find a GR on the use of generative AI in government offices in the corpus.
- run1: I couldn't find a GR on this in the corpus.
- run2: I couldn't find a GR on this in the corpus.

**Q37.** What did the 19 September 2017 Maha-Pariksha GR say?  
*Gold:* Not in this corpus. It was superseded by the GR of 20-02-2020
- F1: I couldn't find a GR on this in the corpus.
- run1: I couldn't find a GR on this in the corpus, because the corpus does not contain the 19 September 2017 Maha-Pariksha GR itself.
- run2: I couldn't find a GR on this in the corpus.

