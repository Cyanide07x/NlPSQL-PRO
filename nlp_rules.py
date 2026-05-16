# nlp_rules.py
import re
from typing import Optional, Tuple

DEPARTMENT_SYNONYMS = {
    "cse": ["cse", "computer science", "cs"],
    "ece": ["ece", "electronics", "electronics and communication"],
    "me": ["mechanical", "me"],
}

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[?.,!]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _match_department(query: str) -> Optional[str]:
    for dept_code, synonyms in DEPARTMENT_SYNONYMS.items():
        for term in synonyms:
            if re.search(rf"\b{re.escape(term)}\b", query):
                return dept_code.upper()
    return None

def parse_query(nl_query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to generate SQL for known student-domain patterns.
    Returns (sql, error_message).
    """
    q = normalize_text(nl_query)

    # Show/list all students
    if re.search(r"\b(show|list|display|get)\b", q) and \
       re.search(r"\ball students\b", q):
        sql = "SELECT studentid, name, age, gender, department FROM students;"
        return sql, None

    # List students in department
    if re.search(r"\bstudents\b", q) and re.search(r"\b(in|from)\b", q):
        dept = _match_department(q)
        if dept:
            sql = (
                "SELECT studentid, name, age, gender, department "
                "FROM students WHERE department = %s;"
            )
            return sql, None

    # How many students in department
    if re.search(r"\bhow many\b", q) and re.search(r"\bstudents\b", q):
        dept = _match_department(q)
        if dept:
            sql = (
                "SELECT COUNT(*) AS count "
                "FROM students WHERE department = %s;"
            )
            return sql, None

    # Show grades of student <id>
    m = re.search(r"student\s+(\d+)", q)
    if m and re.search(r"\bgrade|grades\b", q):
        sql = (
            "SELECT s.studentid, s.name, c.coursename, e.semester, e.grade "
            "FROM enrollments e "
            "JOIN students s ON s.studentid = e.studentid "
            "JOIN courses c ON c.courseid = e.courseid "
            "WHERE s.studentid = %s;"
        )
        return sql, None

    # List courses in department
    if re.search(r"\bcourses?\b", q) and re.search(r"\b(in|from)\b", q):
        dept = _match_department(q)
        if dept:
            sql = (
                "SELECT courseid, coursename, department, credits "
                "FROM courses WHERE department = %s;"
            )
            return sql, None

    return None, "pattern_not_matched"

def extract_params(nl_query: str) -> tuple:
    q = normalize_text(nl_query)
    dept = _match_department(q)
    if dept:
        return (dept,)
    m = re.search(r"student\s+(\d+)", q)
    if m:
        return (int(m.group(1)),)
    return ()