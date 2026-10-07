"""Count what is in github.com/openai/math.

Usage:  python3 catalog.py /path/to/clone-of-openai-math

It reads four things from the clone and prints plain counts:
  overview.tex                 the catalogue: subjects, result families, links to manuscripts
  lean/docs/NNN.md             one page per family that has a Lean formalization
  lean/ComparatorChallenges/   one statement file (.lean) and one config (.json) per checked theorem
  git ls-tree                  the list of every file, to count the Lean library

Nothing here judges whether a proof is right. It only counts what the repository says it contains.
"""
import collections
import json
import os
import re
import subprocess
import sys

MONTHS = {"September": 9, "October": 10}


def read_catalogue(root):
    """Return a list of families: number, title, description, subject, manuscript folders."""
    tex = open(os.path.join(root, "overview.tex"), encoding="utf-8").read()
    sections = [(m.start(), m.group(1)) for m in re.finditer(r"\\cataloguesection\{(.*?)\}\{\d+\}", tex)]
    families = []
    for m in re.finditer(r"\\resultentry\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\s*\n", tex, re.S):
        subject = [name for pos, name in sections if pos < m.start()][-1]
        folders = re.findall(r"preprints/([^/}]+)/[^}]+?\.pdf", m.group(4))
        families.append({"n": m.group(1), "title": m.group(2), "text": m.group(3),
                         "subject": subject, "folders": folders})
    return families


def folder_date(folder):
    """Manuscript folders end in a date: ...-September-23-2026 or ...-2026-09-24."""
    m = re.search(r"-(September|October)-(\d+)-2026$", folder)
    if m:
        return (MONTHS[m.group(1)], int(m.group(2)))
    m = re.search(r"-2026-(\d\d)-(\d\d)$", folder)
    return (int(m.group(1)), int(m.group(2)))


def read_lean_pages(root):
    """lean/docs/NNN.md -> the papers it covers and the challenge statements it links."""
    pages = {}
    d = os.path.join(root, "lean", "docs")
    for name in sorted(os.listdir(d)):
        text = open(os.path.join(d, name), encoding="utf-8").read()
        pages[name[:-3]] = {
            "papers": sorted(set(re.findall(r"preprints/([^/)]+)/", text))),
            "challenges": sorted(set(re.findall(r"ComparatorChallenges/(\w+)\.lean", text))),
        }
    return pages


def read_challenges(root):
    """Each challenge is a statement with the proof left out, plus a config naming the real proof."""
    d = os.path.join(root, "lean", "ComparatorChallenges")
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        cfg = json.load(open(os.path.join(d, name)))
        lean = open(os.path.join(d, name[:-5] + ".lean"), encoding="utf-8").read()
        body = [l for l in lean.split("\n") if l.strip()]
        out[name[:-5]] = {"theorems": cfg["theorem_names"], "axioms": cfg["permitted_axioms"],
                          "solution": cfg["solution_module"], "lines": len(body),
                          "sorries": len(re.findall(r"\bsorry\b", lean))}
    return out


def count_lean_files(root):
    """File names only; works in a clone made with --filter=blob:none."""
    r = subprocess.run(["git", "-C", root, "ls-tree", "-r", "--name-only", "HEAD"],
                       capture_output=True, text=True)
    files = [p for p in r.stdout.split("\n") if p.startswith("lean/OAI/") and p.endswith(".lean")]
    areas = collections.Counter(p.split("/")[2] for p in files)
    return len(files), areas


