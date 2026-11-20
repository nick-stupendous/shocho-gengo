"""data/raw/hanabira_jlpt_n*_grammar.csv -> data/grammar/N*.json + data/books.json"""
import csv, json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# first match wins; patterns run on lowercased Meaning + pattern. HEURISTIC: review the 'other' bucket.
RULES = [
 ("sentence_ending", r"sentence[- ]ending|end of (a |the )?sentence|seeking agreement|tag question|final particle"),
 ("particles",       r"\bparticle\b"),
 ("honorific",       r"honorific|humble|respectful|polite request"),
 ("giving",          r"\bgive\b|giving|\breceiv|do (a )?favou?r|on behalf"),
 ("voice",           r"passive|causative|potential|be able to|\bcan do\b|ability"),
 ("conditionals",    r"\bif\b|conditional|provided that|in case|\bwhen\b.*\bthen\b"),
 ("obligation",      r"\bmust\b|have to|need to|not allowed|permission|prohibit|\bmay\b|forbid|don't have to|need not"),
 ("desire",          r"\bwant|\bwish|desire|volition|intend|intention|plan to|let's|decid"),
 ("suggestion",      r"suggest|advice|advise|request|\bplease\b|why don't|\bshould\b|invit|offer"),
 ("conjecture",      r"seem|appear|apparently|hearsay|\bheard\b|they say|probabl|likely|maybe|perhaps|conjecture|looks like|supposed"),
 ("contrast",        r"although|\bbut\b|however|despite|even though|even if|contrast|whereas|in spite"),
 ("cause",           r"because|reason|\bcause|due to|\bsince\b|therefore|so that|as a result"),
 ("purpose",         r"\bpurpose\b|\baim\b|in order to|for the sake|\bgoal\b|so as to"),
 ("comparison",      r"compar|superlative|more than|\bmost\b|\bthan\b|similar|same as|resembl|\bleast\b"),
 ("time",            r"\bwhen\b|\bwhile\b|before|after|during|until|sequence|already|\bjust\b|\bstill\b|beginning|start"),
 ("quantity",        r"\bonly\b|about|approximately|at least|at most|limit|extent|degree|amount|quantity|too much|enough|per\b|every"),
 ("quotation",       r"quot|nominaliz|noun phrase|turn.* into a noun"),
 ("emphasis",        r"emphasi|feeling|surprise|strong|exclam|indeed|really|\beven\b"),
 ("forms",           r"form of|conjugat|te-form|ta-form|nai-form|stem|negative|past tense|plain form|present tense|progressive|continu"),
]
RULES = [(c, re.compile(p)) for c, p in RULES]

def categorize(pattern, meaning):
    t = f"{meaning} {pattern}".lower()
    for cat, rx in RULES:
        if rx.search(t): return cat
    return "other"

def main():
    (ROOT / "data/grammar").mkdir(parents=True, exist_ok=True)
    books = {}
    for f in sorted((ROOT / "data/raw").glob("hanabira_jlpt_n*_grammar.csv")):
        level = re.search(r"_(n\d)_", f.name).group(1).upper()
        rows = []
        with open(f, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                pat = r["Grammar Point"].split(" (")[0].strip()
                rows.append({"id": len(rows), "level": level, "pattern": pat,
                             "meaning": r["Meaning"], "formation": r.get("Formation", ""),
                             "ja": r["Example (Japanese)"], "romaji": r["Example (Romaji)"],
                             "en": r["Example (English)"], "category": categorize(pat, r["Meaning"])})
        (ROOT / f"data/grammar/{level}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        books[level] = {"file": f.name, "count": len(rows), "categories": dict(collections.Counter(x["category"] for x in rows))}
        print(level, len(rows), books[level]["categories"])
    (ROOT / "data/books.json").write_text(json.dumps(books, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
