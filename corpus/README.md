# Corpus

The 112 Information Technology department Government Resolutions (GRs) of the Government
of Maharashtra, 2018 to 2024, that the engine answers from.

- **Source:** [orgpedia/mahGRs](https://github.com/orgpedia/mahGRs), folder
  `GRs/Information_Technology_Department/`, by the Orgpedia Foundation.
- **Pinned commit:** `c96e88f731589e1284ecab60ff1a63d3b9c6bb82`.
- **Copied unchanged:** all 226 files of that folder at that commit, byte for byte, with
  no edits:
  - 224 text files, two per GR (see below);
  - `GRs.json`, the metadata the engine uses: official PDF link, date, title, GR number,
    order type and page count per GR;
  - `GRs-new.json`, a short update list kept for completeness (the engine doesn't read it).
- **Re-fetching:** run `scripts/fetch_corpus.sh` to fetch the folder again at the pinned
  commit and copy it here.

## Files per GR

| File | Content |
|---|---|
| `<code>.pdf.mr.txt` | Text of the official PDF in its original language (Marathi for most GRs, English for some). Pages start with `# Page N`. |
| `<code>.pdf.en.txt` | English version (machine translation for Marathi GRs) |

The code is an upload timestamp, not the GR's date. Use the `date` field in `GRs.json`.

## Licence

The corpus is used under the MIT licence of orgpedia/mahGRs. Its notice:

```
MIT License

Copyright (c) 2023 Orgpedia Foundation
```

The full notice is in [`../LICENSES/mahGRs-LICENSE.txt`](../LICENSES/mahGRs-LICENSE.txt).
The GRs themselves are public documents of the Government of Maharashtra.
