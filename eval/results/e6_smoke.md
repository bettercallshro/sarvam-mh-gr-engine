# E6: smoke test on questions 1, 7, 11, 30, 36 (18-11-2026)

Run log: `runs/2026-11-18-smoke.jsonl`. Prompt `answer_v2`, JSON mode, temperature 0.2, max_tokens 4096.

Cost: Rs 0.7054 for 5 calls (73314 prompt tokens, of which 12896 cached; 3919 completion tokens; 0 reasoning tokens). Spent today after this run: Rs 1.10.

Each answer below is shown three ways: the raw model reply exactly as returned, the corrections the checks made, and the checked answer (the product).

## Q1: Is the 29 January 2018 cloud computing circular still current?

**Gold:** Not as issued. Deadline moved to 31-03-2020 (19-06-2019); data archival and review rules added (05-07-2019); cloud empanelment ended 30-04-2021 and buying moved to GeM (23-04-2021). Latest: 23-04-2021

Tokens: 15624 in (1344 cached), 1037 out (0 reasoning). Cost Rs 0.1691. Latency 4.41 s.

Newer-GR candidates given: 23-04-2021 `202104231756150811` (date+order), 08-03-2019 `201903081945167511` (date), 04-08-2018 `201808041826435611` (date, in retrieved), 19-05-2018 `201805211415360511` (date, in retrieved), 16-05-2018 `201805171357566211` (date, in retrieved), 16-10-2018 `201810161335463211` (date), 05-07-2019 `201907051642210511` (same_file), 19-06-2019 `201906191741481211` (same_file, in retrieved)

**Raw model reply:**

```json
{
 "asked_for_code": "201801291824268911",
 "candidates_reviewed": [
  {
   "code": "202104231756150811",
   "effect": "unrelated",
   "reason": "It cites the 201801291824268911 only in a list of earlier references and does not amend, replace, stay, extend, or clarify any of its provisions; it deals with GeM portal procurement and expiry of empanelment rates from 201805171357566211."
  },
  {
   "code": "201903081945167511",
   "effect": "unrelated",
   "reason": "It cites the 201801291824268911 only in a list of references and is solely about setting up a Hybrid Adaptive Cyber Security Operations and CERT Maharashtra; no provision of the 2018 GR is amended, replaced, stayed, extended or clarified."
  },
  {
   "code": "201810161335463211",
   "effect": "unrelated",
   "reason": "It cites the 201801291824268911 only in a list of references and is about appointing DIT as Competent Authority for Data and Data Access; it does not change any part of the 2018 GR."
  },
  {
   "code": "201907051642210511",
   "effect": "clarifies",
   "reason": "It issues addendum instructions on data migration, archiving, and periodic review on cloud, which clarifies operational aspects of hosting IT applications under the 2018 GR framework without changing its core policy or deadlines."
  },
  {
   "code": "201906191741481211",
   "effect": "amends",
   "reason": "It explicitly supersedes earlier instructions by changing the application migration deadline from 30.10.2018 to 31.03.2020, and adds new procedural requirements such as mandatory security audits and PIC authorization for CSP selection."
  }
 ],
 "newer": [
  {
   "code": "201906191741481211",
   "date": "19-06-2018",
   "what_changed": "Changed the migration deadline for existing applications from 30.10.2018 to 31.03.2020, and added mandatory security audit and PIC authorization for CSP selection."
  },
  {
   "code": "201907051642210511",
   "date": "05-07-2019",
   "what_changed": "Clarified operational procedures for data migration, archiving, and periodic review on cloud under the 2018 GR framework."
  }
 ],
 "cited": [
  {
   "code": "201801291824268911",
   "date": "29-01-2018",
   "title": "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications",
   "quote": "The following instructions are issued in supersession of all earlier instructions issued in this regard.",
   "page": 1
  },
  {
   "code": "201906191741481211",
   "date": "19-06-2019",
   "title": "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications",
   "quote": "In case of existing applications not hosted in a cloud environment, Government organizations must ensure that the applications are migrated to cloud on or before 31.03.2020.",
   "page": 1
  },
  {
   "code": "20190705161210511",
   "date": "05-00-0000",
   "title": "",
   "quote": "",
   "page": 0
  }
 ],
 "answer": "No, the 29 January 2018 cloud computing circular is not current in its original form because a newer GR dated 19-06-2019 amended its migration deadline from 30.10.2018 to 31.03.2020 and added mandatory security audits and PIC authorization requirements. A further addendum dated 05-07-2019 clarified data migration and archiving procedures. The corpus does not show any GR that repeals or supersedes the 2018 circular entirely.",
 "status": "answered"
}
```

