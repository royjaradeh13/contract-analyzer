import json

CLAUSE_TYPES = [
    "Non-Compete",
    "Termination For Convenience",
    "Uncapped Liability",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
]


def load_contracts():
    """Load all 510 contracts from the CUAD dataset file."""
    with open("data/CUADv1.json", "r", encoding="utf-8") as f:
        cuad = json.load(f)
    return cuad["data"]


def get_clause_spans(contract, clause_type):
    """
    Return ALL labeled text spans for a clause type in one contract.
    Returns an empty list if the clause isn't present.
    """
    qas = contract["paragraphs"][0]["qas"]

    for qa in qas:
        if f'"{clause_type}"' in qa["question"]:
            return [answer["text"] for answer in qa["answers"]]

    raise ValueError(f"Unknown clause type: {clause_type}")


def has_clause(contract, clause_type):
    """Return True if the experts labeled this clause as present."""
    return len(get_clause_spans(contract, clause_type)) > 0


if __name__ == "__main__":
    contracts = load_contracts()

    for contract in contracts:
        if "KIROMICBIOPHARMA,INC_05_11_2020-EX-10.23" in contract["title"]:
            print(contract["title"], "\n")
            for clause_type in CLAUSE_TYPES:
                spans = get_clause_spans(contract, clause_type)
                print(f"{clause_type}: present={has_clause(contract, clause_type)}, spans={len(spans)}")
            break