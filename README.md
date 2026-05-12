# GTM Hunter

Automated outreach pipeline that finds engineers using a competitor's technology and generates personalised LinkedIn messages using Claude. Configure any hunter company, competitor, and technology via CLI flags — no code changes needed.

A frontend dashboard is planned to allow simple configuration.

---

## How it works

1. **Company discovery** — finds companies known to use the target technology via StackShare API + GitHub org search (Mock mode uses a hardcoded list of target companies)
2. **Lead discovery** — finds engineers at those companies in relevant roles via LinkedIn/Proxycurl (Mock mode uses a hardcoded lead list)
3. **Filter + score** — drops non-technical roles and scores leads 0–100 based on seniority, technology signal, and engagement. Uses deterministic filtering with configurable weights
4. **AI personalisation** — generates a LinkedIn connection note (≤300 chars) and a follow-up email for each qualified lead using Claude. The LLM automatically figures out the pitch angle based on the hunter and competitor context
5. **Dry-run trigger** — logs what would have been sent to console and `output/dry_run_log.jsonl`
6. **Report** — saves all leads and messages to a SQLite database and exports a CSV + JSON report to `output/`

---

## Quickstart

```bash
# 1. Clone the repo.
git clone https://github.com/<YOUR_USERNAME>/gtm-hunter.git
cd gtm-hunter

# 2. Create and activate a virtual environment.
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies.
pip install -r requirements.txt

# 4. Add your Anthropic API key to .env.
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY.

# 5. Run the pipeline in mock mode (no other API keys needed).
python main.py run --mock \
  --hunter-company "<HUNTER_COMPANY>" \
  --competitor-company "<COMPETITOR_COMPANY>" \
  --competitor-technology "<COMPETITOR_TECHNOLOGY>"
```

---

## Campaign configuration

The pipeline is fully configurable via CLI flags. You can target any competitor without touching the code:

```bash

python main.py run --mock

# Target a different competitor
python main.py run --mock \
  --hunter-company "<HUNTER_COMPANY>" \
  --competitor-company "<COMPETITOR_COMPANY>" \
  --competitor-technology "<COMPETITOR_TECHNOLOGY>"
```

| Flag                      | Required | Default       | Description                                   |
| ------------------------- | -------- | ------------- | --------------------------------------------- |
| `--hunter-company`        | yes      | —             | Your company — who the messages are sent from |
| `--competitor-company`    | yes      | —             | The competitor whose users you're targeting   |
| `--competitor-technology` | yes      | —             | The technology the competitor is known for    |
| `--mock`                  | no       | off           | Use mock data instead of real APIs            |
| `--dry-run` / `--live`    | no       | `--dry-run`   | Log messages vs. send them                    |
| `--max-companies`         | no       | `10`          | How many target companies to process          |
| `--max-leads`             | no       | set in `.env` | Max leads to process across all companies     |

---

## Output

After a run you'll find:

```
output/
├── dry_run_log.jsonl       ← one JSON line per lead with both messages
├── report_{id}.csv         ← leads + messages in spreadsheet format
└── report_{id}.json        ← same data as JSON
```

The SQLite database `gtm_hunter.db` stores all leads, messages, and run reports.

The messages that were generated in the testing run: [view here](results/messages.md)

---

## Live mode

To run against real APIs, fill in the optional keys in `.env` and drop the `--mock` flag:

```bash
python main.py run
```

| Key                  | Used for                                                  |
| -------------------- | --------------------------------------------------------- |
| `STACKSHARE_API_KEY` | Find companies using the target technology via StackShare |
| `GITHUB_TOKEN`       | Find companies via GitHub org search (higher rate limits) |
| `PROXYCURL_API_KEY`  | Find engineers at target companies via LinkedIn           |

> [!NOTE]
> Live mode has not been end-to-end tested. Some APIs (StackShare, Proxycurl) require paid access or manual approval to obtain keys. The mock mode fully demonstrates the pipeline logic and is the intended way to run this prototype.

---

## Tech stack

**Why Python and not a no-code tool like n8n?** n8n is great for wiring together pre-built integrations, but this pipeline needs custom scoring logic, prompt engineering, structured DB writes, and the flexibility to swap sources or extend behaviour without fighting a GUI. Python gives full control over every step — the scoring weights, the prompt templates, the retry logic, the output format — with no black-box nodes in between. It's also easier for an engineering team to review, version, and test.

**Why LLM and not an agent?** The pipeline has a clear, fixed workflow — filter, score, generate, log. There's no need for autonomous decision-making or tool use (AI Agent). A plain LLM call at the personalisation step is more predictable, cheaper, and easier to debug.

| Tool                 | Why                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Anthropic Claude** | Generates personalised LinkedIn invites and follow-up emails                                                |
| **SQLAlchemy**       | ORM for storing leads, messages, and reports                                                                |
| **SQLite**           | Simple file-based DB, good for this demo. For production, we would swap SQLite with something like postgres |
| **Pydantic**         | Data validation and typed models throughout the pipeline                                                    |
| **httpx + tenacity** | Async HTTP calls with automatic retries for external APIs                                                   |
| **Click**            | CLI interface                                                                                               |

---

> [!NOTE]
> Scoring weights are in `scoring_weights.json` — adjust them to change how leads are ranked without touching code.
> Pipeline behaviour (threshold, max leads, dry run) is controlled via `.env`.

## Limitations

- The pipeline relies on the quality of data from external APIs (StackShare, GitHub, LinkedIn). Inaccurate or incomplete data may lead to missed leads or false positives.
- This is a prototype and has not been tested at scale. Performance may degrade with large datasets or API rate limits.
- The project doesn't include safety checks for the generated messages. In a production system, we would want to implement filters to ensure messages are appropriate and won't harm our brand reputation.
- Logs: The dry-run logs are currently stored in a JSONL file, which is simple but not ideal for querying or analysis. In a production system, we would want to implement a more robust logging solution, potentially with structured logging to a service like Datadog.

## Future improvements

- The project was built with JSON for the output as well as the scoring weights, giving us the flexibility to add a frontend dashboard in the future where we can adjust the scoring weights and thresholds without having to change the code.
- Implement a feedback loop to flag leads where message generation fails, allowing for prompt tweaks and retries.
- Add more data sources for company and lead discovery to improve coverage.
- Implement a more sophisticated scoring algorithm, potentially using LLMs to predict lead quality based on their profile and activity after the deterministic scoring step.
- Add a cron job to run the pipeline on a regular basis and update the database and reports.
