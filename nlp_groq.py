# nlp_groq.py
import os
from typing import Optional, Tuple

from groq import Groq
from config import Config

SYSTEM_PROMPT = """You are a Text-to-SQL assistant.
- Generate a single SQL query for the given natural language question.
- Only output valid SQL, no explanations.
- Target database is: {db_type}.
- Schema:
{schema}
- Use column and table names exactly as in the schema.
- Do NOT generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE statements.
"""

FORBIDDEN = ["insert", "update", "delete", "drop", "alter", "truncate"]

def nl_to_sql_with_groq(
    question: str,
    schema_description: str,
    db_type: str = "MySQL",
) -> Tuple[Optional[str], Optional[str]]:
    if not Config.GROQ_API_KEY:
        return None, "Groq API key not configured."

    try:
        # lazy init here instead of at import time
        client = Groq(api_key=Config.GROQ_API_KEY)
    except Exception as e:
        return None, f"Groq client init error: {e}"

    try:
        system = SYSTEM_PROMPT.format(db_type=db_type, schema=schema_description)
        completion = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
        sql = completion.choices[0].message.content.strip()
        l = sql.lower()
        if any(word in l for word in FORBIDDEN):
            return None, "Generated query looks unsafe (write operation)."
        return sql, None
    except Exception as e:
        return None, f"Groq error: {e}"