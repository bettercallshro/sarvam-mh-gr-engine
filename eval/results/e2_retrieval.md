# E2 retrieval check (top 5)

No model calls. Hit = a gold GR (or its twin) is in the top 5; twins share one slot.

**Overall: 37/37 (100%)**

## By split

`lang` is the language of the gold GRs (EN,MR = both, e.g. twins). Questions with two case tags count under each.

| lang | hit rate |
|---|---|
| EN | 15/15 (100%) |
| EN,MR | 3/3 (100%) |
| MR | 19/19 (100%) |

| task | hit rate |
|---|---|
| L | 23/23 (100%) |
| S | 14/14 (100%) |

| case | hit rate |
|---|---|
| AM | 19/19 (100%) |
| CO | 6/6 (100%) |
| DU | 2/2 (100%) |
| DV | 1/1 (100%) |
| MI | 4/4 (100%) |
| ST | 5/5 (100%) |
| TY | 1/1 (100%) |

Rank of first gold GR: #1: 26, #2: 8, #3: 2, #5: 1

## Misses

None.

## Hits not at rank 1

| Q | gold rank | ranked above it |
|---|---|---|
| 2 | 3 | 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting; 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regarding hosting |
| 4 | 2 | 16-02-2018 `201802161919110111` Setting up of Global Fintech Hub and implementation of Fintech policy |
| 5 | 5 | 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting; 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Providers and Gui; 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Providers and Guid; 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Providers and Gui |
| 6 | 2 | 08-07-2019 `201907111447186811` Inclusion of IP-1 Institutions in Telecom Infrastructure Policy. |
| 14 | 2 | 20-03-2018 `201803201319308011` Regarding Empanelment of Consultants for IT Projects in Government of |
| 15 | 2 | 20-03-2018 `201803201319308011` Regarding Empanelment of Consultants for IT Projects in Government of |
| 16 | 3 | 05-10-2023 `202310041905383211` Regarding Empanelment of Consultants for IT Projects in Government of; 24-04-2023 `202304241816282211` Empanelment of Consultants for IT Projects in Government of Maharashtr |
| 18 | 2 | 20-03-2018 `201803201319308011` Regarding Empanelment of Consultants for IT Projects in Government of |
| 20 | 2 | 12-10-2018 `201810121542077211` Disbursement process of Maharashtra Direct Benefit Transfer and Servic |
| 27 | 2 | 03-04-2018 `201804031706228211` Regarding setting up of the Governance Structure and Domain groups for |
| 37 | 2 | 28-11-2018 `201811281816489211` Regarding Standard Operating Procedure (SOP) for use of e-Maha Pariksh |

## Missing-GR questions (9, 16, 36, 37)

The asked-for GR is not in the corpus. The right result is a GR that cites it; the answer must say the asked-for GR isn't in the corpus.

### Q9: Show me the 24 February 2015 GR on laptops for officers.

- Hit: yes, rank 1
- Asked-for date 24-02-2015: no GR in the corpus has this date. Cited by: 24-12-2019 `201912241451082111`, 12-04-2023 `202304131657547811`
- Top 5:
  1. 24-12-2019 `201912241451082111` To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employe {'text': 1.0, 'cites_missing': 0.9}
  2. 12-04-2023 `202304131657547811` To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employe {'text': 0.971, 'cites_missing': 0.9}
  3. 19-04-2018 `201804201114401011` Fintech Policy- Setting up of Working Group. {'text': 0.399}
  4. 10-10-2019 `201910101158307111` Appointment of Grievance Redressal office under Article 23 of The Righ {'text': 0.359}
  5. 19-10-2020 `202010191540488111` Use of mahaeoffice portal for of official work. {'text': 0.353}

### Q16: What did the 9 May 2019 IT consultant GR say?

- Hit: yes, rank 3
- Asked-for date 09-05-2019: no GR in the corpus has this date. Cited by: 19-03-2021 `202103191753279311`, 24-04-2023 `202304241816282211`, 05-10-2023 `202310041905383211`
- Top 5:
  1. 05-10-2023 `202310041905383211` Regarding Empanelment of Consultants for IT Projects in Government of {'text': 1.0, 'cites_missing': 0.9}
  2. 24-04-2023 `202304241816282211` Empanelment of Consultants for IT Projects in Government of Maharashtr {'text': 0.944, 'cites_missing': 0.9}
  3. 19-03-2021 `202103191753279311` Regarding Empanelment of Consultants for IT Projects in Government of {'text': 0.871, 'cites_missing': 0.9}
  4. 05-03-2024 `202403051249430211` Regarding Empanelment of Consultants for IT Projects in Government of {'text': 0.985}
  5. 20-03-2018 `201803201319308011` Regarding Empanelment of Consultants for IT Projects in Government of {'text': 0.96}

### Q36: Is the 2022 GR on generative AI use in government offices in force?

- Hit: yes, rank 1
- No full date in the question (year [2022]): the missing-GR signal has to come from the answer step (no exact match).
- Top 5:
  1. 03-03-2020 `202003031509142811` Regarding use of Artificial Intelligence Marathi Language Technology, {'text': 1.0}
  2. 04-11-2022 `202211041809363311` Telecom Infrastructure Policy. {'text': 0.436, 'year': 0.1}
  3. 16-02-2018 `201802161919110111` Setting up of Global Fintech Hub and implementation of Fintech policy {'text': 0.499}
  4. 27-03-2023 `202303301831230311` Regarding setting up a task force to launch and implement 5G services {'text': 0.382}
  5. 23-02-2023 `202302231826565311` Standard Operating Procedures for implement eOffice.... {'text': 0.362}

### Q37: What did the 19 September 2017 Maha-Pariksha GR say?

- Hit: yes, rank 2
- Asked-for date 19-09-2017: no GR in the corpus has this date. Cited by: 28-11-2018 `201811281816489211`, 28-11-2018 `201811291757404011`, 20-02-2020 `202002201713214911`, 21-01-2021 `202101211644450911`, 04-03-2021 `202103041719472911`
- Top 5:
  1. 28-11-2018 `201811281816489211` Regarding Standard Operating Procedure (SOP) for use of e-Maha Pariksh {'text': 1.0, 'cites_missing': 0.9}
  2. 20-02-2020 `202002201713214911` About updated process of Exams Conduction under Maha-Pariksha. {'text': 0.932, 'cites_missing': 0.9}
  3. 24-02-2020 `202002241155355511` About updated process of Exams Conduction under Maha-Pariksha. {'text': 0.932}
  4. 12-10-2018 `201810121542077211` Disbursement process of Maharashtra Direct Benefit Transfer and Servic {'text': 0.384}
  5. 22-04-2020 `202004221243514111` Renewal rate of Technical Manpower of Maha IT for year dated 01/04/202 {'text': 0.341}

## Newer-GR candidates: Controls (30 to 35)

For the top retrieved GR, and for each gold GR not already shown. Ranked by evidence: date+order, order, date, same_file. *Candidate only* = only a shared file number; never proof of a newer GR.

### Q30: Is the e-Tenders GR of 11 May 2021 still the latest on e-tendering?

- top result: 11-05-2021 `202105111646307611` Implementation of E-Tenders
  - 14-05-2021 `202105141255466911` Reorganization of Dicrect Benefit Transfer Action Committee — **same_file** (candidate only)

### Q31: Has the model RFP GR of September 2019 been updated?

- top result: 20-09-2019 `201909202117198311` Maharashtra Model RFP document For IT and e-Governance projects.
  - 26-02-2020 `202002261550215011` Administrative approval for the Implementation of Hon. Chief — **same_file** (candidate only)

### Q32: What is the latest GR on the State Data Center as critical information infrastructure?

- top result: 05-10-2019 `201910051257224511` Declaration of Maharashtra State Data Center as Critical Information I
  - none (no GR in the corpus cites it)

### Q33: What is the latest GR on the Maharashtra Unified Citizen Data Hub?

- top result: 04-02-2022 `202202042136207511` Regarding implementation of Maharashtra Unified Citizen Data Hub for d
  - none (no GR in the corpus cites it)

### Q34: Is there a GR on a 5G task force, and has it changed?

- top result: 27-03-2023 `202303301831230311` Regarding setting up a task force to launch and implement 5G services
  - none (no GR in the corpus cites it)

### Q35: What is the latest GR on the Setu Kendra tender process?

- top result: 19-07-2024 `202407191742379111` Regarding the tender process of Setu Kendra in the collector and tehsi
  - none (no GR in the corpus cites it)

