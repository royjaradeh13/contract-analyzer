from contracts import load_contracts
from analyzer import analyze_contract
import json

with open("testset.json", "r", encoding="utf-8") as f:
    testset = json.load(f)

contracts_by_title = {c["title"]: c for c in load_contracts()}

# Find one contract where the experts say Uncapped Liability IS present
for item in testset:
    if item["labels"]["Uncapped Liability"]:
        title = item["title"]
        break

contract = contracts_by_title[title]
text = contract["paragraphs"][0]["context"]

print(f"Testing: {title}\n")
result = analyze_contract(text)
print(json.dumps(result, indent=2))

from contracts import get_clause_spans

expert_spans = get_clause_spans(contract, "Uncapped Liability")
print(f"\nExpert-labeled spans ({len(expert_spans)}):\n")
for span in expert_spans:
    print(span, "\n")