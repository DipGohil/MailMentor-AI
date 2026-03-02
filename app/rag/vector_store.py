import chromadb
from app.rag.embeddings import generate_embedding

client = chromadb.PersistentClient(path = "chroma_db")

collection = client.get_or_create_collection(
    name = "emails"
)

def add_email_vector(email_id, text, created_at):
    
    print("adding vectors: ", email_id)
    
    metadata = {}
    embedding = generate_embedding(text)
    
    if created_at:
        metadata["created_at"] = str(created_at)
    
    collection.add(
        ids=[str(email_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    
def search_email_vectors(query, n_results=5):

    query_embedding = generate_embedding(query)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    output = []

    if result["ids"]:

        for i in range(len(result["ids"][0])):
            output.append({
                "email_id": result["ids"][0][i],
                "content": result["documents"][0][i],
                "distance": result["distances"][0][i],
                "created_at": result["metadatas"][0][i].get("created_at")
            })

    return output
