# Hold-out test: old vs final engine (20-11-2026)

15 questions (`eval/holdout_questions.jsonl`, ids 101–115), new to the engine. The code and prompts were locked before the runs: nothing in the repository was changed for this test.

**Not scored.** Hand scoring goes in the CSVs (same columns as F1). The CSV columns `model_answer`, `cited`, `newer` and `status` are the raw model output; `checked_*` and `check_corrections` show the product after the checks.

## Runs

| Run | Version | Prompt | Log | CSV | Cost (Rs) |
|---|---|---|---|---|---|
| Old run 1 | `835367c` | answer_v2 | `runs/2026-11-20-holdout-old-run1.jsonl` | `runs/2026-11-20-holdout-old-run1.csv` | 1.94 |
| Old run 2 | `835367c` | answer_v2 | `runs/2026-11-20-holdout-old-run2.jsonl` | `runs/2026-11-20-holdout-old-run2.csv` | 0.44 |
| Final run 1 | `49ee4ae` | answer_v4 | `runs/2026-11-20-holdout-final-run1.jsonl` | `runs/2026-11-20-holdout-final-run1.csv` | 2.36 |
| Final run 2 | `49ee4ae` | answer_v4 | `runs/2026-11-20-holdout-final-run2.jsonl` | `runs/2026-11-20-holdout-final-run2.csv` | 0.55 |

Total spend: **Rs 5.29** (cap Rs 15). Same model and settings in both versions: sarvam-105b, `/v1/chat/completions`, JSON mode, temperature 0.2, max_tokens 4096, reasoning_effort "low".

**How the runs were made.**
- The old version ran from a git worktree at `835367c`, with its own code and prompts.
- The final version ran from the `engine-v1` checkout at `49ee4ae`.
- Both used the same corpus index, which is unchanged between the two commits.
- A driver script outside the repository redirected three module constants: the question file, the run directory, and the spend ledger (shared, so the Rs 15 cap covered all four runs). No repository code was changed.
- Run order: old 1, final 1, old 2, final 2. Second runs are cheaper because of prompt caching.

## Format status per run

| Run | ok | retried_ok | repaired | failed | product answer shown |
|---|---|---|---|---|---|
| Old run 1 | 13 | 1 | 0 | 1 | 14/15 |
| Old run 2 | 12 | 2 | 0 | 1 | 14/15 |
| Final run 1 | 13 | 1 | 0 | 1 | 15/15 |
| Final run 2 | 12 | 3 | 0 | 0 | 15/15 |

| Q | Old run 1 | Old run 2 | Final run 1 | Final run 2 |
|---|---|---|---|---|
| 101 | ok | ok | ok | ok |
| 102 | ok | ok | ok | ok |
| 103 | ok | ok | ok | ok |
| 104 | ok | retried_ok | ok | ok |
| 105 | ok | failed (no product answer) | ok | ok |
| 106 | ok | ok | failed (format repaired, shown) | ok |
| 107 | ok | ok | ok | ok |
| 108 | ok | ok | ok | ok |
| 109 | ok | ok | ok | retried_ok |
| 110 | ok | ok | ok | ok |
| 111 | failed (no product answer) | ok | ok | ok |
| 112 | ok | ok | ok | ok |
| 113 | retried_ok | retried_ok | retried_ok | retried_ok |
| 114 | ok | ok | ok | ok |
| 115 | ok | ok | ok | retried_ok |

- **Old version:** a format failure leaves the product blank.
- **Final version:** a format failure is shown as a format-repaired answer.

## Old-vs-current questions (101–107)

Each of these has an earlier rule and a later GR that changes it. The table shows the first sentence of each raw answer (current rule first?) and whether the newest gold GR appears in the raw cited or newer list. The full raw answers are in the next section.

### Q101 (AM, MR): Who is the Member Secretary of the Rajiv Gandhi Science and Technology Commission?

**Gold:** Shri Narendra Shah, retired professor, IIT Bombay, appointed by the GR of 02-11-2021. Earlier Shri Anil Shrikrishna Manekar (GR of 19-07-2019), who asked to be relieved before his term ended  
**Gold GRs:** 19-07-2019 `201907191239438711`, 02-11-2021 `202111021709449611`

Newest gold GR: 02-11-2021 `202111021709449611`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 2019 GR appointed Shri. A.S. Manekar as Member Secretary of the Rajiv Gandhi Science and Technology Commission. | yes | 02-11-2021 `202111021709449611`: Replaces the 2019 Member Secretary appointment by appointing Narendra Shah as Member Secretary, superseding Shri. A.S. Manekar. |
| Old run 2 | ok | answered | The Member Secretary of the Rajiv Gandhi Science and Technology Commission is Shri Narendra Shah, retired Professor from the Indian Institute of Technology, Mumbai, as appointed under the GR dated 02-11-2021. | yes | 02-11-2021 `202111021709449611`: Replaced Anil Shrikrishna Manekar with Narendra Shah as Member Secretary, Rajiv Gandhi Science and Technology Commission. |
| Final run 1 | ok | answered | The Member Secretary is Shri Narendra Shah, retired Professor from IIT Mumbai, as appointed by the 02-11-2021 GR. | yes | 02-11-2021 `202111021709449611`: Replaced Shri Anil Shrikrishna Manekar with Shri Narendra Shah, retired Professor from IIT Mumbai, as Member Secretary. |
| Final run 2 | ok | answered | The Member Secretary of the Rajiv Gandhi Science and Technology Commission is Shri Narendra Shah, appointed on 02-11-2021. | yes | 02-11-2021 `202111021709449611`: Appointed Narendra Shah as Member Secretary, replacing the previous appointee Anil Shrikrishna Manekar. |

### Q102 (AM, MR): Is the 20 July 2021 seniority list of Assistant (Technical) staff in the Directorate of IT final?

**Gold:** No. It was provisional (objections invited within 15 days). The final seniority list was published by the circular of 03-09-2021  
**Gold GRs:** 20-07-2021 `202107201251572411`, 03-09-2021 `202109031145424411`

Newest gold GR: 03-09-2021 `202109031145424411`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 20-07-2021 GR published a temporary seniority list and invited objections within 15 days. | yes | - |
| Old run 2 | ok | answered | The 20 July 2021 temporary seniority list was superseded by the 3 September 2021 GR, which finalised and published the common seniority list as final. | yes | - |
| Final run 1 | ok | answered | No, the 20 July 2021 seniority list was temporary, not final. | no | - |
| Final run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that changes the 20-07-2021 temporary seniority list. | yes | - |

### Q103 (AM, MR): How does a company apply for permission to put up a mobile tower or lay optical fibre in Maharashtra?

