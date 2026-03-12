import chromadb
from app.rag.embeddings import generate_embedding

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="emails"
)


# SINGLE EMAIL VECTOR (existing)

def add_email_vector(email_id, text, created_at=None):

    metadata = {
        "email_id": str(email_id)
    }

    if created_at:
        metadata["created_at"] = str(created_at)

    embedding = generate_embedding(text)

    collection.add(
        ids=[str(email_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    

# BATCH EMAIL EMBEDDING

def add_email_vectors_batch(emails):

    """
    emails format:
    [
        {
            "id": email_id,
            "text": email_text,
            "created_at": datetime
        }
    ]
    """

    print(f"Batch embedding {len(emails)} emails...")

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for e in emails:

        ids.append(str(e["id"]))
        documents.append(e["text"])

        metadata = {
            "email_id": str(e["id"])
        }
        if e.get("created_at"):
            metadata["created_at"] = str(e["created_at"])

        metadatas.append(metadata)

        # generate embedding
        emb = generate_embedding(e["text"])
        embeddings.append(emb)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print("Batch embedding completed.")



# VECTOR SEARCH

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