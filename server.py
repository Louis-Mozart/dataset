import sqlite3
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Persona KB API")

DB_PATH = "personas.db"

def query_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/")
def root():
    """
    Welcome endpoint describing all available API routes.
    """
    return {
        "message": "Welcome to the Persona KB API!",
        "description": "This API allows you to retrieve persona descriptions from the knowledge base (up to 200,000).",
        "endpoints": {
            "/personas_random?limit=N": "Get N random persona descriptions (default 10). Limit max 200000.",
            "/personas?limit=N": "Get N persona descriptions sequentially (ordered by ID). Limit max 200000.",
            "/personas/{id}": "Get the description of a single persona by its ID.",
            "/personas_list?limit=N": "Get N persona descriptions formatted as a Python persona_list variable (default 10). Limit max 200000."
        },
        "examples": {
            "Random personas": "/personas_random?limit=10",
            "Sequential personas": "/personas?limit=10",
            "Single persona by ID": "/personas/42",
            "Formatted persona list": "/personas_list?limit=3"
        }
    }


# Get N random persona descriptions
@app.get("/personas_random")
def get_personas(limit: int = Query(10, le=200000)):
    return query_db("SELECT id, description FROM personas ORDER BY RANDOM() LIMIT ?", (limit,))

# Get N persona descriptions not randomly
@app.get("/personas")
def get_personas(limit: int = Query(10, le=200000)):
    return query_db("SELECT id, description FROM personas LIMIT ?", (limit,))

# Get one persona description by ID
@app.get("/personas/{persona_id}")
def get_persona(persona_id: int):
    result = query_db("SELECT id, description FROM personas WHERE id=?", (persona_id,))
    if not result:
        return {"error": "Persona not found"}
    return result[0]

# Get N persona descriptions formatted as a Python persona_list variable
@app.get("/personas_list", response_class=PlainTextResponse)
def get_personas_list(limit: int = Query(10, le=200000)):
    rows = query_db("SELECT id, description FROM personas LIMIT ?", (limit,))
    lines = ["persona_list = ["]
    for i, row in enumerate(rows):
        desc = row["description"].replace('"""', "'''")
        comma = "," if i < len(rows) - 1 else ""
        lines.append(f'    ("Persona_{row["id"]}", """')
        lines.append(f'    {desc.strip()}')
        lines.append(f'    """){comma}')
    lines.append("]")
    return "\n".join(lines)