**Gold:** Fresh applications go through the GatiShakti Sanchar portal (gatishaktisanchar.gov.in), per the telecom infrastructure policy GR of 04-11-2022 (forest department applications excepted; regularisation of existing infrastructure through the Mahasanchar portal). Earlier, the 03-03-2018 circular had applications filed in hard copy with local authorities until the DGIT single-window portal was ready  
**Gold GRs:** 03-03-2018 `201803031333271711`, 04-11-2022 `202211041809363311`

Newest gold GR: 04-11-2022 `202211041809363311`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | not_found | I couldn't find a GR on this in the corpus. | no | - |
| Old run 2 | ok | not_found | The 2018 GR (03-03-2018) states that until the online single-window portal is activated, applicants must submit hard-copy applications to the concerned local authorities for telecom towers, micro cells, masts, base stations, and optical fibre cable, and these must be processed according to the policy dated 17.02.2018. | no | - |
| Final run 1 | ok | answered | A company applies for permission to put up a mobile tower or lay optical fibre through the GatiShakti Sanchar Portal for new applications, and through the Mahasanchar Portal for regularization, as per the Telecom Infrastructure Policy dated 04-11-2022. | yes | - |
| Final run 2 | ok | answered | A company must apply in hard copy form to the concerned competent authority for permission to put up a mobile tower or lay optical fibre cable until the online single window portal is activated, and a copy must be sent by email to mahatip@maharashtra.gov.in. | no | - |

### Q104 (AM, MR): Which GR sets MahaIT's current rates for supplying technical manpower to departments?

**Gold:** The GR of 22-04-2020, with rates for 01-04-2020 to 31-03-2021: the latest in this corpus. It follows the rate GRs for 2018-19 (03-04-2018) and 2019-20 (09-04-2019). No newer rate GR in this corpus  
**Gold GRs:** 03-04-2018 `201804031521270211`, 09-04-2019 `201904091114390811`, 22-04-2020 `202004221243514111`

Newest gold GR: 22-04-2020 `202004221243514111`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The current rates for supplying technical manpower to departments are set by the 22-04-2020 GR (202004221243514111), which fixes rates for 01/04/2020 to 31/03/2021 via an annexure; earlier GRs set rates for 2018-19 and 2019-20. | yes | 22-04-2020 `2020042212439514111`: Sets rates for 01/04/2020 to 31/03/2021 via annexure and requires work orders per availability under Annexure-1 agreement.; 09-04-2019 `201904091114390811`: Sets rates for 01/04/2019 to 31/03/2020 via annexure and requires work orders per availability under Annexure-1 agreement. |
| Old run 2 | retried_ok | answered | The GR dated 03-04-2018 (code 201804031521270211) originally set the rates for supplying technical manpower from 01/04/2018 to 31/03/2019 as per the attached Annexure. | no | 09-04-2019 `201904091114390811`: Added a conditional clause that Maharashtra IT Corporation shall issue work orders as per the availability of technical manpower of institutions mentioned in Annexure-I as per the agreement with supplying agencies.; 22-04-2020 `202004221243510111`: Added a conditional clause that Maharashtra IT Corporation shall issue work orders as per the availability of technical manpower of institutions mentioned in Annexure-I as per the agreement with supplying agencies. |
| Final run 1 | ok | answered | The current rate-setting GR is the one dated 22-04-2020, which establishes the rates for technical manpower supplied by MahaIT for the period 01/04/2020 to 31/03/2021 as per its attached annexure. | yes | 22-04-2020 `202004221243514111`: Supersedes the 2018 GR for the period 01/04/2020 to 31/03/2021, maintaining the annexure-based rate structure with an added condition that work orders must follow agency availability per Annexure-I.; 09-04-2019 `201904091114390811`: Supersedes the 2018 GR for the period 01/04/2019 to 31/03/2020, maintaining the annexure-based rate structure with an added condition that work orders must follow agency availability per Annexure-I. |
| Final run 2 | ok | answered | The current rates for supplying technical manpower are set by the GR dated 22-04-2020 (code 202004221243514111), which fixes rates for 01/04/2020 to 31/03/2021 as per the attached appendix. | yes | 09-04-2019 `201904091114390811`: Set technical manpower rates (excluding tax) for 01/04/2019 to 31/03/2020 as per the attached appendix, and added that work orders must be issued according to the availability of technical manpower of institutions mentioned in Annexure-1 as per the agreement with supplying agencies.; 22-04-2020 `202004221243514111`: Set technical manpower rates (excluding tax) for 01/04/2020 to 31/03/2021 as per the attached appendix, and added that work orders must be issued according to the availability of technical manpower of institutions mentioned in Annexure-1 as per the agreement with supplying agencies. |

### Q105 (AM, MR): From what date must ministry departments run their work on the e-office system?

**Gold:** From 01-04-2023, per the standard operating procedure circular of 23-02-2023 (which cites a circular of 02-02-2023 not in this corpus). The 2020 mahaeoffice GR and SOP (19-10-2020, 09-11-2020) came earlier  
**Gold GRs:** 23-02-2023 `202302231826565311`, 19-10-2020 `202010191540488111`, 09-11-2020 `202011091654026811`

Newest gold GR: 23-02-2023 `202302231826565311`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 19-10-2020 GR directs that the mahaeoffice web-based system must be implemented immediately in all ministerial departments. | yes | - |
| Old run 2 | failed | answered | Based on the GR dated 19-10-2020, ministry departments must run their work on the e-office system from 01-11-2020, when e-dharika is to be fully operationalized in the first phase by the listed departments. | no | - |
| Final run 1 | ok | answered | The 2020-10-19 GR mandates that all ministry departments run their work on the e-office system from 01-11-2020. | no | - |
| Final run 2 | ok | answered | Ministry departments must run their work on the e-office system from 01-11-2020. | no | 09-11-2020 `202011091654026811`: It fixes the SOP for e-office implementation in the Ministry, referencing the 19-10-2020 GR, but does not alter the 01-11-2020 start date for e-tpal/e-rja or e-Dharika. |

### Q106 (AM, MR): Is Nyas Communication Pvt. Ltd. an empanelled OMR vendor for Maha-Pariksha recruitment?

**Gold:** Yes. It was not in the list in the GR of 21-01-2021; it was added by the supplement of 04-03-2021, after MahaIT heard the company and verified its documents following a High Court decision  
**Gold GRs:** 21-01-2021 `202101211644450911`, 04-03-2021 `202103041719472911`

