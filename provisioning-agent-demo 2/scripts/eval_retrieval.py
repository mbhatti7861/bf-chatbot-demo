"""Retrieval evaluation harness (rag-architect lens).

Principle: "a RAG pipeline without retrieval metrics is an untested hypothesis."
This runs a golden query set against the document connectors (Knowledge Base +
Confluence) and reports hit@k / precision@k / MRR. It works in either vector mode
(Titan + FAISS) or the keyword fallback, and prints which backend was live.

Run:  python scripts/eval_retrieval.py
Exit code is non-zero if hit@3 falls below TARGET_HIT3 (so it can gate CI later).
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import sources  # noqa: E402

TARGET_HIT3 = 0.90

# Golden set: query -> the document id(s) that should be retrieved. Multiple ids
# mean any of them counts as relevant (some questions are answered by >1 doc).
GOLDEN = [
    {"q": "how long does CIDR generation take",                 "src": "kb", "rel": ["STEP-100"]},
    {"q": "how does the vending machine update the CMDB",       "src": "kb", "rel": ["STEP-400"]},
    {"q": "what QA checks are expected to fail for CICD",       "src": "kb", "rel": ["STEP-900"]},
    {"q": "decommission idle 60 days policy",                   "src": "kb", "rel": ["POLICY-DECOM"]},
    {"q": "intake order files parameter metadata feature",      "src": "kb", "rel": ["STEP-10"]},
    {"q": "non routable CIDR block standard for accounts",      "src": "kb", "rel": ["POLICY-CIDR", "STEP-400-PARAMS"]},
    {"q": "standard change pre-approved scheduling for build",  "src": "kb", "rel": ["STEP-300", "POLICY-CHANGE-WINDOW"]},
    {"q": "remove yourself from all LZ roles after QA",         "src": "kb", "rel": ["STEP-900", "POLICY-ACCESS-HYGIENE"]},

    {"q": "what are all the steps in the build process",        "src": "confluence", "rel": ["CLOUD-STEPCATALOG", "CLOUD-OVERVIEW"]},
    {"q": "reference architecture SQS queue manager lambda",    "src": "confluence", "rel": ["CLOUD-ARCH"]},
    {"q": "when can a landing zone be decommissioned",          "src": "confluence", "rel": ["CLOUD-DECOM-FAQ"]},
    {"q": "meeting notes CIDR generation about 10 minutes",     "src": "confluence", "rel": ["CLOUD-SYNC-20260605"]},
]

K_VALUES = (1, 3, 5)


def _doc_id(citation: str) -> str:
    return citation.rsplit("/", 1)[-1]


def _search(src: str, query: str):
    fn = sources.search_kb if src == "kb" else sources.search_confluence
    return [_doc_id(h["citation"]) for h in fn(query)]


def evaluate():
    results = []
    for item in GOLDEN:
        hits = _search(item["src"], item["q"])
        rel  = set(item["rel"])
        rank = next((i + 1 for i, h in enumerate(hits) if h in rel), None)
        results.append({"item": item, "hits": hits, "rank": rank})
    return results


def _metrics(results):
    n = len(results)
    hit = {k: sum(1 for r in results if r["rank"] and r["rank"] <= k) / n for k in K_VALUES}
    mrr = sum((1.0 / r["rank"]) if r["rank"] else 0.0 for r in results) / n
    return hit, mrr


def main():
    # Warm indexes so the backend (vector vs keyword) is known.
    try:
        sources.warmup()
    except Exception:
        pass
    backend = sources.retrieval_backend()

    results = evaluate()
    hit, mrr = _metrics(results)

    print(f"\nRetrieval evaluation -- backend: {backend}  ({len(GOLDEN)} golden queries)\n")
    print(f"  {'query':<52} {'rank':>4}  hit@3")
    print("  " + "-" * 68)
    for r in results:
        rank = r["rank"]
        mark = "Y" if rank and rank <= 3 else "-"
        rstr = str(rank) if rank else "-"
        print(f"  {r['item']['q'][:52]:<52} {rstr:>4}  {mark}")

    print("\n  Metrics")
    for k in K_VALUES:
        print(f"    hit@{k}: {hit[k]:.2f}")
    print(f"    MRR:   {mrr:.3f}")

    ok = hit[3] >= TARGET_HIT3
    print(f"\n  {'PASS' if ok else 'BELOW TARGET'} -- hit@3 {hit[3]:.2f} (target >= {TARGET_HIT3:.2f})\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
