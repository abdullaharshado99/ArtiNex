import cohere
import numpy as np
from Anna_pipeline.config import RAGConfig


class EmbeddingGenerator:
    def __init__(self):
        self.config = RAGConfig()
        self.client = cohere.Client(self.config.COHERE_KEY)

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""

        response = self.client.embed(
            texts=texts,
            model=self.config.COHERE_EMBEDDING_MODEL,
            input_type="search_document",
            truncate="END"
        )
        return np.array(response.embeddings)

    def generate_single_embedding(self, text: str) -> np.ndarray:
        response = self.client.embed(
            texts=[text],
            model=self.config.COHERE_EMBEDDING_MODEL,
            input_type="search_query",
            truncate="END"
        )

        return np.array(response.embeddings[0])


if __name__ == "__main__":
    # Initialize
    emb = EmbeddingGenerator()




# import os
# import numpy as np
# from dotenv import load_dotenv
# from Anna_pipeline.config import RAGConfig
# from sentence_transformers import SentenceTransformer
# import chromadb.utils.embedding_functions as embedding_functions
#
# load_dotenv()
#
# hf_token = os.getenv("HF_TOKEN")
# cohere_token = os.getenv("COHERE_KEY")
#
# class EmbeddingGenerator:
#     def __init__(self):
#         self.config = RAGConfig()
#         self.model =  SentenceTransformer(self.config.EMBEDDING_MODEL, token=hf_token)
#             # embedding_functions.CohereEmbeddingFunction(api_key=cohere_token,  model_name="multilingual-22-12")
#
#     def generate_embeddings(self, texts: list[str]) -> np.ndarray:
#         """Generate embeddings for a list of texts"""
#
#         embeddings = self.model.encode(
#             texts,
#             normalize_embeddings=True,
#             show_progress_bar=True
#         )
#         return embeddings
#
#     def generate_single_embedding(self, text: str) -> np.ndarray:
#         """Generate embedding for a single text"""
#
#         return self.model.encode(text, normalize_embeddings=True)
#
# if __name__=="__main__":
#     emb = EmbeddingGenerator()