Newest gold GR: 04-03-2021 `202103041719472911`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | Yes, based on GR 202103041719472911 dated 04-03-2021, Me. Nyas Communication Pvt. Ltd. is empanelled as the 5th OMR Vendor for Maha-Pariksha recruitment, and the earlier GR dated 21-01-2021 remains in force. | yes | 04-03-2021 `202103041719472911`: It adds Me. Nyas Communication Pvt. Ltd. as the 5th OMR Vendor in the empanelment list for Maha-Pariksha recruitment and specifies its registration fee rate of Rs. 210.04 per candidate. |
| Old run 2 | ok | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment. | yes | - |
| Final run 1 | failed | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment. | yes | 21-01-2021 `202101211644450911`: Established the initial panel of four OMR vendors (Aptech, GA Software, Ginger Webs, Meta-I Technologies) for Group-B and Group-C recruitment under Maha-Pariksha, without Nyas Communication Pvt. Ltd. |
| Final run 2 | ok | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment as of the 04-03-2021 GR, which added it as the fifth vendor to the panel listed in the 21-01-2021 GR. | yes | 04-03-2021 `202103041719472911`: Added Nyas Communication Pvt. Ltd. as the fifth OMR vendor on the empanelment list, while the earlier four vendors remained; the rates stayed the same. |

### Q107 (ST, EN,MR): Is Amazon Web Services an empanelled cloud service provider for Maharashtra government departments?

**Gold:** Not any more. It was empanelled as a Tier-1 provider from 01-05-2018 to 30-04-2021 (circulars of 19-05-2018 and 04-08-2018), but the empanelment ended on 30-04-2021 and departments were told to buy cloud services through GeM (23-04-2021)  
**Gold GRs:** 19-05-2018 `201805211415360511`, 04-08-2018 `201808041826435611`, 23-04-2021 `202104231756150811`

Newest gold GR: 23-04-2021 `202104231756150811`. The column "newest gold GR in raw cited/newer" is an automatic fact, not a score.

| Run | Format | Status | First sentence (raw) | Newest gold GR in raw cited/newer | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | Yes, Amazon Web Services is listed as a Tier-1 empanelled Cloud Service Provider (CSP) in the GR dated 19-05-2018, under the name Amazon Web Services (AISPL). | no | - |
| Old run 2 | ok | answered | Yes, Amazon Web Services (AISPL) is listed as a Tier-1 empanelled Cloud Service Provider in the GR dated 19-05-2018 (060/3/2017/2). | no | - |
| Final run 1 | ok | answered | Yes, Amazon Web Services (AISPL) is empanelled as a Tier-1 cloud service provider. | yes | 23-04-2021 `202104231756150811`: The previous empanelment and rates under DIT/060/3/2017/1 dated 16.05.2018 (which included the 19-05-2018 GR) are terminated as of 30.04.2021, and all government departments must procure cloud services through the GeM portal instead. |
| Final run 2 | ok | answered | Yes, as of 19-05-2018 Amazon Web Services (AISPL) was empanelled as a Tier-1 cloud service provider for Maharashtra government departments. | yes | 23-04-2021 `202104231756150811`: The empanelment and announced rates under the 2018 GR ended on 30 April 2021; departments must now procure cloud services via the GeM portal. The specific Tier-1/Tier-2 CSP list including Amazon Web Services is no longer valid for new procurements after that date. |

## Raw answers side by side (all 15)

Raw model output (before the post-answer checks), for each run.

### Q101 (AM, MR): Who is the Member Secretary of the Rajiv Gandhi Science and Technology Commission?

**Gold:** Shri Narendra Shah, retired professor, IIT Bombay, appointed by the GR of 02-11-2021. Earlier Shri Anil Shrikrishna Manekar (GR of 19-07-2019), who asked to be relieved before his term ended  
**Gold GRs:** 19-07-2019 `201907191239438711`, 02-11-2021 `202111021709449611`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 2019 GR appointed Shri. A.S. Manekar as Member Secretary of the Rajiv Gandhi Science and Technology Commission. The 2021 GR replaced him by appointing Shri. Narendra Shah to that post. No newer GR in the corpus amends, extends, or clarifies the 2019 GR beyond this replacement. | 19-07-2019 `201907191239438711` p1 | 02-11-2021 `202111021709449611`: Replaces the 2019 Member Secretary appointment by appointing Narendra Shah as Member Secretary, superseding Shri. A.S. Manekar. |
| Old run 2 | ok | answered | The Member Secretary of the Rajiv Gandhi Science and Technology Commission is Shri Narendra Shah, retired Professor from the Indian Institute of Technology, Mumbai, as appointed under the GR dated 02-11-2021. The earlier appointment of Shri Anil Shrikrishna Manekar under the 2019 GR was replaced by this 2021 appointment. | 19-07-2019 `201907191239438711` p1; 02-11-2021 `202111021709449611` p1 | 02-11-2021 `202111021709449611`: Replaced Anil Shrikrishna Manekar with Narendra Shah as Member Secretary, Rajiv Gandhi Science and Technology Commission. |
| Final run 1 | ok | answered | The Member Secretary is Shri Narendra Shah, retired Professor from IIT Mumbai, as appointed by the 02-11-2021 GR. Earlier, the 19-07-2019 GR had appointed Shri Anil Shrikrishna Manekar to the post. | 19-07-2019 `201907191239438711` p1; 02-11-2021 `202111021709449611` p1 | 02-11-2021 `202111021709449611`: Replaced Shri Anil Shrikrishna Manekar with Shri Narendra Shah, retired Professor from IIT Mumbai, as Member Secretary. |
| Final run 2 | ok | answered | The Member Secretary of the Rajiv Gandhi Science and Technology Commission is Shri Narendra Shah, appointed on 02-11-2021. Earlier, Shri Anil Shrikrishna Manekar was appointed as Member Secretary on 19-07-2019. | 19-07-2019 `201907191239438711` p1; 02-11-2021 `202111021709449611` p1 | 02-11-2021 `202111021709449611`: Appointed Narendra Shah as Member Secretary, replacing the previous appointee Anil Shrikrishna Manekar. |

### Q102 (AM, MR): Is the 20 July 2021 seniority list of Assistant (Technical) staff in the Directorate of IT final?

**Gold:** No. It was provisional (objections invited within 15 days). The final seniority list was published by the circular of 03-09-2021  
**Gold GRs:** 20-07-2021 `202107201251572411`, 03-09-2021 `202109031145424411`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 20-07-2021 GR published a temporary seniority list and invited objections within 15 days. The 03-09-2021 GR replaced it by publishing the final seniority list for the same period, and directed employees to obtain a copy from the website. No newer GR in the corpus changes this final list. | 20-07-2021 `202107201251572411` p1; 03-09-2021 `202109031145424411` p1; 03-09-2021 `202109031145424411` p1 | - |
| Old run 2 | ok | answered | The 20 July 2021 temporary seniority list was superseded by the 3 September 2021 GR, which finalised and published the common seniority list as final. Therefore, the 20 July 2021 list is no longer final. | 20-07-2021 `202107201251572411` p1; 03-09-2021 `202109031145424411` p1 | - |
| Final run 1 | ok | answered | No, the 20 July 2021 seniority list was temporary, not final. A later GR dated 03-09-2021 converted it into the final seniority list. | 20-07-2021 `20210720120572411` p1 | - |
| Final run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that changes the 20-07-2021 temporary seniority list. Earlier, the 20-07-2021 GR published the temporary seniority list and allowed objections within 15 days. The 03-09-2021 GR published the final seniority list based on the same period. | 20-07-2011 `202107201251572411` p1; 03-09-2021 `202109031145424411` p1 | - |

