"""
verify_setup.py
───────────────
Run this after `docker compose up -d` to confirm every service
is healthy and correctly configured.

Usage:
    python verify_setup.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

PASS = "  ✅"
FAIL = "  ❌"
WARN = "  ⚠️ "

def check_env_vars():
    print("\n── Environment Variables ──────────────────────")
    required = [
        "OPENAI_API_KEY",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "DATABASE_URL",
    ]
    all_ok = True
    for var in required:
        val = os.getenv(var)
        if val and val != f"sk-your-openai-api-key-here":
            print(f"{PASS} {var} is set")
        elif var == "OPENAI_API_KEY" and (not val or val == "sk-your-openai-api-key-here"):
            print(f"{FAIL} {var} — replace placeholder in .env!")
            all_ok = False
        else:
            print(f"{FAIL} {var} — missing!")
            all_ok = False
    return all_ok


def check_postgres():
    print("\n── PostgreSQL + pgvector ──────────────────────")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
        cur = conn.cursor()
        print(f"{PASS} PostgreSQL connection successful")

        # Check pgvector
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        row = cur.fetchone()
        if row:
            print(f"{PASS} pgvector extension loaded — version {row[1]}")
        else:
            print(f"{FAIL} pgvector extension NOT found — check init SQL ran correctly")

        # Check pg_trgm
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'pg_trgm';")
        if cur.fetchone():
            print(f"{PASS} pg_trgm extension loaded")
        else:
            print(f"{WARN} pg_trgm not loaded (optional but recommended)")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"{FAIL} PostgreSQL connection failed: {e}")
        print(f"       → Is the container running? Try: docker compose ps")
        return False


def check_openai():
    print("\n── OpenAI API ─────────────────────────────────")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        if "gpt-4o" in model_ids:
            print(f"{PASS} OpenAI API reachable — gpt-4o available")
        else:
            print(f"{WARN} OpenAI API reachable — gpt-4o not listed (check org access)")

        # Test embeddings
        resp = client.embeddings.create(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            input="test embedding"
        )
        dims = len(resp.data[0].embedding)
        print(f"{PASS} Embeddings working — dimensions: {dims}")
        return True

    except Exception as e:
        print(f"{FAIL} OpenAI API error: {e}")
        return False


def check_python_packages():
    print("\n── Python Packages ────────────────────────────")
    packages = {
        "langgraph": "langgraph",
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "openai": "openai",
        "psycopg2": "psycopg2-binary",
        "sqlalchemy": "sqlalchemy",
        "pgvector": "pgvector",
        "pandas": "pandas",
        "gradio": "gradio",
        "faker": "faker",
        "dotenv": "python-dotenv",
        "pydantic": "pydantic",
        "tenacity": "tenacity",
        "rich": "rich",
    }
    all_ok = True
    for module, pkg in packages.items():
        try:
            __import__(module)
            print(f"{PASS} {pkg}")
        except ImportError:
            print(f"{FAIL} {pkg} — run: pip install -r requirements.txt")
            all_ok = False
    return all_ok


def check_directory_structure():
    print("\n── Project Directory Structure ────────────────")
    dirs = [
        "database/init",
        "agent",
        "notebooks",
        "gradio_app",
    ]
    for d in dirs:
        if os.path.isdir(d):
            print(f"{PASS} {d}/")
        else:
            print(f"{WARN} {d}/ — missing, creating...")
            os.makedirs(d, exist_ok=True)
            print(f"       → Created {d}/")


if __name__ == "__main__":
    print("=" * 52)
    print("  Semantic Query Agent — Environment Verifier")
    print("=" * 52)

    results = []
    results.append(check_env_vars())
    check_directory_structure()
    results.append(check_python_packages())
    results.append(check_postgres())
    results.append(check_openai())

    print("\n" + "=" * 52)
    if all(results):
        print("  🎉 All checks passed — ready for Phase 2!")
    else:
        print("  ⚠️  Some checks failed — fix issues above before continuing.")
    print("=" * 52 + "\n")
