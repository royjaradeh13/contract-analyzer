import json

# Open the big CUAD file and load it into memory as a Python dictionary
with open("data/CUADv1.json", "r", encoding="utf-8") as f:
    cuad = json.load(f)

# The real contracts are inside cuad["data"], as a list
contracts = cuad["data"]
print(f"Total contracts: {len(contracts)}")

# Let's look at just the first one
first = contracts[0]
print(f"\nTitle: {first['title']}")

# Each contract has 'paragraphs', and inside that, 'qas' (question-answers)
first_paragraph = first["paragraphs"][0]
qas = first_paragraph["qas"]
print(f"Number of clause-questions for this contract: {len(qas)}")

# Print the first 2 questions and their answers
for qa in qas[:2]:
    print(f"\nQuestion: {qa['question']}")
    if qa["answers"]:
        print(f"Answer found: {qa['answers'][0]['text'][:200]}")
    else:
        print("Answer found: (none, this clause type isn't in this contract)")