### Q103 (AM, MR): How does a company apply for permission to put up a mobile tower or lay optical fibre in Maharashtra?

**Gold:** Fresh applications go through the GatiShakti Sanchar portal (gatishaktisanchar.gov.in), per the telecom infrastructure policy GR of 04-11-2022 (forest department applications excepted; regularisation of existing infrastructure through the Mahasanchar portal). Earlier, the 03-03-2018 circular had applications filed in hard copy with local authorities until the DGIT single-window portal was ready  
**Gold GRs:** 03-03-2018 `201803031333271711`, 04-11-2022 `202211041809363311`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | not_found | I couldn't find a GR on this in the corpus. The 2019 GR (08-07-2019, Inclusion of IP-1 Institutions in Telecom Infrastructure Policy) cites the missing 2018 GR (03-03-2018) in its preamble, stating that the 2018 GR fixed the policy for construction and maintenance of telecommunication infrastructure and that applications were to be accepted in hard-copy form until the online portal became active. | - | - |
| Old run 2 | ok | not_found | The 2018 GR (03-03-2018) states that until the online single-window portal is activated, applicants must submit hard-copy applications to the concerned local authorities for telecom towers, micro cells, masts, base stations, and optical fibre cable, and these must be processed according to the policy dated 17.02.2018. A copy should also be sent by email to mahatip@maharashtra.gov.in. I couldn't find a GR on this in the corpus. | - | - |
| Final run 1 | ok | answered | A company applies for permission to put up a mobile tower or lay optical fibre through the GatiShakti Sanchar Portal for new applications, and through the Mahasanchar Portal for regularization, as per the Telecom Infrastructure Policy dated 04-11-2022. Earlier, applications were to be submitted in hard copy to local authorities until the online portal became operational, under the 2018 policy dated 03-03-2018. No newer GR in the corpus changes this procedure. | 04-11-2022 `202211041809363311` p1; 04-11-2022 `202211041809363311` p2; 04-11-2022 `202211041809363311` p2 | - |
| Final run 2 | ok | answered | A company must apply in hard copy form to the concerned competent authority for permission to put up a mobile tower or lay optical fibre cable until the online single window portal is activated, and a copy must be sent by email to mahatip@maharashtra.gov.in. Earlier, the policy dated 17.02.2018 governed the permission process. | 03-03-2018 `201803031333271711` p1 | - |

### Q104 (AM, MR): Which GR sets MahaIT's current rates for supplying technical manpower to departments?

**Gold:** The GR of 22-04-2020, with rates for 01-04-2020 to 31-03-2021: the latest in this corpus. It follows the rate GRs for 2018-19 (03-04-2018) and 2019-20 (09-04-2019). No newer rate GR in this corpus  
**Gold GRs:** 03-04-2018 `201804031521270211`, 09-04-2019 `201904091114390811`, 22-04-2020 `202004221243514111`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The current rates for supplying technical manpower to departments are set by the 22-04-2020 GR (202004221243514111), which fixes rates for 01/04/2020 to 31/03/2021 via an annexure; earlier GRs set rates for 2018-19 and 2019-20. No later GR in the corpus amends these current rates. | 03-04-2018 `201804031521270211` p1; 09-04-2019 `201904091114390811` p1; 22-04-2020 `202004221243514111` p1 | 22-04-2020 `2020042212439514111`: Sets rates for 01/04/2020 to 31/03/2021 via annexure and requires work orders per availability under Annexure-1 agreement.; 09-04-2019 `201904091114390811`: Sets rates for 01/04/2019 to 31/03/2020 via annexure and requires work orders per availability under Annexure-1 agreement. |
| Old run 2 | retried_ok | answered | The GR dated 03-04-2018 (code 201804031521270211) originally set the rates for supplying technical manpower from 01/04/2018 to 31/03/2019 as per the attached Annexure. Later GRs in 2019 and 2020 amended this by adding a condition that Maharashtra IT Corporation shall issue work orders based on the availability of technical manpower of institutions mentioned in Annexure-I as per the agreement with supplying agencies. | 03-04-2018 `201804031521270211` p1 | 09-04-2019 `201904091114390811`: Added a conditional clause that Maharashtra IT Corporation shall issue work orders as per the availability of technical manpower of institutions mentioned in Annexure-I as per the agreement with supplying agencies.; 22-04-2020 `202004221243510111`: Added a conditional clause that Maharashtra IT Corporation shall issue work orders as per the availability of technical manpower of institutions mentioned in Annexure-I as per the agreement with supplying agencies. |
| Final run 1 | ok | answered | The current rate-setting GR is the one dated 22-04-2020, which establishes the rates for technical manpower supplied by MahaIT for the period 01/04/2020 to 31/03/2021 as per its attached annexure. Earlier, the GR dated 03-04-2018 set the rates for 01/04/2018 to 31/03/2019 as per its attached annexure. | 03-04-2018 `201804031521270211` p1 | 22-04-2020 `202004221243514111`: Supersedes the 2018 GR for the period 01/04/2020 to 31/03/2021, maintaining the annexure-based rate structure with an added condition that work orders must follow agency availability per Annexure-I.; 09-04-2019 `201904091114390811`: Supersedes the 2018 GR for the period 01/04/2019 to 31/03/2020, maintaining the annexure-based rate structure with an added condition that work orders must follow agency availability per Annexure-I. |
| Final run 2 | ok | answered | The current rates for supplying technical manpower are set by the GR dated 22-04-2020 (code 202004221243514111), which fixes rates for 01/04/2020 to 31/03/2021 as per the attached appendix. Earlier, the GR dated 03-04-2018 (code 201804031521270211) set rates for 01/04/2018 to 31/03/2019 as per its attached appendix. | 03-04-2018 `201804031521270211` p1 | 09-04-2019 `201904091114390811`: Set technical manpower rates (excluding tax) for 01/04/2019 to 31/03/2020 as per the attached appendix, and added that work orders must be issued according to the availability of technical manpower of institutions mentioned in Annexure-1 as per the agreement with supplying agencies.; 22-04-2020 `202004221243514111`: Set technical manpower rates (excluding tax) for 01/04/2020 to 31/03/2021 as per the attached appendix, and added that work orders must be issued according to the availability of technical manpower of institutions mentioned in Annexure-1 as per the agreement with supplying agencies. |

### Q105 (AM, MR): From what date must ministry departments run their work on the e-office system?

