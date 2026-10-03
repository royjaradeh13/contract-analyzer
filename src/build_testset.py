import json
import random
from contracts import load_contracts, has_clause, CLAUSE_TYPES

SAMPLE_SIZE = 40

contracts = load_contracts()

random.seed(42)
sample = random.sample(contracts, SAMPLE_SIZE)

testset = []
for contract in sample:
    labels = {}
    for clause_type in CLAUSE_TYPES:
        labels[clause_type] = has_clause(contract, clause_type)
    testset.append({"title": contract["title"], "labels": labels})

with open("testset.json", "w", encoding="utf-8") as f:
    json.dump(testset, f, indent=2)

print(f"Saved {len(testset)} contracts to testset.json\n")

for clause_type in CLAUSE_TYPES:
    yes_count = sum(1 for item in testset if item["labels"][clause_type])
    print(f"{clause_type}: {yes_count} yes, {SAMPLE_SIZE - yes_count} no")