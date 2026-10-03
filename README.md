# Contract Clause Risk Analyzer

An AI-powered MCP server that analyzes commercial contracts for legally significant clause types, built on the public CUAD (Contract Understanding Atticus Dataset) legal dataset.

> This is an MCP (Model Context Protocol) server. It needs to be connected to an MCP-compatible AI assistant (such as Claude Desktop) to be used, it isn't a standalone app you can just double-click.

## What it does

This tool checks any contract for 5 risk-relevant clause types:

- **Non-Compete** — restrictions on competing after the contract ends
- **Termination For Convenience** — whether either party can walk away with no reason, just notice
- **Uncapped Liability** — whether liability has no maximum dollar limit (including caps with exceptions that reintroduce unlimited liability)
- **Renewal Term** — how long the contract automatically renews for
- **Notice Period To Terminate Renewal** — how much notice is needed to stop an automatic renewal

For each clause type, it reports whether it was found, quotes the exact supporting text, and **verifies that the quote genuinely appears in the contract** (catching potential AI hallucination).

## How it works

1. **Data**: 510 real, expert-labeled contracts from [CUAD](https://github.com/TheAtticusProject/cuad), a public legal NLP dataset.
2. **Analysis**: contract text is sent to Claude (Haiku), with a carefully-tuned prompt that defines each clause type precisely to avoid common confusions (e.g., "termination for cause" vs. "termination for convenience").
3. **Verification**: every AI-claimed quote is checked against the actual contract text (with whitespace normalization to handle PDF-extraction artifacts like words split across line breaks).
4. **Delivery**: exposed as an MCP server, so any MCP-compatible AI assistant can call it directly.

## Measured accuracy

Tested against a random, fixed sample of 40 contracts (of the 510), compared to CUAD's expert legal labels:

| Clause Type | Accuracy |
|---|---|
| Renewal Term | 95%+ |
| Notice Period To Terminate Renewal | 90%+ |
| Non-Compete | 90% |
| Termination For Convenience | 82.5% |
| Uncapped Liability | 82.5% |

**Overall: 92.5% agreement with expert legal labels** across all 5 clause types.

These numbers came after two rounds of real debugging: an initial version scored 0% on Uncapped Liability (it couldn't detect caps-with-exceptions), and later testing revealed confusions between similar-sounding clause types (e.g., flagging "termination for cause" as "termination for convenience"). Both were fixed by sharpening the prompt's clause definitions based on reading actual mismatches, not by guessing.

## MCP Tools

| Tool | Description | Cost |
|---|---|---|
| `list_contracts` | Browse the 510 dataset contracts | Free |
| `find_contracts` | Search dataset contracts by keyword | Free |
| `get_contract_text` | Get a dataset contract's full text | Free |
| `get_expert_labels` | Look up CUAD's human-labeled answer for one clause type | Free |
| `analyze_clause` | Live AI analysis of one clause type, on a dataset contract | Paid (API call) |
| `analyze_full_contract` | Live AI analysis of **any pasted contract text**, all 5 clause types at once | Paid (API call) |

`analyze_full_contract` is the main entry point for real use: paste any contract text and get a full risk report.

## Setup

1. Clone this repo and `cd` into it.
2. Download the CUAD dataset from [the official repo](https://github.com/TheAtticusProject/cuad) and place `CUADv1.json` in `data/`.
3. Install dependencies: `pip install "mcp[cli]" anthropic python-dotenv`
4. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your-key-here`
5. Run the server: `mcp dev server.py`

## How to use it

Once the server is running, connect it to an MCP-compatible AI client (like Claude Desktop, or the MCP Inspector for testing: `mcp dev server.py` opens a test page in your browser).

### Option 1: Analyze your own contract

Call `analyze_full_contract` with your contract's text pasted in. You'll get a report like:

✅ Non-Compete: FOUND (✅ verified)
   Quote: "Consultant will not directly or indirectly participate in..."

❌ Termination For Convenience: not found

✅ Uncapped Liability: FOUND (✅ verified)
   Quote: "liability will in no event exceed the compensation paid..."

❌ Renewal Term: not found

❌ Notice Period To Terminate Renewal: not found

This works with any contract text: a lease, a freelance agreement, an NDA, anything you can copy as plain text. (PDF/Word file upload isn't supported yet, see Known Limitations.)

### Option 2: Explore the built-in dataset

1. `find_contracts("some company name")` → get an exact contract title
2. `get_contract_text(title)` → read its full text
3. `analyze_clause(title, "Non-Compete")` → get the AI's live analysis of one specific clause type for that contract
4. `get_expert_labels(title, "Non-Compete")` → compare against the human legal expert's original label (free, no AI call)

## Known limitations

- **Text only**: currently accepts plain contract text, not PDF or Word file uploads directly. Adding file parsing (via `pypdf` / `python-docx`) would be a natural next step.
- **Quote verification is exact-match (with whitespace normalization)**: it won't catch a quote that's paraphrased rather than verbatim, by design, since the goal is confirming the AI didn't invent text, not grading paraphrase quality.
- **5 clause types**, chosen deliberately from CUAD's 41 total categories, prioritizing types that are common enough to test reliably and distinct enough to verify independently. The pipeline generalizes to more clause types; this was a scoping decision to validate the approach thoroughly before widening it.
- **Measured on a 40-contract sample**, not the full 510, for cost reasons during development. The sample was randomly selected with a fixed seed for reproducibility.

## Project structure

```
contract-analyzer/
├── src/
│   ├── server.py         # MCP server, 6 tools
│   ├── analyzer.py       # AI analysis + quote verification
│   ├── contracts.py      # CUAD data loading + expert label lookup
│   ├── build_testset.py  # builds the 40-contract evaluation set
│   ├── evaluate.py       # runs full accuracy evaluation
│   └── data/              # CUAD dataset (not included, see Setup)
└── README.md
```