## Newer-GR candidates: Cloud chain (1 to 6)

For the top retrieved GR, and for each gold GR not already shown. Ranked by evidence: date+order, order, date, same_file. *Candidate only* = only a shared file number; never proof of a newer GR.

### Q1: Is the 29 January 2018 cloud computing circular still current?

- top result: 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **date+order**
  - 08-03-2019 `201903081945167511` HYBRID - Administrative Approval on Establishment of Hybrid — **date**
  - 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Provider — **date**
  - 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 16-10-2018 `201810161335463211` Competent Authority for Data and Data Access for all Governm — **date**, 2 hops
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
  - 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
- gold: 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Providers and Gui
  - none (no GR in the corpus cites it)

### Q2: What is the deadline for moving existing department applications to the cloud?

- top result: 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **date+order**
  - 08-03-2019 `201903081945167511` HYBRID - Administrative Approval on Establishment of Hybrid — **date**
  - 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Provider — **date**
  - 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 16-10-2018 `201810161335463211` Competent Authority for Data and Data Access for all Governm — **date**, 2 hops
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
  - 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)

### Q3: There was a cloud policy circular a couple of years ago, something about migration. Which GR?

- top result: 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **date+order**
  - 08-03-2019 `201903081945167511` HYBRID - Administrative Approval on Establishment of Hybrid — **date**
  - 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Provider — **date**
  - 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 16-10-2018 `201810161335463211` Competent Authority for Data and Data Access for all Governm — **date**, 2 hops
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
  - 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
- gold: 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Providers and Gui
  - none (no GR in the corpus cites it)

### Q4: A file cites the State cloud policy dated 19/01/2018. Is that current?

- top result: 16-02-2018 `201802161919110111` Setting up of Global Fintech Hub and implementation of Fintech policy
  - 30-11-2018 `201811301239595811` Setting up of Global Fintech Hub and implementation of Finte — **date+order**
  - 30-11-2018 `201811301240117211` Setting up of Global Fintech Hub and implementation of Finte — **date+order**
  - 05-11-2018 `201811061202283811` Administrative approval to the Maharashtra Information Techn — **date+order**
  - 19-04-2018 `201804201113320211` Fintech Policy- Setting up of State Level Steering Committee — **date+order**
  - 19-04-2018 `201804201114401011` Fintech Policy- Setting up of Working Group. — **date+order**
  - 19-04-2018 `201804201439329111` Fintech Policy- Setting up of Advisory Panel — **date+order**
- gold: 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **date+order**
  - 08-03-2019 `201903081945167511` HYBRID - Administrative Approval on Establishment of Hybrid — **date**
  - 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Provider — **date**
  - 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 16-10-2018 `201810161335463211` Competent Authority for Data and Data Access for all Governm — **date**, 2 hops
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
  - 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**
- gold: 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Providers and Gui
  - none (no GR in the corpus cites it)

### Q5: Can my department still buy cloud services from the empanelled cloud providers?

- top result: 29-01-2018 `201801291824268911` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **date+order**
  - 08-03-2019 `201903081945167511` HYBRID - Administrative Approval on Establishment of Hybrid — **date**
  - 04-08-2018 `201808041826435611` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 19-05-2018 `201805211415360511` Cloud Computing Policy-Empanelment of Cloud Service Provider — **date**
  - 16-05-2018 `201805171357566211` Cloud Computing Policy- Empanelment of Cloud Service Provide — **date**
  - 16-10-2018 `201810161335463211` Competent Authority for Data and Data Access for all Governm — **date**, 2 hops
  - 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
  - 19-06-2019 `201906191741481211` Cloud Computing Policy- Instructions to Departments regardin — **same_file** (candidate only)
- gold: 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Providers and Gui
  - none (no GR in the corpus cites it)

### Q6: What did the July 2019 cloud GR change?

- top result: 08-07-2019 `201907111447186811` Inclusion of IP-1 Institutions in Telecom Infrastructure Policy.
  - none (no GR in the corpus cites it)
- gold: 05-07-2019 `201907051642210511` Cloud Computing Policy- Instructions to Departments regarding hosting
  - 23-04-2021 `202104231756150811` Cloud Computing policy  Empanelment of Cloud Service Provide — **order**