**Gold:** From 01-04-2023, per the standard operating procedure circular of 23-02-2023 (which cites a circular of 02-02-2023 not in this corpus). The 2020 mahaeoffice GR and SOP (19-10-2020, 09-11-2020) came earlier  
**Gold GRs:** 23-02-2023 `202302231826565311`, 19-10-2020 `202010191540488111`, 09-11-2020 `202011091654026811`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 19-10-2020 GR directs that the mahaeoffice web-based system must be implemented immediately in all ministerial departments. It further mandates that from 01-11-2020, e-Dharika must be fully operationalised in the listed ministerial departments, and thereafter all ministerial departments must start using the e-office system in a phased manner. The 09-11-2020 GR fixes the SOP for this implementation but does not state a new compliance date for ministry departments. The 23-02-2023 GR states that e-office system use must be made effective from 01-04-2023 in all ministry administrative departments and regional offices, and that e-postal/e-holidays must be sent through e-office from that date, with physical mail sent only by hand where e-office is not possible. No newer GR in the corpus amends, replaces, stays, extends or clarifies the 19-10-2020 GR; the 2023 GR concerns SOP procedure rather than the original directive date. | 19-10-2020 `202010191540488111` p2; 19-10-2020 `202010191540488111` p2; 19-10-2020 `20201019154040488111` p2; 23-02-2023 `202302231826565311` p1; 2023-02-23 `202302231826565311` p1 | - |
| Old run 2 | failed | answered | Based on the GR dated 19-10-2020, ministry departments must run their work on the e-office system from 01-11-2020, when e-dharika is to be fully operationalized in the first phase by the listed departments. | 19-10-2020 `202010191540488111` p2; 19-10-2020 `202010191540488111` p2 | - |
| Final run 1 | ok | answered | The 2020-10-19 GR mandates that all ministry departments run their work on the e-office system from 01-11-2020. The later SOP GR of 09-11-2020 clarifies the procedure but does not alter that date. Earlier, the 2020-10-19 GR listed specific departments for the first phase and required e-post/e-holidays from 1.11.2020, while the ministry e-office system was to be fully implemented in phased manner thereafter. | 19-10-2020 `202010191540488111` p2; 09-11-2020 `202011091654026811` p1 | - |
| Final run 2 | ok | answered | Ministry departments must run their work on the e-office system from 01-11-2020. The 09-11-2020 GR fixed the SOP for this but did not change the start date. Earlier, the 19-10-2020 GR directed all ministries to implement the NIC e-office system immediately and start e-tpal/e-rja from 01-11-2020, with e-Dharika to begin in phases from 01-11-2020. | 19-10-2020 `202010191540488111` p2; 09-11-2020 `202011091654026811` p1 | 09-11-2020 `202011091654026811`: It fixes the SOP for e-office implementation in the Ministry, referencing the 19-10-2020 GR, but does not alter the 01-11-2020 start date for e-tpal/e-rja or e-Dharika. |

### Q106 (AM, MR): Is Nyas Communication Pvt. Ltd. an empanelled OMR vendor for Maha-Pariksha recruitment?

**Gold:** Yes. It was not in the list in the GR of 21-01-2021; it was added by the supplement of 04-03-2021, after MahaIT heard the company and verified its documents following a High Court decision  
**Gold GRs:** 21-01-2021 `202101211644450911`, 04-03-2021 `202103041719472911`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | Yes, based on GR 202103041719472911 dated 04-03-2021, Me. Nyas Communication Pvt. Ltd. is empanelled as the 5th OMR Vendor for Maha-Pariksha recruitment, and the earlier GR dated 21-01-2021 remains in force. | 04-03-2021 `202103041719472911` p2; 04-03-2021 `202103041719472911` p2 | 04-03-2021 `202103041719472911`: It adds Me. Nyas Communication Pvt. Ltd. as the 5th OMR Vendor in the empanelment list for Maha-Pariksha recruitment and specifies its registration fee rate of Rs. 210.04 per candidate. |
| Old run 2 | ok | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment. The 04-03-2021 GR states that MahaIT proposed to include Nyas Communication Pvt. Ltd. at number five in the approved vendor list and that the company is being appointed on the government empanelment. | 21-01-2021 `2021030417194450911` p1; 21-01-2021 `2021030417194450911` p1; 04-03-2021 `202103041719472911` p2 | - |
| Final run 1 | failed | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment. According to the GR dated 04-03-2021, MahaIT found the company eligible after a hearing and verification of documents, and it was appointed on the government empanelment as the fifth OMR vendor at the rate of Rs. 210.04 per candidate (including GST). Earlier, the GR dated 21-01-2021 had appointed only four vendors and did not include Nyas Communication Pvt. Ltd. | 04-03-2021 `202103041719472911` p1; 04-03-2021 `202103041719472911` p2; 04-03-2021 `202103041719472911` p2; 21-01-2021 `202101211644450911` p2 | 21-01-2021 `202101211644450911`: Established the initial panel of four OMR vendors (Aptech, GA Software, Ginger Webs, Meta-I Technologies) for Group-B and Group-C recruitment under Maha-Pariksha, without Nyas Communication Pvt. Ltd. |
| Final run 2 | ok | answered | Yes, Nyas Communication Pvt. Ltd. is an empanelled OMR vendor for Maha-Pariksha recruitment as of the 04-03-2021 GR, which added it as the fifth vendor to the panel listed in the 21-01-2021 GR. Earlier, the 21-01-2021 GR had only four vendors on the panel. | 21-01-2021 `202101211644450911` p2; 04-03-2021 `202103041719472911` p2 | 04-03-2021 `202103041719472911`: Added Nyas Communication Pvt. Ltd. as the fifth OMR vendor on the empanelment list, while the earlier four vendors remained; the rates stayed the same. |

### Q107 (ST, EN,MR): Is Amazon Web Services an empanelled cloud service provider for Maharashtra government departments?

**Gold:** Not any more. It was empanelled as a Tier-1 provider from 01-05-2018 to 30-04-2021 (circulars of 19-05-2018 and 04-08-2018), but the empanelment ended on 30-04-2021 and departments were told to buy cloud services through GeM (23-04-2021)  
**Gold GRs:** 19-05-2018 `201805211415360511`, 04-08-2018 `201808041826435611`, 23-04-2021 `202104231756150811`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | Yes, Amazon Web Services is listed as a Tier-1 empanelled Cloud Service Provider (CSP) in the GR dated 19-05-2018, under the name Amazon Web Services (AISPL). Tier-1 empanelment for Amazon Web Services (AISPL) is valid for the period from 1.5.2018 till 30.4.2021. | 19-05-2018 `201805211415360511` p1 | - |
| Old run 2 | ok | answered | Yes, Amazon Web Services (AISPL) is listed as a Tier-1 empanelled Cloud Service Provider in the GR dated 19-05-2018 (060/3/2017/2). The same GR also lists its Managed Service Providers as M/s Orient Technologies Pvt Ltd and Mahaonline, and notes conditional empanelment for Sec-A of Annexure 8.1, 8.2 and 8.3 only. | 19-05-2018 `201805211415360511` p1 | - |
| Final run 1 | ok | answered | Yes, Amazon Web Services (AISPL) is empanelled as a Tier-1 cloud service provider. Earlier, under GR 201805211415360511 dated 19-05-2018, it was listed among Tier-1 empanelled CSPs, but as per GR 202104231756150811 dated 23-04-2021, that empanelment ended on 30-04-2021 and cloud services must now be procured via the GeM portal. | 19-05-2018 `201805211415360511` p1 | 23-04-2021 `202104231756150811`: The previous empanelment and rates under DIT/060/3/2017/1 dated 16.05.2018 (which included the 19-05-2018 GR) are terminated as of 30.04.2021, and all government departments must procure cloud services through the GeM portal instead. |
| Final run 2 | ok | answered | Yes, as of 19-05-2018 Amazon Web Services (AISPL) was empanelled as a Tier-1 cloud service provider for Maharashtra government departments. However, the 2021 GR states that the empanelment and rates ended on 30-04-2021, and all cloud services must now be procured through the GeM portal, so the prior empanelment is no longer in force for new procurements. | 19-05-2018 `201805211415360511` p1 | 23-04-2021 `202104231756150811`: The empanelment and announced rates under the 2018 GR ended on 30 April 2021; departments must now procure cloud services via the GeM portal. The specific Tier-1/Tier-2 CSP list including Amazon Web Services is no longer valid for new procurements after that date. |

### Q108 (AM, EN): Have the contact details of the IT consultancy firms empanelled in October 2023 changed?

**Gold:** Yes. The circular of 27-10-2023 modified the firms' contact details in Annexure 1 of the GR of 05-10-2023  
**Gold GRs:** 05-10-2023 `202310041905383211`, 27-10-2023 `202310271649358711`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 27-10-2023 GR states that the contact details of the empanelled firms were modified as per Annexure 1. No newer GR in the corpus amends, replaces, stays, extends, or clarifies those contact details. | 27-10-2023 `202310271649358711` p1 | - |
| Old run 2 | ok | answered | The 2023-10-27 GR itself states that the contact details of the empanelled firms are being modified as mentioned in Annexure 1 below. No newer GR in this corpus amends, replaces, extends, or clarifies that GR. | 27-10-2023 `202310271649358711` p1 | - |
| Final run 1 | ok | answered | Yes, the contact details of the IT consultancy firms empanelled in October 2023 were changed. The GR dated 27-10-2023 explicitly states that the contact details of the empanelled firms (Annexure 1) of the above referred GR are being modified as mentioned in Annexure 1 below. Earlier, the 05-10-2023 GR listed the contact details of the empaneled firms in Annexure 1. | 27-10-2023 `202310271649358711` p1; 05-10-2023 `202310041905383211` p1 | - |
| Final run 2 | ok | answered | Yes, the contact details of the IT consultancy firms empanelled in October 2023 were changed. The GR dated 27-10-2023 (202310271649358711) states that the contact details of the empanelled firms (Annexure 1) are being modified as mentioned in Annexure 1 below. | 27-10-2023 `202310271649358711` p1 | - |

### Q109 (CO, MR): Did the 14 May 2021 GR change the Maha DBT disbursement process?

**Gold:** No. It reconstitutes the state-level DBT Working Committee (first set up by a GR of 16-09-2016 not in this corpus). The disbursement process of 12-10-2018 was amended only by the GR of 30-11-2021 (paragraphs 8 and 9)  
**Gold GRs:** 14-05-2021 `202105141255466911`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The 14-05-2021 GR only reorganizes the Direct Benefit Transfer (DBT) Action Committee at the State level and does not mention or change the Maha DBT disbursement process. No newer GR found in this corpus (covers 2018 to 2024) amends, replaces, stays, extends, or clarifies this GR. | 12-10-2018 `201810121542077211` p4 | - |
| Old run 2 | ok | answered | The 14 May 2021 GR (202105141255466911) reorganises the DBT Action Committee and does not change the Maha DBT disbursement process. No newer GR in the corpus amends, replaces, stays, extends or clarifies that 14 May 2021 GR. | 30-11-2021 `20211130156272711` p2; 12-10-2018 `201810121542077211` p4 | - |
| Final run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) changed the 14-05-2021 GR. The 14-05-2021 GR itself only reconstitutes the state-level DBT Action Committee and does not describe any disbursement process. | 14-05-2021 `202105141255466911` p1; 30-11-2021 `202111301536272711` p1 | - |
| Final run 2 | retried_ok | answered | No newer GR found in this corpus (covers 2018 to 2024) changed the 14-05-2021 GR. The 14-05-2021 GR is about reconstituting the state-level DBT Working Committee and does not mention any change to the Maha DBT disbursement process. | 14-05-2021 `202105141255466911` p1 | - |

### Q110 (CO, MR): Has the 26 February 2020 approval for the Chief Minister's Helpline been changed by a later GR?

**Gold:** No newer GR found in this corpus (covers 2018 to 2024)  
**Gold GRs:** 26-02-2020 `202002261550215011`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 26 February 2020 approval for the Chief Minister's Helpline. The newer-GR candidate 201907311131241311 is unrelated to this approval. I couldn't find a later GR changing that specific approval. | 26-02-2020 `202002261550215011` p1 | - |
| Old run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 26-02-2020 approval for the Chief Minister's Helpline. The only newer-GR candidate reviewed, 201907311131241311, cites a different GR and is unrelated to the Chief Minister Helpline approval. | 26-02-2000 `202002261550215011` p1 | - |
| Final run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that changes the 26 February 2020 administrative approval for the Chief Minister's Helpline. The retrieved GR from 26-02-2020 itself grants the administrative approval for integrating citizen contact with a single telephone number for the Chief Minister's Helpline, approving 80 seats for three years at a per-seat monthly cost of Rs. 21,462 plus GST and toll-free number expenses totaling Rs. 6,83,26,560 excluding GST. | 26-02-2000 `202002261550215011` p1 | - |
| Final run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) has amended, replaced, stayed, extended, or clarified the 26 February 2020 administrative approval for the Chief Minister's Helpline. | 26-02-2020 `202002261550215011` p1 | - |

### Q111 (CO, MR): What is the latest GR on free 7/12 and 8A land record extracts through Aaple Sarkar centres?

