# Q6: why final run B said a 2021 GR amended the July 2019 GR

**Question:** "What did the July 2019 cloud GR change?"

**Gold:** Added rules on which data moves to cloud, archival and periodic review. No
deadline or amount change. The gold GR is `201907051642210511` (05-07-2019).

**Source:** `runs/2026-11-18-v4-run2.jsonl` (final, run B), Q6. Scored answer 0, citation
pass, latest fail, confident-wrong yes (`eval/scores.csv`).

## What the model said

| | |
|---|---|
| asked_for_code | `201907051642210511` (05-07-2019), the right GR |
| GR named as amending it | `202104231756150811` (23-04-2021), "Cloud Computing policy Empanelment of Cloud Service Providers and Guidelines for Government Organizations" |
| Review entry | effect `amends`, reason: "It changes procurement rules and deadlines for the 2019 cloud GR by shifting to GeM portal and setting expiry dates." |
| newer | 23-04-2021: "It mandates that all departments procure cloud services through the GeM portal, sets the previous empanelment expiry on 30-04-2021, and requires migration to new cloud within 45 days with the empanelment rate expiring on 15-06-2021." |
| Answer (raw) | "The 2021-04-23 GR amends the July 2019 cloud GR by requiring all government departments to procure cloud services through the GeM portal, ending the previous empanelment on 30-04-2021, and mandating migration to a new cloud within 46 days with the empanelment rate expiring on 15-06-2021. Earlier, the July 2019 GR instructed departments to define data for cloud migration in writing and to periodically review applications on cloud for efficiency and cost." |
| Format and checks | Format ok on the first reply. The current-rule check passed (the first sentence states 30-04-2021 and 15-06-2021, both new in the 2021 GR). No retry. |

The second sentence of the answer describes the July 2019 GR correctly. The first sentence
is wrong.

## What the 2021 GR's text says about the July 2019 GR

Nothing. Its full text was given to the model as a candidate block:

- **References ("वाचा"):** six documents, none dated 05-07-2019:
  - Industries Department GR of 24-08-2017 (GeM purchase);
  - DIT/060/3/2017, 29.01.2018;
  - DIT/060/3/2017/1, 16.05.2018;
  - DIT/060/3/2017/2, 19.05.2018;
  - DIT/060/3/2017/3, 04.08.2018;
  - DIT/060/3/2017/3 addendum ("जोडपत्र"), 19.06.2019.
- **Body:** the empanelment and service rates announced under the letter of 16 May 2018 end
  on 30 April 2021. From now on, cloud services are bought on the GeM portal. Departments
  that gave work orders beyond 30 April 2021 must buy through GeM within 45 days and move
  their systems and data. For them, the empanelment rates for ongoing services end on
  15 June 2021.

The July 2019 GR is about which data moves to cloud, archived data, and periodic review.
The 2021 GR doesn't mention any of these.

## Why it was a candidate

The citation graph links the 2021 GR to `201907051642210511` with evidence `order` only.
The 2021 GR is listed as a candidate of the July 2019 GR, and the prompt says "evidence:
order". The match comes from one line of the 2021 GR's **English machine translation**:
"vide letter No.060/3/2017/1, dated 16th May," with the year on the next line. Because the
date was split across lines, the reference was not read as dated. Its file number
`060/3` then matched every GR on that file, including the July 2019 addendum (GR number
`GAD-IT-060/3/2017`).

The 2021 GR's own number is `2021/3/060`, a different key. So the link was labelled
`order`, the second-strongest evidence type, not `same_file`, the weakest, which is
treated as "candidate only".

## Likely cause

Two things together:

1. **Graph:** a split date in the machine translation turned a dated reference to the
   16-05-2018 letter into a bare file-number match. That linked the 2021 GR to every GR on
   file 060/3, and labelled the link more strongly than a shared file number deserves.
2. **Model reading:** with that lead and the 2021 GR's text, the model judged `amends`
   without the text saying anything about the July 2019 GR. In final run A
   (`runs/2026-11-18-v4-run1-2.jsonl`), the same candidate with the same evidence was
   judged `clarifies` ("does not alter the July 2019 cloud hosting instructions"), and Q6
   was scored fully correct. So the outcome varies from run to run.

The current-rule-first check could not catch this. It checks that the first sentence
names the newest change the model listed, not whether that change is real.

No fix has been made.
