import os
import chromadb
import numpy as np
from dotenv import load_dotenv
from typing import List, Dict, Any
from chromadb.config import Settings
from Anna_pipeline.config import RAGConfig
from Anna_pipeline.embeddings import EmbeddingGenerator

load_dotenv()

chroma_key = os.getenv("CHROMA_CLOUD")
tenant_key = os.getenv("CHROMA_TENANT")
chroma_database = os.getenv("CHROMA_DATABASE")


class VectorStore:
    def __init__(self):
        self.config = RAGConfig()
        self.embedding_generator = EmbeddingGenerator()
        self.client = chromadb.CloudClient(
            api_key=chroma_key,
            tenant=tenant_key,
            database=chroma_database,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=self.config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: list[str], metadata: list[Dict], embeddings: np.ndarray) -> int|None:
        """Add chunked documents with embeddings to vector store"""
        if not (chunks and metadata and embeddings is not None):
            return None

        if not (len(chunks) == len(metadata) == len(embeddings)):
            return None

        ids = [f"doc_{i}" for i in range(len(chunks))]
        embeddings= [emb.tolist() if isinstance(emb, np.ndarray) else emb for emb in embeddings]

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata
        )

        return len(chunks)

    def retrieve_similar(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],
                        'distance': results['distances'][0][i]
                    }

                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def retrieve_by_text(self, query_text: str) -> List[Dict[str, Any]]:

        query_embedding = self.embedding_generator.generate_single_embedding(query_text)
        return self.retrieve_similar(query_embedding.tolist(), self.config.TOP_K_RESULTS)

    def delete_document(self, document_id: str):
        """Delete a document by ID"""
        self.collection.delete(ids=[document_id])

    def get_collection_stats(self):
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.config.COLLECTION_NAME
        }

if __name__=="__main__":
    vector_store = VectorStore()