**Corrections made by the checks:** 
- `title_from_metadata` cited[1].title: "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications" → "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications."
- `drop_unknown_code` cited[2]: {"code": "20190705161210511", "date": "05-00-0000"} → "dropped (not a corpus GR code)"
- `date_from_metadata` newer[0].date: "19-06-2018" → "19-06-2019"

**Flags (left in place):** none

**Checked answer (product):**

```json
{
 "status": "answered",
 "answer": "No, the 29 January 2018 cloud computing circular is not current in its original form because a newer GR dated 19-06-2019 amended its migration deadline from 30.10.2018 to 31.03.2020 and added mandatory security audits and PIC authorization requirements. A further addendum dated 05-07-2019 clarified data migration and archiving procedures. The corpus does not show any GR that repeals or supersedes the 2018 circular entirely.",
 "cited": [
  {
   "code": "201801291824268911",
   "date": "29-01-2018",
   "title": "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications",
   "url": "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/English/201801291824268911.pdf",
   "quote": "The following instructions are issued in supersession of all earlier instructions issued in this regard.",
   "page": 1,
   "quote_verified": true
  },
  {
   "code": "201906191741481211",
   "date": "19-06-2019",
   "title": "Cloud Computing Policy- Instructions to Departments regarding hosting of IT applications.",
   "url": "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/English/201906191741481211.pdf",
   "quote": "In case of existing applications not hosted in a cloud environment, Government organizations must ensure that the applications are migrated to cloud on or before 31.03.2020.",
   "page": 1,
   "quote_verified": true
  }
 ],
 "newer": [
  {
   "code": "201906191741481211",
   "date": "19-06-2019",
   "what_changed": "Changed the migration deadline for existing applications from 30.10.2018 to 31.03.2020, and added mandatory security audit and PIC authorization for CSP selection."
  },
  {
   "code": "201907051642210511",
   "date": "05-07-2019",
   "what_changed": "Clarified operational procedures for data migration, archiving, and periodic review on cloud under the 2018 GR framework."
  }
 ],
 "coverage": "Information Technology GRs, 2018 to 2024"
}
```

## Q7: What is the maximum spend on a laptop or tablet for an IAS, IPS or IFS officer?

**Gold:** Rs 1,20,000 (12-04-2023). Earlier cap Rs 85,000 (24-12-2019)

Tokens: 8879 in (8832 cached), 473 out (0 reasoning). Cost Rs 0.0145. Latency 1.67 s.

Newer-GR candidates given: 12-04-2023 `202304131657547811` (date+order, in retrieved)

**Raw model reply:**

```json
{
 "candidates_reviewed": [
  {
   "code": "202304131657547811",
   "effect": "replaces",
   "reason": "The 2023 GR supersedes the 2019 GR by stating 'सदर शुध्दिपत्रक या शुध्दिपत्रकान्वये अधिक्रमित करण्यात येत आहे' (This corrigendum is being superseded by this corrigendum) and revises the maximum purchase limit from Rs. 85,000 to Rs. 1,20,000."
  }
 ],
 "newer": [
  {
   "code": "202304131657547811",
   "date": "12-04-2023",
   "what_changed": "Replaces the 2019 GR and increases the maximum spend on a laptop/tablet/iPad for IAS, IPS, IFS officers from Rs. 85,000 to Rs. 1,20,000."
  }
 ],
 "cited": [
  {
   "code": "201912241451082111",
   "date": "24-12-2019",
   "title": "To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employees.",
   "quote": "सदर खरेदी रू. ८५०००/- या कमाल मर्यादेत असावी.",
   "page": 1
  },
  {
   "code": "202304131657547811",
   "date": "12-04-2024",
   "title": "To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employees..",
   "quote": "सदर खरेदी रू. १२००००/- (रूपये एक लाख वीस हजार फक्त) या कमाल मर्यादेत असावी.",
   "page": 1
  }
 ],
 "answer": "The maximum spend is Rs. 1,20,000 for a laptop or tablet for IAS, IPS or IFS officers, as revised by the 12-04-2023 GR which superseded the 2019 GR.",
 "status": "answered"
}
```

**Corrections made by the checks:** 
- `date_from_metadata` cited[1].date: "12-04-2024" → "12-04-2023"

**Flags (left in place):** none

**Checked answer (product):**

```json
{
 "status": "answered",
 "answer": "The maximum spend is Rs. 1,20,000 for a laptop or tablet for IAS, IPS or IFS officers, as revised by the 12-04-2023 GR which superseded the 2019 GR.",
 "cited": [
  {
   "code": "201912241451082111",
   "date": "24-12-2019",
   "title": "To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employees.",
   "url": "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/English/201912241451082111.pdf",
   "quote": "सदर खरेदी रू. ८५०००/- या कमाल मर्यादेत असावी.",
   "page": 1,
   "quote_verified": true
  },
  {
   "code": "202304131657547811",
   "date": "12-04-2023",
   "title": "To Provide Computer/Laptop/Tablet/IPad to Government Officials/Employees..",
   "url": "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/English/202304131657547811.pdf",
   "quote": "सदर खरेदी रू. १२००००/- (रूपये एक लाख वीस हजार फक्त) या कमाल मर्यादेत असावी.",
   "page": 1,
   "quote_verified": true
  }
 ],
 "newer": [
  {
   "code": "202304131657547811",
   "date": "12-04-2023",
   "what_changed": "Replaces the 2019 GR and increases the maximum spend on a laptop/tablet/iPad for IAS, IPS, IFS officers from Rs. 85,000 to Rs. 1,20,000."
  }
 ],
 "coverage": "Information Technology GRs, 2018 to 2024"
}
```

## Q11: Is the 26 November 2020 GR on the computer qualification certificate in force?

**Gold:** No. Stayed until further orders by the GR of 27-11-2020, which reinstated the orders under the 20-11-2018 letter

Tokens: 9356 in (1376 cached), 1567 out (0 reasoning). Cost Rs 0.1193. Latency 4.8 s.

Newer-GR candidates given: 27-11-2020 `202011271209526511` (date+order, in retrieved)

**Raw model reply:**

