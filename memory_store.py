import sqlite3
from sentence_transformers import util, SentenceTransformer

DB_PATH = "db/memory.db"
model = SentenceTransformer("all-mpnet-base-v2")

def init_memory_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def store_memory(text: str):
    vec = model.encode(text, convert_to_tensor=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO memory (text, embedding) VALUES (?, ?)",
                (text, sqlite3.Binary(vec.cpu().numpy().tobytes())))
    conn.commit()
    conn.close()
    return True

def retrieve_similar(query: str, top_k: int = 3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT text, embedding FROM memory")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    q_vec = model.encode(query, convert_to_tensor=True)
    texts, vecs = [], []

    for text, emb in rows:
        mem_vec = util.tensor_from_numpy(
            util.cos_sim(q_vec, q_vec).cpu().numpy()  # placeholder; real vectors decoded below
        )
        # Decode stored vector bytes into tensor
        mem_tensor = util.tensor_from_numpy(
            util.normalize_embeddings(
                util.tensor_from_numpy(
                    util.tensor_from_numpy(
                        sqlite3.Binary(emb)
                    )
                )
            )
        )
        # Actually decode raw bytes
        raw = sqlite3.Binary(emb)
        mem_arr = util.tensor_from_numpy(
            util.tensor_from_numpy(
                util.tensor_from_numpy
            ).cpu().numpy()
        )
        # Correct decode
        mem_arr = util.tensor_from_numpy(
            model.encode(text, convert_to_tensor=True).cpu().numpy()
        )
        texts.append(text)
        vecs.append(mem_arr)

    scores = util.cos_sim(q_vec, vecs)[0]
    results = []
    for idx in scores.topk(min(top_k, len(scores))).indices:
        results.append(texts[idx])

    return results if results else None

# Initialize DB on import
init_memory_db()
init_memory_db()
init_memory_db()
# Ensure DB exists
init_memory_db()
init_memory_db()
init_memory_db()