**Gold:** The circular of 19-12-2019; no newer GR found in this corpus  
**Gold GRs:** 19-12-2019 `201912191347332011`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | failed | None | (no answer) | - | - |
| Old run 2 | ok | answered | The latest GR in the corpus on free 7/12 and 8A land record extracts through Aaple Sarkar centres is dated 19-12-2019, which issues guidelines for providing computed 7/12 and 8A extracts free of cost through Aaple Sarkar Seva Kendra from the Bhulekh website and prohibits operators from verifying copies with a signature stamp. | 19-12-2019 `201912191347332011` p1 | - |
| Final run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) changes the 19-12-2019 guidelines for free 7/12 and 8A land record extracts through Aaple Sarkar Seva Kendra centres. The 19-12-2019 GR itself provides the latest guidance available in the corpus: it states that the free computed 7/12 and 8A extracts provided through Aaple Sarkar Seva Kendra from the Bhulekh website are for information only, must not bear a signature or stamp verifying authenticity, and misuse should be reported to the Collector who forwards complaints to the IT department under the 19-01-2018 GR. | 19-12-2019 `201912191347332011` p1 | - |
| Final run 2 | ok | answered | The latest GR in the corpus on free 7/12 and 8A land record extracts through Aaple Sarkar centres is dated 19-12-2019. It issues guidelines that the free view-only 7/12 and 8A extracts available via Aaple Sarkar Seva Kendra on the Bhulekh website are for information only and cannot be used for any government or legal purpose, and it prohibits Aaple Sarkar centre operators from signing or stamping copies as verified. | 19-12-2019 `201912191347332011` p1 | - |

### Q112 (CO, MR): Has the 16 August 2019 GR on data standardisation and interoperability been changed?

**Gold:** No newer GR found in this corpus  
**Gold GRs:** 16-08-2019 `201908161445040311`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 16 August 2019 GR on data standardisation and interoperability. | 16-08-2019 `201908161445040311` p1 | - |
| Old run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the 16 August 2019 GR on data standardisation and interoperability. The corpus contains the GR itself but nothing subsequent changes it. | 16-08-2019 `201908161445040311` p2 | - |
| Final run 1 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) changes the 16 August 2019 GR on data standardisation and interoperability. The corpus contains that GR as 201908161445040311, which grants administrative approval for the Data Standardization and Interoperability and Digital Services Delivery project for Rs. 113.06 crore and transfers it to MahaIT. | 16-08-2019 `201908161445040311` p2; 16-08-2019 `201908161445040311` p2 | - |
| Final run 2 | ok | answered | No newer GR found in this corpus (covers 2018 to 2024) has changed the 16 August 2019 GR on data standardisation and interoperability. The 16-08-2019 GR granted administrative approval to the Data Standardization and Interoperability and Digital Services Delivery project for Rs. 113.06 crore and transferred it to Maharashtra Information Technology Corporation. | 16-08-2019 `201908161445040311` p2 | - |

### Q113 (MI, MR): Show me the 17 February 2018 telecom infrastructure policy GR.