```json
{
 "code": "202011261535430611",
 "date": "26-11-2020",
 "title": "Decision regarding final date for submission of compulsory computer qualification certificate and recovery of excess payment.",
 "GR number": "मातंसं २०१८/प्र.क्र .५३/से-५/३ ९",
 "original language": "Marathi",
 "text": "# Page 1\nअनिवार्य संगणक अर्हता प्रमाणपत्र सादर करण्याची अंतिम मुदतवाढ ठरविणेबाबत व शासकीय अधिकारी/कर्मचारी यांना अतिप्रदान करण्यात आलेल्या रकमेच्या वसूलीबाबत.\nमहाराष्ट्र शासन\nसामान्य प्रशासन विभाग (माहिती तंत्रज्ञान),\nशासन निर्णय क्रमांक - मातंसं २०१८/प्र.क्र.५३/से-५/३९,\nहुतादत राजगुरु चौक, मादाम कामा मार्ग, मंत्रालय, Mumbai, ४०० ०३२\nदिनांक - २६ नोव्हेंबर, २०२०.\nसंदर्भ - १. शासन अधिसूचना, सामान्य प्रशासन विभाग, क्रमांक सेप्रनि-१०९८/प्र.क्र.७/९९/१२, दि. २५ जानेवारी, १९९९, २. सामान्य प्रशासन विभाग, शासन निर्णय क्रमांक - प्रशिक्षण-२०००/प्र.क्र.५/२००१/३९, दि. २० जुलै, २००२, ३. सामान्य प्रशासन विभाग, शासन निर्णय क्र.मातंसं/नस्ती ०४/२२४/३9, दि.०५ मे, २००७, ४. सामान्य प्रशासन डिपार्टमेंट (माहिती तंत्रज्ञान), पत्र क्रमांक-मातंसं २०१८/प्र.क्र.५३/से-५/३९, दि. २० नोव्हियर, २०१८.\nप्रस्तावना - \n१) संदर्भ क्र.१ येथील शासन अधिसुचनेनुसार राज्य शासकीय सेवेतील गट-अ, गट-ब व गट-क मधील अधिकारी/कर्मचाऱ्यांना संगणक अर्हता प्रमाणपत्र सादर करणे बंधनकारक करण्यात आले आहे.\n२) संदर्भ क्र.३ नुसार संगणक अर्हता प्रमाणपत्र सादर करण्याची अंतिम मुदतवाढ ३१ डिसेंबर, २००७ पर्यंत करण्यात आली होती. सदर मुदतीला मुदतवाढ देण्याबाबत शासनाकडे प्रस्ताव प्राप्त झाले होते.\n३) संदर्भ क्र.२ येथील शासन निर्णयान्वये ज्या अधिकारी/कर्मचारी यांनी विहित मुदतीत संगणiveत प्रमाणपत्र सादर केले नाही, अशा अधिकारी / कर्मचारी यांची वेतनवाढ रोखण्याचे आदेश निर्गमित करण्यात आले आहेत. तथापि, ज्या अधिकारी/कर्मचाऱ्यांनी विहित मुदतीत संगक अर्हता प्रमाणपत्र सादर केले नाही, त्यांची वेतनवाढ रोखणे आवश्यक होते, परंतू ती रोखण्यात न आल्यामुळे अतिप्रदान करण्यात आलेल्या वेतनाच्या वसूलीस संदर्भ क्र.४ येथील पत्रान्वये स्थगिती देण्यात आली होती. याबाबत खालील प्रमाणे निर्णय घेण्यात येत आहे.\nशासन निर्णय - \nअ) राज्य शासकीय सेवेतील गट-अ, गट-ब व गट-क मधील अधिकारी / कर्मचाऱ्यांना संगणक अर्हता प्रमाणपत्र सादर करण्यास संदर्भ क्र.३ येथील शासन निर्णयान्वये\n# Page 2\nशासन निर्णय क्रमांकः मातंसं २०१८/प्र.क्र.५३/से-५/३९\nअंतिमपणे देण्यात आलेली दि. ३१/१२/२००७ पर्यंतची मुदतवाढ हीच अंतिम मुदतवाढ समजण्यात यावी.\nब) ज्या राज्य शासकीय सेवेतील गट-अ, गट-ब व गट-c मधील सेवानिवृत्त / कार्यरत अधिकारी/कर्मचारी यांनी संगणक अर्हता प्रमाणपत्र विहित मुदतीत सादर केलेले नाही, अशा अधिकारी/कर्मचाऱ्यांची वेतनवाढ रोखणे आवश्यक होते. तथापि त्यांची वेतनवाढ रोखण्यात न आल्यामूळे अतिप्रदान करण्यात आलेल्या वेतनाची वसूली करण्यात यावी. सदर शासन निर्णयान्वये संदर्भ क्र.४ येथील दि. २० नोव्हेंबर, २०१८ रोजीचे पत्र अधिक्रमित करण्यात येत आहे.\n# Page 3\n\n--- English machine translation (for reference only; never quote it) ---\nRegarding extension of deadline for submission of Compulsory Computer Qualification Certificate and recovery of excess payment to Government officers/ employees.\nThe Government of Maharashtra\nDepartment of General Administration (Information Technology)\nGOVERNMENT DECISION NO. 2018/ PR. NO. 53/ SE- 5/39,\nHubatma Rajguru Chowk, Madame Cama Marg, Mantralaya, Mumbai, 400 032\nThe date is November 26, 2020.\nReference- 1. Government Notification, General Administration Department, No. Sep. 1098/ Q. No. 7/98/12, D. January 25, 1999, 2. General Administration Department, Government Resolution No. 2000/ Q. No. 5/2001/39, d. July 20, 2002, 2. General Administration Department, Government Resolution No. Matansa/ Nasti 04/224/39, D. May 05, 2007, 3. General Administration Department (Information Technology), Letter No. 2018/ Q. No.53/ Sec- 5/39, D. November 20, 20008.\nThe proposal- \n1) According to the government notification, it has been made mandatory for the officers/ employees of Group-A, Group-B and Group-C in the state government service to submit a computer qualification certificate.\n2) The last date for submission of Computer Qualification Certificate was extended to 31st December, 2007. A proposal had been sent to the government in this regard. 3) According to the GR No. 2 here, orders have been issued to stop the increase in the salary of the officers/ employees who have not submitted the computer qualification certificate within the stipulated time. However, it was necessary to withhold the increment of the officers/ employees who did not submit the computer qualification certificate within the stipulated time, but since it was not withheld, the recovery of the overpaid salary was not considered in the Reference No. 4 has been postponed. The decision is as follows:\nGovernment's decision \n(a) The officers/ employees belonging to Group-A, Group-B and Group-C of the State Government Service are required to submit Computer Qualification Certificate in Reference No. 3 Decisions made by the government\nGOVERNMENT DECISION NO.: MATSAM 2018/ P.S. NO. 53/ SE- 5/39\nThe last given. The extension up to 31/12/2007 should be considered as the final extension. \n(b) It was necessary to withhold the increment of the candidates who have not submitted the computer qualification certificate within the prescribed time. However, the overpaid salaries should be recovered without stopping their increments. As per the Government Resolution No. 4 here. The letter is dated November 20, 2018. \n\n}</div>കമന്റുകൾ</div>",
 "evidence_type": "same_file"
}
```

