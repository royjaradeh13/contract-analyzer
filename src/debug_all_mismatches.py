import json
from contracts import load_contracts, get_clause_spans
from analyzer import analyze_contract

with open("testset.json", "r", encoding="utf-8") as f:
    testset = json.load(f)

contracts_by_title = {c["title"]: c for c in load_contracts()}

mismatches = []

for i, item in enumerate(testset):
    title = item["title"]
    expert_labels = item["labels"]
    contract = contracts_by_title[title]
    text = contract["paragraphs"][0]["context"]

    print(f"[{i+1}/{len(testset)}] {title[:50]}...")
    ai_result = analyze_contract(text)

    for clause_type, expert_says_yes in expert_labels.items():
        ai_says_yes = ai_result.get(clause_type, {}).get("present", False)
        if ai_says_yes != expert_says_yes:
            mismatches.append({
                "title": title,
                "clause_type": clause_type,
                "expert_says": expert_says_yes,
                "ai_says": ai_says_yes,
                "ai_quote": ai_result[clause_type].get("quote", ""),
            })

with open("mismatches.json", "w", encoding="utf-8") as f:
    json.dump(mismatches, f, indent=2)

print(f"\nFound {len(mismatches)} mismatches. Saved to mismatches.json")

from collections import Counter
counts = Counter(m["clause_type"] for m in mismatches)
for clause_type, count in counts.items():
    print(f"  {clause_type}: {count} mismatches")