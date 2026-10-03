import json
import re
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

PROMPT_TEMPLATE = """You are reviewing a commercial contract. For each of the following clause types, decide if the contract contains it. Be precise about the definitions below, several of these are easy to confuse with similar-sounding clauses.

Clause types and precise definitions:

- Non-Compete: an actual restriction, stated in THIS contract, preventing a party from competing or engaging in similar business. Do NOT count a "whereas" recital that merely mentions or references a separately-named "Non-Competition Agreement" without restating the restriction itself.

- Termination For Convenience: either party may end the contract for NO REASON at all, just by giving notice. Do NOT count termination that requires a specific reason or cause (e.g., breach, insolvency, bankruptcy, illegality, failure to meet a legal requirement). Those are "termination for cause," a different and more restrictive concept.

- Uncapped Liability: a statement that liability has NO maximum dollar limit, or a cap that has a stated exception making it unlimited for specific situations. Do NOT count clauses about "irreparable harm," "injunctive relief," or damages being "difficult to ascertain," those justify a court order (an injunction), not an absence of a liability cap, and are a different legal concept.

- Renewal Term: how long the contract AUTOMATICALLY renews for, with no action needed from either party (e.g., "renews for successive one-year terms unless cancelled," or continues "month to month"). Do NOT count renewal that requires both parties to proactively agree in writing, that is a negotiated renewal, not automatic.

- Notice Period To Terminate Renewal: specifically, how much advance notice is needed to STOP an AUTOMATIC renewal from happening. This only applies when renewal is automatic by default. Do NOT count a deadline for both parties to mutually agree to renew, that is a different (opt-in) structure, not something to "terminate."

Special note on "Uncapped Liability": contracts often state a liability cap, but then carve out exceptions elsewhere (phrases like "except as provided in Section X" or "except for breaches of confidentiality"). If such an exception exists, liability becomes uncapped for those specific situations, so treat this as "present." Read the full contract text for any exception language, not just the main cap sentence.

Contract text:
{contract_text}

Respond with ONLY a JSON object, no other text, in this exact format. If a quote contains double quotation marks (e.g. a defined term like "Competitive Business"), escape them as \\" so the JSON stays valid:
{{"Non-Compete": {{"present": true, "quote": "..."}}, ...}}

For each clause type: "present" is true or false. "quote" is the exact sentence from the contract if present, or an empty string if not."""


def analyze_contract(contract_text):
    """Send one contract to Claude and get yes/no + quote for each clause type."""
    prompt = PROMPT_TEMPLATE.format(contract_text=contract_text)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("Could not parse this as JSON:\n")
        print(raw_text)
        raise


def verify_quotes(contract_text, ai_result):
    """
    Check that every quote the AI gave actually appears in the contract text.
    Adds a "quote_verified" field to each clause's result.
    Whitespace differences (line breaks, extra spaces, and
    hyphen-breaks from PDF extraction) are ignored.
    """
    normalized_contract = re.sub(r"\s+", " ", contract_text)
    normalized_contract = re.sub(r"-\s+", "-", normalized_contract)

    for clause_type, answer in ai_result.items():
        if answer["present"] and answer["quote"]:
            normalized_quote = re.sub(r"\s+", " ", answer["quote"])
            normalized_quote = re.sub(r"-\s+", "-", normalized_quote)
            answer["quote_verified"] = normalized_quote in normalized_contract
        else:
            answer["quote_verified"] = None
    return ai_result


if __name__ == "__main__":
    from contracts import load_contracts

    contracts = load_contracts()
    test_contract = None
    for c in contracts:
        if "kiromic" in c["title"].lower():
            test_contract = c
            break

    text = test_contract["paragraphs"][0]["context"]
    result = analyze_contract(text)
    result = verify_quotes(text, result)


    print(f"Contract: {test_contract['title']}\n")
    for clause_type, answer in result.items():
        print(f"{clause_type}: present={answer['present']}, quote_verified={answer['quote_verified']}")
        if answer["present"]:
            print(f"  Quote: {answer['quote']}\n")


    