def main(root):
    fam = read_catalogue(root)
    pages = read_lean_pages(root)
    chal = read_challenges(root)
    papers = [f for x in fam for f in x["folders"]]

    print("CATALOGUE")
    print(f"  result families      {len(fam)}")
    print(f"  manuscripts          {len(papers)}")
    subj = collections.Counter(x["subject"] for x in fam)
    subj_papers = collections.Counter()
    subj_lean = collections.Counter()
    for x in fam:
        subj_papers[x["subject"]] += len(x["folders"])
        subj_lean[x["subject"]] += x["n"] in pages
    print(f"  subjects             {len(subj)}")
    print(f"  {'subject':44s} families  papers  with a Lean page")
    for s, n in subj.most_common():
        print(f"  {s:44s} {n:8d} {subj_papers[s]:7d} {subj_lean[s]:9d}")

    sizes = collections.Counter(len(x["folders"]) for x in fam)
    print(f"  families with 1 paper   {sizes[1]}")
    print(f"  largest family          {max(len(x['folders']) for x in fam)} papers")

    words = re.compile(r"[Cc]ounterexample|[Dd]isprov|[Rr]efut")
    neg = [x for x in fam if words.search(x["title"] + " " + x["text"])]
    print(f"  families whose entry says counterexample, disproves or refutes   {len(neg)}")

    print("\nDATES IN THE FOLDER NAMES")
    days = collections.Counter(folder_date(f) for f in papers)
    for (mo, d), n in sorted(days.items()):
        print(f"  2026-{mo:02d}-{d:02d}  {n:4d}  {'#' * (n // 4)}")
    first, last = min(days), max(days)
    print(f"  first 2026-{first[0]:02d}-{first[1]:02d}   last 2026-{last[0]:02d}-{last[1]:02d}")
    top2 = sorted(days.items(), key=lambda kv: -kv[1])[:2]
    print(f"  two busiest days hold {sum(n for _, n in top2)} of {len(papers)}")

    print("\nLEAN")
    covered = sorted(set(p for v in pages.values() for p in v["papers"]))
    print(f"  families with a Lean page       {len(pages)} of {len(fam)}  ({100 * len(pages) / len(fam):.1f}%)")
    print(f"  families without one            {len(fam) - len(pages)}")
    print(f"  manuscripts named on Lean pages {len(covered)} of {len(papers)}  ({100 * len(covered) / len(papers):.1f}%)")
    print(f"  challenge statements            {len(chal)}")
    linked = set(c for v in pages.values() for c in v["challenges"])
    print(f"  challenges linked from pages    {len(linked & set(chal))}")
    ax = collections.Counter(tuple(c["axioms"]) for c in chal.values())
    for a, n in ax.most_common():
        print(f"  permitted axioms {', '.join(a)}: {n} challenges")
    print(f"  theorems named in the configs   {sum(len(c['theorems']) for c in chal.values())}")
    lines = sorted(c["lines"] for c in chal.values())
    print(f"  statement length in lines: shortest {lines[0]}, median {lines[len(lines) // 2]}, longest {lines[-1]}")
    print(f"  statements of 20 lines or fewer {sum(1 for l in lines if l <= 20)}")
    for name in ("QuasiRiemannHypothesis", "EuclideanFiveColor", "PiExponent"):
        print(f"    {name:24s} {chal[name]['lines']} lines, proves {chal[name]['solution']}")
    no_challenge = [n for n, v in pages.items() if not v["challenges"]]
    print(f"  Lean pages that link no challenge  {len(no_challenge)}")
    nfiles, areas = count_lean_files(root)
    print(f"  Lean files in lean/OAI          {nfiles}")
    for a, n in areas.most_common(6):
        print(f"    {a:22s} {n}")

    yaml = open(os.path.join(root, "lean", "formalization.yaml"), encoding="utf-8").read()
    print(f"  formalization.yaml: papers {len(re.findall(r'id: ../preprints/', yaml))}, "
          f"main results {len(re.findall(r'comparator_config:', yaml))}, "
          f"review status {re.search(r'review:\s+status: (\w+)', yaml).group(1)}")

    print("\nTHE TEN FAMILIES WITH A REASONING SUMMARY")
    readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()
    ten = re.findall(r"^\| (\d{3}) \|", readme, re.M)
    byn = {x["n"]: x for x in fam}
    for n in ten:
        print(f"  {n}  {'Lean page' if n in pages else 'no Lean page':13s} {byn[n]['title'][:70]}")
    print(f"  with a Lean page: {sum(n in pages for n in ten)} of {len(ten)}")

    result = {
        "families": len(fam), "papers": len(papers),
        "subjects": [[s, n, subj_papers[s], subj_lean[s]] for s, n in subj.most_common()],
        "single": sizes[1], "largest": max(len(x["folders"]) for x in fam), "negative": len(neg),
        "days": [[f"{mo:02d}-{d:02d}", n] for (mo, d), n in sorted(days.items())],
        "top2": sum(n for _, n in top2),
        "leanFamilies": len(pages), "leanPapers": len(covered), "challenges": len(chal),
        "theorems": sum(len(c["theorems"]) for c in chal.values()),
        "lineShort": lines[0], "lineMedian": lines[len(lines) // 2], "lineLong": lines[-1],
        "le20": sum(1 for l in lines if l <= 20),
        "named": {n: chal[n]["lines"] for n in ("QuasiRiemannHypothesis", "EuclideanFiveColor", "PiExponent")},
        "leanFiles": nfiles, "areas": areas.most_common(6),
        "ten": [[n, n in pages] for n in ten],
        "noLean": [x["n"] for x in fam if x["n"] not in pages],
        "leanMap": "".join("1" if x["n"] in pages else "0" for x in sorted(fam, key=lambda x: x["n"])),
    }
    json.dump(result, open("catalog.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "math")