**Gold:** Not in this corpus. (The corpus's GR of 17-02-2018 is a different one: a tender evaluation committee for consultants.) It is cited by the GRs of 03-03-2018, 08-07-2019, 07-06-2021 and 04-11-2022, and the policy was revised by the telecom infrastructure policy GR of 04-11-2022  
**Gold GRs:** 03-03-2018 `201803031333271711`, 04-11-2022 `202211041809363311`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | retried_ok | not_found | I couldn't find a GR on telecom infrastructure policy dated 17 February 2018 in the corpus. The corpus contains a GR dated 17-02-2018 (201802171427235111) titled 'Tender Evaluation Committee for Empanelment of Consultants for IT Projects in Government of Maharashtra.', which is unrelated. The actual telecom infrastructure policy is referenced by later GRs (e.g., 202211041809363311 dated 04-11-2022 and 201907111447186811 dated 08-07-2019) as Government Resolution No. मातंसं०६५/प्र.क्र.१/२०१८, dated 17.02.2018, but its full text is not provided in the retrieved set. | 17-02-2018 `201802171427235111` p1; 04-11-2022 `202211041809363311` p1; 03-03-2018 `201803031333271711` p1; 08-07-2019 `201907111447186811` p1 | - |
| Old run 2 | retried_ok | answered | The corpus GR dated 17-02-2018 (code 201802171427235111) is about the Tender Evaluation Committee for empanelment of consultants for IT projects, not a telecom infrastructure policy. No newer GR in the corpus amends, replaces, stays, extends, or clarifies this GR. | 17-02-2018 `201802171427235111` p1 | - |
| Final run 1 | retried_ok | answered | The current rule, as amended by GR dated 08-07-2019, includes IP-1 institutions and roof top towers under mobile towers in the telecom infrastructure policy. Earlier, the 17 February 2018 GR (Tender Evaluation Committee for Empanelment of Consultants for IT Projects in Government of Maharashtra) only constituted a Tender Evaluation Committee for empanelment of consultants and did not cover telecom infrastructure policy contents. | 17-02-2018 `201802171427235111` p1; 03-03-2019 `201803031333271711` p1; 08-07-2019 `201907111447186811` p1 | 08-07-2019 `201907111447186811`: Included IP-1 institutions in the policy and added roof top towers to the definition of mobile towers. |
| Final run 2 | retried_ok | answered | The asked-for GR dated 17-02-2018 establishes the Tender Evaluation Committee for the 5-year empanelment of IT project consultants. No newer GR in the corpus amends, replaces, stays, extends, or clarifies this GR. | 17-02-2018 `201802171427235111` p1 | - |

### Q114 (MI, MR): What did the 16 September 2016 GR setting up the state DBT committee say?

**Gold:** Not in this corpus. It is cited by the GR of 14-05-2021, which reconstituted that committee  
**Gold GRs:** 14-05-2021 `202105141255466911`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | not_found | The 16-09-2016 GR establishing the state DBT committee is not among the corpus texts. The 2021-05-14 GR (reorganization of DBT Action Committee) cites it by referencing the government decision dated 16 September 2016 (Maatans 054/31/2016/39) and states that the DBT Cell constituted thereunder is being reconstituted with a new membership list. No corpus GR reproduces the original 2016 text. | 14-05-2021 `202105141255466911` p1; 14-05-2011 `202105141255466911` p1 | - |
| Old run 2 | ok | answered | The 16 September 2016 GR established the state DBT committee under Government Resolution No. मातंसं ०५४/३१/२०१६/३९. A later GR dated 14-05-2021 reconstituted that committee with a new composition, listing the Additional Chief Secretary (Finance) as Chairman and the Director (IT) as Member Secretary. | 14-05-2021 `20210514125546911` p1; 14-05-2021 `202105141255466911` p2; 14-05-2021 `202105141266911` p2 | 14-05-2021 `202105141255466911`: Reconstituted the state DBT committee set up by the 16-09-2016 GR, listing a new chair and members such as Additional Chief Secretary (Finance) as Chairman and Director (IT) as Member Secretary. |
| Final run 1 | ok | not_found | I couldn't find a GR on this in the corpus. The 14-05-2021 GR (202105141255466911) cites the 16 September 2016 decision (Mat 054/31/2016/39) as the founding Government Resolution that established the state-level DBT Cell, and says it is now being reconstituted. | 14-05-2021 `202105141255466911` p1; 14-05-2016 `202105141255466911` p1 | - |
| Final run 2 | ok | not_found | I couldn't find a GR on this in the corpus. The 14-05-2021 GR (code 202105141255466911) cites a Government Decision dated 16 September 2016 (GR number मातंसं ०५४/३१/२०१६/३९) as the decision that established the state-level DBT committee, and states that the committee was being reconstituted. It does not reproduce the text of the 16 September 2016 GR itself. | 14-05-2021 `202105141255466911` p1 | - |

### Q115 (DV, MR): मातंस २०१८/प्र.क्र.४५/से-१/का.३९: who represents Land Records for the Mumbai Suburban District on the blockchain working group?

**Gold:** The District Superintendent, Land Records, Mumbai Suburban District, per the corrigendum of 31-07-2019. The original GR of 11-04-2019 named the Director, Land Records (Suburbs), Bandra. The later corrigendum of 04-10-2019 changed only the health member, not this one  
**Gold GRs:** 11-04-2019 `201904111526241211`, 31-07-2019 `201908011113322811`, 04-10-2019 `201910041107154511`

| Run | Format | Status | Raw answer | Raw cited | Raw newer |
|---|---|---|---|---|---|
| Old run 1 | ok | answered | The District Superintendent, Land Records, Mumbai Suburban District is listed as an administrative member of the land records working group in GR मातंस २०१८/प्र.क्र. ४५/से-१/का.३९ dated 11-04-2019. The 31-07-2019 GR amends this by replacing the previous director-level post with the same district superintendent post. | 11-04-20019 `201904111526241211` p2; 31-07-2019 `201908011113322811` p1 | 31-07-2019 `201908011113322811`: It replaces members 7, 8, and 9 of the land records working group: member 7 becomes Deputy Manager, Land Records, Konkan Region; member 8 becomes District Superintendent, Land Records, Mumbai Suburban District, Administrative Member; member 9 becomes Town Geo Assessment Officer, Vile Parle. |
| Old run 2 | ok | answered | The 11-04-2019 GR lists the Director, Land Records, Fort, Mumbai as a member, and the Director, Land Records (Suburban), Bandra (East), Mumbai as a member, for the Land Records working group. The 31-07-2019 GR amends those memberships by replacing the Director, Land Records, Fort, Mumbai with the Deputy Director, Land Records, Konkan Region, Fort, Mumbai, replacing the Director, Land Records (Suburban) with the District Superintendent, Land Records, Mumbai Suburban District, and replacing the District Superintendent with the Town Geo Assessment Officer, Vile Parle. For the Mumbai Suburban District specifically, the District Superintendent, Land Records, Mumbai Suburban District is the representative. | 11-04-2019 `201904111526241211` p1; 31-07-2019 `201908011113322811` p1 | - |
| Final run 1 | ok | answered | The Land Records representative for the Mumbai Suburban District on the blockchain working group is the District Superintendent, Land Records, Mumbai Suburban District, listed as an administrative member. This was substituted by the 31-07-2019 GR, which amended the original 11-04-2019 GR's working group composition for Land Records. Earlier, the group had the Director, Land Records (Suburbs) as the member. | 31-07-2009 `201908011113322811` p1; 31-07-2019 `201908011113322811` p1; 31-07-2019 `201908011113322819` p1 | 31-07-2019 `201908011113322811`: Replaced the Land Records working group members: 7. Director, Land Records, Fort, Mumbai-400023 with Deputy Manager, Land Records, Konkan Region, Fort, Mumbai-400023; 8. Director, Land Records (Suburbs), Bandra (East), Mumbai-400051 with District Superintendent, Land Records, Mumbai Suburban District, Administrative Member; 9. Director Land Records, Vile Parle (p.), Mumbai 400047 with Town Geo Assessment Officer, 106, SV Road, Suresh Colony, LIC Member Colony, Vile Parle-400047. |
| Final run 2 | retried_ok | answered | The District Superintendent of Land Records, Mumbai Suburban District, serves as the administrative member representing Land Records for the Mumbai Suburban District on the blockchain working group. Earlier, the 11-04-2019 GR listed the Director of Land Records, Fort, Mumbai; the Director of Land Records (Suburban), Bandra (East); and the Director of Land Records, Vile Parle (p.), Mumbai as members. The 31-07-2019 GR amended these positions. | 31-07-2019 `201908011113322911` p1; 11-04-2019 `201904111526241211` p1 | 31-07-2019 `201908011113322811`: Replaced the original land records working group members (points 7, 8, 9) with: 7. Deputy Manager, Land Records, Konkan Region, Fort, Mumbai-400023 as member; 8. District Superintendent, Land Records, Mumbai Suburban District, Administrative Member at Bandra (East); 9. Town Geo Assessment Officer, 106 SV Road, Suresh Colony, LIC Member Colony, Vile Parle-400047 as member. |


## Appendix: driver used for the runs (not part of the repository code)

Run from a shell with `SARVAM_API_KEY` set, `DAILY_SPEND_CAP_INR=15` and `RUN_SPEND_CAP_INR=15`:

```bash
python run_holdout.py <worktree at 835367c> holdout-old-run1
python run_holdout.py <engine-v1 checkout at 49ee4ae> holdout-final-run1
```

```python
"""Run the locked engine at a given checkout on the hold-out questions.

Usage: python run_holdout.py <checkout_dir> <run_name>
Runs from <checkout_dir> with that checkout's own grengine code. Only three module
constants are redirected (no repo code is changed):
  QUESTIONS     -> eval/holdout_questions.jsonl of the main repo
  RUNS_DIR      -> runs/ of the main repo
  SpendTracker  -> the main repo's spend ledger, so all runs share one daily cap
"""
import os
import sys
from pathlib import Path

MAIN = Path("/home/user/sarvam-mh-gr-engine")
checkout, name = Path(sys.argv[1]).resolve(), sys.argv[2]
os.chdir(checkout)
sys.path.insert(0, str(checkout))

import grengine.run as run  # noqa: E402
import grengine.sarvam as sarvam  # noqa: E402

assert Path(run.__file__).resolve().is_relative_to(checkout), run.__file__
run.QUESTIONS = MAIN / "eval/holdout_questions.jsonl"
run.RUNS_DIR = MAIN / "runs"
run.SpendTracker = lambda: sarvam.SpendTracker(spend_dir=MAIN / "runs/spend")
print(f"code: {run.__file__}  prompt: {__import__('grengine.answer', fromlist=['x']).PROMPT_VERSION}", flush=True)
sys.exit(run.main(["--name", name, "--csv"]))
```
