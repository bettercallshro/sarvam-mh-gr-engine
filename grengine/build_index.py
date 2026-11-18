"""E1: load the corpus, detect twins, build the citation graph, write the index.

Usage:
    python -m grengine.build_index [--corpus DIR] [--out DIR]

Writes:
    <out>/grs.json             metadata per GR (+ twin group, original language)
    <out>/pages.jsonl          one line per page: code, page, original text, English text,
                               and ASCII-digit normalised copies for matching
    <out>/twins.json           English/Marathi twin pairs
    <out>/citation_graph.json  edges (cites) and unresolved references
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from .citations import build_graph
from .corpus import COVERAGE, DEFAULT_CORPUS_DIR, load_corpus
from .dates import date_key
from .normalize import normalize
from .twins import find_twins, group_ids

DEFAULT_OUT = Path("data/index")


def _dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def build(corpus_dir: Path, out_dir: Path) -> dict:
    grs, failures = load_corpus(corpus_dir)
    grs.sort(key=lambda g: (date_key(g.date), g.code))
    twins = find_twins(grs)
    group_of = group_ids(grs, twins)
    graph = build_graph(grs, group_of)

    out_dir.mkdir(parents=True, exist_ok=True)
    _dump(out_dir / "grs.json", {
        "coverage": COVERAGE,
        "count": len(grs),
        "failures": failures,
        "grs": [{**g.meta(), "group": group_of[g.code]} for g in grs],
    })
    with (out_dir / "pages.jsonl").open("w", encoding="utf-8") as f:
        for g in grs:
            for p in sorted(set(g.pages_orig) | set(g.pages_en)):
                orig, en = g.pages_orig.get(p, ""), g.pages_en.get(p, "")
                f.write(json.dumps({
                    "code": g.code, "page": p,
                    "text_orig": orig, "text_en": en,
                    "norm_orig": normalize(orig), "norm_en": normalize(en),
                }, ensure_ascii=False) + "\n")
    _dump(out_dir / "twins.json", twins)
    _dump(out_dir / "citation_graph.json", graph)
    return {"grs": grs, "failures": failures, "twins": twins, "graph": graph, "group_of": group_of}


def report(result: dict) -> str:
    grs, twins, graph = result["grs"], result["twins"], result["graph"]
    by_code = {g.code: g for g in grs}
    lines = []
    lines.append(f"GRs loaded: {len(grs)}   failed: {len(result['failures'])}")
    for f in result["failures"]:
        lines.append(f"  FAILED {f['code']}: {f['reason']}")
    langs = Counter(g.original_lang for g in grs)
    lines.append(f"Original language: Marathi {langs['mr']}, English {langs['en']}")
    years = Counter(g.date[-4:] for g in grs)
    lines.append("By year: " + ", ".join(f"{y} {n}" for y, n in sorted(years.items())))
    pages = sum(len(g.pages_orig) for g in grs)
    lines.append(f"Pages: {pages}")
    zero = [g.code for g in grs if g.num_pages == 0]
    if zero:
        lines.append(f"Metadata num_pages is 0 for {len(zero)} GRs (text has pages): {', '.join(zero)}")
    lines.append(f"Distinct GRs after merging twins: {len(set(result['group_of'].values()))}")

    lines.append(f"\nTwin pairs: {len(twins)}")
    for t in twins:
        lines.append(f"  {t['date']}  EN {t['en_code']}  MR {t['mr_code']}  "
                     f"(similarity {t['similarity']})  {by_code[t['en_code']].title[:60]}")

    edges = graph["edges"]
    ev = Counter(e for x in edges for e in x["evidence"])
    lines.append(f"\nCitation edges: {len(edges)} "
                 f"(GRs citing: {len({e['from'] for e in edges})}, GRs cited: {len({e['to'] for e in edges})})")
    lines.append("  edges by evidence (an edge can have several): "
                 + ", ".join(f"{k} {v}" for k, v in sorted(ev.items())))
    strong = [e for e in edges if "date+order" in e["evidence"] or "order" in e["evidence"]]
    lines.append(f"  with an explicit number match (date+order or order): {len(strong)}")

    unresolved = graph["unresolved"]
    by_date = Counter(u["cited_date"] for u in unresolved)
    lines.append(f"\nUnresolved references (cited, not in corpus): {len(unresolved)} mentions, "
                 f"{len(by_date)} distinct dates")
    in_range = sorted({u["cited_date"] for u in unresolved if u["cited_date"][-4:] >= "2018"},
                      key=date_key)
    lines.append(f"  of which dated 2018 or later: {len(in_range)}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_DIR)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = build(args.corpus, args.out)
    print(report(result))
    print(f"\nIndex written to {args.out}/")


if __name__ == "__main__":
    main()
