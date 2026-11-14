from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np

class EmbeddingCache:
    model = SentenceTransformer("all-MiniLM-L6-v2")

    @staticmethod
    def init_db():
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS embedding_cache (
            query TEXT PRIMARY KEY,
            vector BLOB
        )
        """)
        con.commit()
        con.close()
        print("Embedding Cache DB Initialized ✔")

    @staticmethod
    def get_embedding(query):
        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("SELECT vector FROM embedding_cache WHERE query=?", (query,))
        row = cur.fetchone()
        con.close()

        if row:
            return np.frombuffer(row[0], dtype=np.float32)

        vec = EmbeddingCache.model.encode(query).astype(np.float32)

        con = sqlite3.connect("config/assistant.db")
        cur = con.cursor()
        cur.execute("INSERT INTO embedding_cache(query, vector) VALUES(?,?)",
                    (query, vec.tobytes()))
        con.commit()
        con.close()

        return vec

    @staticmethod
    def clear():
        con = sqlite3.connect("config/assistant.db")
        con.execute("DELETE FROM embedding_cache")
        con.commit()
        con.close()
        return {"status": "cleared"}
