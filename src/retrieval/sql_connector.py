"""
sql_connector.py
Connects to a SQL database and executes natural language → SQL queries via LLM.
Supports SQLite (default) and PostgreSQL.
"""
import os
import sqlite3
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SQLConnector:
    def __init__(self, db_url: str = None):
        """
        db_url examples:
          SQLite:     "sqlite:///data/processed/knowledge.db"
          PostgreSQL: "postgresql://user:pass@localhost/dbname"
        """
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///data/processed/knowledge.db")
        self._setup_demo_db()

    def _setup_demo_db(self):
        """Create a demo SQLite database with sample business data."""
        if not self.db_url.startswith("sqlite"):
            return

        db_path = self.db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock INTEGER
            );
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER,
                total REAL,
                sale_date TEXT,
                customer TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                segment TEXT,
                city TEXT
            );
        """)

        # Insert demo data if empty
        if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", [
                (1, "Business Analytics Suite", "Software",   1200.00, 45),
                (2, "CRM Enterprise License",   "Software",    890.00, 30),
                (3, "AI Chatbot Module",         "AI Tools",    450.00,  8),
                (4, "Cloud Storage Plan",        "Cloud",       150.00, 60),
                (5, "Security Audit Package",    "Services",    750.00,  5),
            ])
            cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", [
                (1, "Acme Corp",       "acme@corp.com",    "Enterprise", "Bogotá"),
                (2, "TechNova SAS",    "tech@nova.com",    "SMB",        "Medellín"),
                (3, "Bright Solutions","bright@sol.com",   "Startup",    "Cali"),
                (4, "Delta Logistics", "delta@log.com",    "Enterprise", "Barranquilla"),
                (5, "Sigma Analytics", "sigma@anal.com",   "SMB",        "Bogotá"),
            ])
            cur.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?)", [
                (1,  1, 2, 2400.00, "2024-01-15", "Acme Corp"),
                (2,  2, 1,  890.00, "2024-01-20", "TechNova SAS"),
                (3,  3, 3, 1350.00, "2024-02-10", "Bright Solutions"),
                (4,  4, 5,  750.00, "2024-02-14", "Delta Logistics"),
                (5,  5, 1,  750.00, "2024-03-01", "Sigma Analytics"),
                (6,  1, 1, 1200.00, "2024-03-15", "Acme Corp"),
                (7,  2, 2, 1780.00, "2024-04-01", "TechNova SAS"),
                (8,  3, 1,  450.00, "2024-04-20", "Bright Solutions"),
                (9,  4, 10,1500.00, "2024-05-05", "Acme Corp"),
                (10, 5, 2, 1500.00, "2024-05-18", "Delta Logistics"),
            ])
            conn.commit()
            print("✅ Demo SQLite database created with sample data")

        conn.close()

    def get_schema(self) -> str:
        """Return the database schema as a string for the LLM."""
        if self.db_url.startswith("sqlite"):
            db_path = self.db_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            schema_parts = []
            for table in tables:
                cur.execute(f"PRAGMA table_info({table})")
                cols = cur.fetchall()
                col_str = ", ".join(f"{c[1]} {c[2]}" for c in cols)
                schema_parts.append(f"Table {table}: ({col_str})")
            conn.close()
            return "\n".join(schema_parts)
        return "Schema not available for this database type"

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as a list of dicts."""
        if self.db_url.startswith("sqlite"):
            db_path = self.db_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute(sql)
                rows = [dict(row) for row in cur.fetchall()]
                conn.close()
                return rows
            except Exception as e:
                conn.close()
                raise ValueError(f"SQL error: {e}")
        raise NotImplementedError("Only SQLite supported in demo mode")

    def natural_language_to_sql(self, question: str, llm_client) -> str:
        """Use LLM to convert a natural language question to SQL."""
        schema = self.get_schema()
        prompt = f"""You are a SQL expert. Convert the question to a valid SQLite query.

Database schema:
{schema}

Question: {question}

Rules:
- Return ONLY the SQL query, no explanation
- Use proper SQLite syntax
- Keep it simple and efficient
- Never use DROP, DELETE, UPDATE or INSERT

SQL query:"""

        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        sql = response.choices[0].message.content.strip()
        # Clean up markdown code blocks if present
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql
