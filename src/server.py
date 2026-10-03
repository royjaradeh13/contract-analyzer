from mcp.server.mcpserver import MCPServer
from contracts import load_contracts, get_clause_spans, CLAUSE_TYPES
from analyzer import analyze_contract, verify_quotes
from typing import Literal

mcp = MCPServer("contract-analyzer")

# Load the 510 contracts once, when the server starts, into a dictionary
# where the key is the title, so we can look any contract up instantly.
CONTRACTS = {c["title"]: c for c in load_contracts()}

ClauseType = Literal[
    "Non-Compete",
    "Termination For Convenience",
    "Uncapped Liability",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
]


@mcp.tool()
def list_contracts(limit: int = 20) -> list[str]:
    """List the titles of contracts available for analysis.

    Use this first when you don't know a contract's exact title.
    Input: limit, how many titles to return (default 20).
    Returns: a list of contract titles.
    """
    return list(CONTRACTS.keys())[:limit]


@mcp.tool()
def find_contracts(keyword: str, limit: int = 10) -> list[str]:
    """Search contract titles for a keyword (not case sensitive).

    Use this when you know part of a title, such as a company name,
    but not the exact title.
    Input: keyword, the text to look for, like "kiromic".
    Returns: a list of matching exact titles, to use with the other tools.
    """
    keyword = keyword.lower()
    matches = [title for title in CONTRACTS if keyword in title.lower()]
    return matches[:limit]


@mcp.tool()
def get_contract_text(title: str) -> str:
    """Get the full text of one contract.

    Input: title, the exact contract title from list_contracts.
    Returns: the contract text, or an error message if the title is unknown.
    """
    contract = CONTRACTS.get(title)
    if contract is None:
        return f"No contract found with title: {title}"
    return contract["paragraphs"][0]["context"]


@mcp.tool()
def get_expert_labels(title: str, clause_type: ClauseType) -> str:
    """Get the clause text that legal experts labeled in a contract.

    Input: title, the exact contract title; clause_type, one of:
    Non-Compete, Termination For Convenience, Uncapped Liability,
    Renewal Term, Notice Period To Terminate Renewal.
    Returns: the labeled text, or a message saying the clause is not present.
    """
    contract = CONTRACTS.get(title)
    if contract is None:
        return f"No contract found with title: {title}"
    if clause_type not in CLAUSE_TYPES:
        return f"Unknown clause type. Choose from: {', '.join(CLAUSE_TYPES)}"

    spans = get_clause_spans(contract, clause_type)
    if not spans:
        return f"Experts found no {clause_type} clause in this contract."
    return "\n\n".join(spans)


@mcp.tool()
def analyze_clause(title: str, clause_type: ClauseType) -> str:
    """Use AI to analyze whether a contract contains a specific clause type.

    Unlike get_expert_labels (which only returns pre-existing human labels),
    this tool runs a fresh AI analysis of the actual contract text, checks
    whether the found quote is genuinely present in the contract, and
    reports both the answer and whether it's verified.

    Input: title, the exact contract title; clause_type, one of:
    Non-Compete, Termination For Convenience, Uncapped Liability,
    Renewal Term, Notice Period To Terminate Renewal.
    Returns: the AI's finding, the supporting quote, and whether that
    quote was verified as genuinely present in the contract text.
    """
    contract = CONTRACTS.get(title)
    if contract is None:
        return f"No contract found with title: {title}"

    text = contract["paragraphs"][0]["context"]
    ai_result = analyze_contract(text)
    ai_result = verify_quotes(text, ai_result)

    answer = ai_result.get(clause_type)
    if answer is None:
        return f"Unknown clause type. Choose from: {', '.join(CLAUSE_TYPES)}"

    if not answer["present"]:
        return f"AI analysis: no {clause_type} clause found in this contract."

    verified_note = "verified as genuine" if answer["quote_verified"] else "⚠️ COULD NOT BE VERIFIED in contract text"
    return f"AI analysis: {clause_type} clause found ({verified_note}).\n\nQuote: {answer['quote']}"


@mcp.tool()
def analyze_full_contract(contract_text: str) -> str:
    """Analyze any contract text for all 5 risk clause types at once.

    Use this when a user pastes their own contract text and wants a
    full risk check. Unlike analyze_clause, this checks all 5 clause
    types in a single call and does not require a dataset contract title.

    Input: contract_text, the full text of any contract.
    Returns: a readable summary covering all 5 clause types, each
    marked as found or not found, with supporting quotes and
    verification status.
    """
    ai_result = analyze_contract(contract_text)
    ai_result = verify_quotes(contract_text, ai_result)

    lines = []
    for clause_type in CLAUSE_TYPES:
        answer = ai_result[clause_type]
        if not answer["present"]:
            lines.append(f"❌ {clause_type}: not found")
        else:
            note = "✅ verified" if answer["quote_verified"] else "⚠️ unverified"
            lines.append(f"✅ {clause_type}: FOUND ({note})\n   Quote: {answer['quote']}")

    return "\n\n".join(lines)


if __name__ == "__main__":
    mcp.run()