**Corrections made by the checks:** none

**Flags (left in place):** 
- bad status None

**Checked answer (product):**

```json
{
 "status": null,
 "answer": "",
 "cited": [],
 "newer": [],
 "coverage": "Information Technology GRs, 2018 to 2024"
}
```

## Q30: Is the e-Tenders GR of 11 May 2021 still the latest on e-tendering?

**Gold:** No newer GR found in this corpus (covers 2018 to 2024)

Tokens: 20209 in (0 cached), 411 out (0 reasoning). Cost Rs 0.2124. Latency 2.22 s.

Newer-GR candidates given: 14-05-2021 `202105141255466911` (same_file)

**Raw model reply:**

```json
{
 "asked_for_code": "202105111646307611",
 "candidates_reviewed": [
  {
   "code": "202105141255466911",
   "effect": "cites_only",
   "reason": "The GR only reconstitutes a DBT Working Committee using the same file number (मातंसं ०५४/३१/२०१६/३९) and does not mention e-tendering or e-Tenders at all."
  }
 ],
 "newer": [],
 "cited": [
  {
   "code": "202105111646307611",
   "date": "11-05-2021",
   "title": "Implementation of E-Tenders",
   "quote": "आमच्या विभागामार्फत ई-निविदा संदर्भात निर्गमित करण्यात आलेले संदर्भाधीन अनु.क्र.१ ते ३ येथील आदेश अधिक्रमीत करण्यात येत आहेत।",
   "page": 2
  }
 ],
 "answer": "No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the e-Tenders GR of 11-05-2021. The only newer GR that cites it is 202105141255466911, which only reconstitutes a DBT Working Committee and does not change the e-Tendering GR. Therefore, within the corpus, the 11-05-2011 GR remains the latest on e-tendering.",
 "status": "answered"
}
```

**Corrections made by the checks:** none

**Flags (left in place):** 
- cited[0]: quote not found in the original text of 202105111646307611
- candidates not reviewed by the model: 201803031333271711, 202403051249430211, 202312151508137711, 202310271649358711, 202310041905383211, 202304241816282211, 202103191753279311, 201907111447186811, 201808011629400011

**Checked answer (product):**

```json
{
 "status": "answered",
 "answer": "No newer GR found in this corpus (covers 2018 to 2024) that amends, replaces, stays, extends, or clarifies the e-Tenders GR of 11-05-2021. The only newer GR that cites it is 202105141255466911, which only reconstitutes a DBT Working Committee and does not change the e-Tendering GR. Therefore, within the corpus, the 11-05-2011 GR remains the latest on e-tendering.",
 "cited": [
  {
   "code": "202105111646307611",
   "date": "11-05-2021",
   "title": "Implementation of E-Tenders",
   "url": "https://gr.maharashtra.gov.in/Site/Upload/Government%20Resolutions/English/202105111646307611.pdf",
   "quote": "आमच्या विभागामार्फत ई-निविदा संदर्भात निर्गमित करण्यात आलेले संदर्भाधीन अनु.क्र.१ ते ३ येथील आदेश अधिक्रमीत करण्यात येत आहेत।",
   "page": 2,
   "quote_verified": false
  }
 ],
 "newer": [],
 "coverage": "Information Technology GRs, 2018 to 2024"
}
```

