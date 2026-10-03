import json
import random
from contracts import load_contracts

# FAKE analyze_contract, for testing the pipeline without spending API credits
def analyze_contract(contract_text):
    """Returns random-ish fake answers, just to test the pipeline logic."""
    fake_result = {}
    for clause_type in ["Non-Compete", "Termination For Convenience", "Uncapped Liability",
                         "Renewal Term", "Notice Period To Terminate Renewal"]:
        present = random.choice([True, False])
        fake_result[clause_type] = {
            "present": present,
            "quote": "This is a fake quote for testing." if present else ""
        }
    return fake_result


with open("testset.json", "r", encoding="utf-8") as f:
    testset = json.load(f)

contracts_by_title = {c["title"]: c for c in load_contracts()}

results = {}
for clause_type in testset[0]["labels"]:
    results[clause_type] = {"correct_yes": 0, "correct_no": 0, "false_yes": 0, "false_no": 0}

for i, item in enumerate(testset):
    title = item["title"]
    expert_labels = item["labels"]

    contract = contracts_by_title[title]
    text = contract["paragraphs"][0]["context"]

    print(f"[{i+1}/{len(testset)}] Analyzing: {title[:60]}...")

    try:
        ai_result = analyze_contract(text)
    except Exception as e:
        print(f"  FAILED: {e}")
        continue

    for clause_type, expert_says_yes in expert_labels.items():
        ai_says_yes = ai_result.get(clause_type, {}).get("present", False)

        if expert_says_yes and ai_says_yes:
            results[clause_type]["correct_yes"] += 1
        elif not expert_says_yes and not ai_says_yes:
            results[clause_type]["correct_no"] += 1
        elif not expert_says_yes and ai_says_yes:
            results[clause_type]["false_yes"] += 1
        else:
            results[clause_type]["false_no"] += 1

print("\n" + "=" * 60)
print("RESULTS (FAKE DATA - for testing the pipeline only)")
print("=" * 60)

for clause_type, counts in results.items():
    total = sum(counts.values())
    accuracy = (counts["correct_yes"] + counts["correct_no"]) / total * 100
    print(f"\n{clause_type}: {accuracy:.1f}% accuracy")
    print(f"  Correctly found: {counts['correct_yes']}")
    print(f"  Correctly said none: {counts['correct_no']}")
    print(f"  False alarms: {counts['false_yes']}")
    print(f"  Missed clauses: {counts['false_no']}")