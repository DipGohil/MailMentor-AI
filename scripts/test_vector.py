from app.rag.vector_store import collection

results = collection.query(
    query_texts=["job offer"],
    n_results=2
)

print(results)