## Q36: Is the 2022 GR on generative AI use in government offices in force?

**Gold:** No such 2022 GR in this corpus. Closest: the circular of 03-03-2020 on AI, Marathi language technology and NLP in government work; a good answer names it without claiming it is the GR asked for

Tokens: 19246 in (1344 cached), 431 out (0 reasoning). Cost Rs 0.1901. Latency 3.16 s.

Newer-GR candidates given: none

**Raw model reply:**

```json
{
 "asked_for_code": null,
 "candidates_reviewed": [
  {
   "code": "202003031509142811",
   "effect": "unrelated",
   "reason": "The GR discusses use of Artificial Intelligence and Natural Language Processing in government work, not generative AI in government offices."
  },
  {
   "code": "202211041809363311",
   "effect": "unrelated",
   "reason": "The GR discusses Telecom Infrastructure Policy, not generative AI in government offices."
  },
  {
   "code": "201802161919110111",
   "effect": "unrelated",
   "reason": "The GR discusses setting up of Global Fintech Hub and implementation of Fintech policy, not generative AI in government offices."
  },
  {
   "code": "202303301831230311",
   "effect": "unrelated",
   "reason": "The GR discusses setting up a task force to launch and implement 5G services, not generative AI in government offices."
  },
  {
   "code": "202302231826565311",
   "effect": "unrelated",
   "reason": "The GR discusses Standard Operating Procedures for implement eOffice, not generative AI in government offices."
  }
 ],
 "newer": [],
 "cited": [],
 "answer": "I couldn't find a GR on this in the corpus. The corpus covers Information Technology GRs from 2018 to 2024 and none of the retrieved GRs address generative AI use in government offices.",
 "status": "not_found"
}
```

**Corrections made by the checks:** none

**Flags (left in place):** 
- candidates not reviewed by the model: 201811301239595811, 201811301240117211, 201811061202283811, 201804201113320211, 201804201114401011, 201804201439329111

**Checked answer (product):**

```json
{
 "status": "not_found",
 "answer": "I couldn't find a GR on this in the corpus. The corpus covers Information Technology GRs from 2018 to 2024 and none of the retrieved GRs address generative AI use in government offices.",
 "cited": [],
 "newer": [],
 "coverage": "Information Technology GRs, 2018 to 2024"
}
```
## Assessment (before F1)

| Q | Raw answer vs gold | Main problem |
|---|---|---|
| 1 | Partly right. Found the 19-06-2019 deadline change (31.03.2020) and the 05-07-2019 data rules. Missed the 23-04-2021 GR (empanelment ended, buying moved to GeM), which the model called "unrelated". | Misjudged a candidate; the "latest" is wrong |
| 7 | Right: Rs 1,20,000 (12-04-2023), earlier Rs 85,000 | Wrong date in the raw reply (12-04-2024), fixed by the check |
| 11 | Failed: the reply echoes the input GR document instead of answering; no status | Malformed reply (looks like a prompt echo) |
| 30 | Right: "No newer GR found in this corpus (covers 2018 to 2024)"; DBT committee GR judged cites_only | Quote spliced across a page break (flagged); typo "11-05-2011" in the answer |
| 36 | Partly right: "I couldn't find a GR on this in the corpus", but it doesn't name the closest GR, the 03-03-2020 AI circular | Misses the closest GR |

**Checks:** 4 corrections in 2 questions. Q1: a wrong date in `newer` fixed (19-06-2018 to
19-06-2019), a junk citation dropped, and a title punctuation difference. Q7: a wrong date
fixed. Without the checks, the raw replies show wrong dates in 2 of 5 answers.

**Flag noise:** the "candidates not reviewed" flag also lists candidates of other
retrieved GRs (Q30, Q36), which don't bear on the asked-for GR. It should only count
candidates of the asked-for GR.
