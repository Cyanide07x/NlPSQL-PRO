# Audex — Natural Language Interface for SQL Querying

Audex lets anyone query a database by typing a plain-English question instead of writing SQL. It parses the question using either regex-based rules or an LLM (via Groq), runs the resulting SQL against a database, and returns the result through a simple web UI — no SQL knowledge required.

**Repo:** https://github.com/Cyanide07x/NlPSQL-PRO

---

## Features

- Convert plain-English questions into SQL queries
- Dual parsing: fast regex-based rules, with an LLM (Groq) fallback for complex phrasing
- User accounts (sign up / log in) so queries can be tied to a user
- Simple web interface to type a question and see results

## Why I built this

Most people who actually need answers from a database — analysts, ops folks, non-technical stakeholders — can't write SQL. They either wait for an engineer or choose not to ask the question. Audex removes that gap by turning a normal English sentence into a working query.

## Example

```
Input:  "show me the top 5 customers by total orders last month"
Output: SELECT customer_name, COUNT(order_id) AS total_orders
        FROM orders
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY customer_name
        ORDER BY total_orders DESC
        LIMIT 5;
```


## How it works

1. **Auth** — users sign up / log in (`auth.py`, `user_db.py`) before querying.
2. **Input parsing** — the plain-English question is parsed one of two ways:
   - `nlp_rules.py` — rule-based parsing using regex pattern matching for intent, entities, filters, and aggregations.
   - `nlp_groq.py` — LLM-based parsing via the Groq API, for phrasing the rules engine can't handle.
3. **Query construction** — parsed components are mapped to a valid SQL query (`models.py`, `db.py`).
4. **Execution** — the query runs against the database.
5. **Response** — results are rendered to the user through the web UI (`templates/`, `static/`).

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQL (via `db.py` / `models.py`)
- **NLP:** Rule-based parsing (regex) + LLM-based parsing (Groq API)
- **Auth:** Custom auth layer (`auth.py`, `user_db.py`)
- **Frontend:** HTML, CSS, JavaScript (Flask templates)

## Architecture

```
User Query (English)
      │
      ▼
   Auth Check (auth.py / user_db.py)
      │
      ▼
 NLP Parser ─── nlp_rules.py (regex)
      │    └── nlp_groq.py (Groq LLM)
      ▼
 SQL Query Builder (models.py / db.py)
      │
      ▼
      Database
      │
      ▼
  Rendered Result (templates/)
```

## Getting started

### Prerequisites
- Python 3.x
- MySQL Server
- pip

### Installation

```bash
git clone https://github.com/Cyanide07x/NlPSQL-PRO.git
cd NlPSQL-PRO
pip install -r requirements.txt
```

### Configuration

Update your credentials in `config.py`:

```
GROQ_API_KEY = "your_groq_api_key"
DB_HOST = "localhost"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "your_database"
```

Get a Groq API key from [console.groq.com](https://console.groq.com).

### Run

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

## Project structure

```
NlPSQL-PRO/
├── app.py              # Flask app entry point
├── auth.py              # User authentication
├── config.py             # Config / API keys (e.g. GROQ_API_KEY)
├── db.py                # Database connection
├── models.py             # Data models / query building
├── nlp_groq.py            # LLM-based parsing (Groq API)
├── nlp_rules.py           # Rule-based parsing (regex)
├── user_db.py            # User data storage
├── run.py               # App runner
├── requirements.txt
├── static/              # CSS / JS assets
├── templates/            # HTML pages (Flask/Jinja)
└── README.md
```

## Limitations

- The rule-based parser (`nlp_rules.py`) is fast and free but breaks on phrasings it wasn't written for; the Groq-based parser (`nlp_groq.py`) handles a wider range of phrasing but depends on an external API and incurs latency/cost.
- Currently supports [list supported query types — e.g. SELECT with filters, grouping, ordering, basic aggregations].
- No support yet for [joins across multiple tables / nested subqueries / etc. — edit to match reality].

## What I'd do differently today

Early on, I planned to rely purely on regex-based rules, but that broke the moment a question was phrased in a way I hadn't anticipated. I've since added an LLM-based path (`nlp_groq.py`) using the Groq API for exactly this reason — I'd start there from day one next time instead of treating it as a fallback, and use the rules engine only for a fast/cheap first pass on the most common query patterns.

## Roadmap

- [ ] Support multi-table joins
- [ ] Add query history / saved queries per user
- [ ] Smarter routing between rules-based and Groq-based parsing (use rules first, fall back to Groq only when confidence is low)
- [ ] Add tests / CI

## Author

**Utsav Sachan**
[GitHub](https://github.com/Cyanide07x) · [LinkedIn](https://www.linkedin.com/in/utsav-sachan-7759b4250/) · utsav0724@gmail.com

## License

MIT
