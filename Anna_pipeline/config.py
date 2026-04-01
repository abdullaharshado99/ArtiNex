import os
from dotenv import load_dotenv

load_dotenv()


class RAGConfig:
    # Chunking settings
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 10

    # Embedding settings
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-mpnet-base-v2"
    COHERE_EMBEDDING_MODEL = "embed-multilingual-v3.0"
    # Alternative: "BAAI/bge-small-en-v1.5" or "intfloat/e5-large-v2" or "all-MiniLM-L6-v2"


    COHERE_KEY = os.getenv("COHERE_KEY")

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    FLASK_APP_PASSWORD= os.environ.get('SECRET_KEY')

    RESEND_KEY = os.environ.get('RESEND_KEY')
    RECEIVER_EMAIL = os.getenv("RECEIVE_EMAIL")

    CHROMA_KEY = os.getenv("CHROMA_CLOUD")
    TENANT_KEY = os.getenv("CHROMA_TENANT")
    CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
    CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION")

    # Search settings
    TOP_K_RESULTS = 1
    SIMILARITY_THRESHOLD = 0.5

    # File upload settings
    UPLOAD_FOLDER = "uploads"
    DATA_FOLDER = "D:\Abdullah\Documents\codes\Projects\ArtiNex\static\data"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB