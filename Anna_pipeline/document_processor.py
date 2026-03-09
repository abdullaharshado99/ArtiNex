import os, re
import hashlib
from Anna_pipeline.config import RAGConfig
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chonkie import SemanticChunker, AutoEmbeddings, Document as ChonkieDocument
from langchain_community.document_loaders import (PyPDFLoader, TextLoader, Docx2txtLoader)


class DocumentProcessor:
    def __init__(self):
        self.config = RAGConfig()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        # self.text_splitter = SemanticChunker(
        #     embedding_model=AutoEmbeddings.get_embeddings("all-MiniLM-L6-v2"),
        #     threshold=self.config.SIMILARITY_THRESHOLD,
        #     chunk_size=2048,
        #     similarity_window=3,
        #     skip_window=0
        # )

    @staticmethod
    def extract_text_from_file(folder_path: str) -> list[Document]:

        textual_data: list = []

        file_loaders = {
            ".txt": TextLoader,
            ".docx": Docx2txtLoader,
            ".pdf": lambda path: PyPDFLoader(path, extract_images=True)
        }

        supported_extensions = [".txt", ".docx", ".pdf"]

        try:
            all_files = os.listdir(folder_path)

            files_to_process = [
                f for f in all_files
                if os.path.splitext(f)[1].lower() in supported_extensions
            ]

            for filename in files_to_process:
                file_path = os.path.join(folder_path, filename)
                file_extension = os.path.splitext(filename)[1].lower()

                try:
                    loader_class = file_loaders.get(file_extension)

                    if file_extension == ".pdf":
                        loader = loader_class(file_path)
                    else:
                        loader = loader_class(file_path)

                    loaded_data = loader.load()

                    for i, entry in enumerate(loaded_data):
                        entry.metadata.update({
                            "file_name": filename,
                            "file_extension": file_extension,
                            "document_id": hashlib.md5(f"{filename}_{i}".encode()).hexdigest()[:10]
                        })

                        if file_extension == ".pdf":
                            if "page" in entry.metadata:
                                entry.metadata["page_number"] = entry.metadata.pop("page") + 1

                            if hasattr(loader, "metadata") and loader.metadata:
                                entry.metadata.update(loader.metadata)


                    textual_data.extend(loaded_data)

                except Exception as e:
                    print(e)

        except Exception as e:
            print(f"Error scanning folder: {e}")

        return textual_data

    @staticmethod
    def clean_page_content(page_content: str) -> str:
        try:
            page_content = re.sub(r'\s+', ' ', page_content).strip()
            page_content = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"-]', '', page_content)
            page_content = re.sub(r'(\b[a-zA-Z])\s(?=[a-zA-Z]\b)', r'\1', page_content)
            page_content = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\b', r'\1\2', page_content)

            page_content = re.sub(r'\s([.,!?])', r'\1', page_content)

            page_content = " ".join(page_content.split())

            return page_content
        except Exception as e:
            raise e

    # def create_chunks(self, documents: list[Document]) -> tuple[list[str], list[dict]]:
    #
    #     all_chunks = []
    #     all_metadata = []
    #
    #     try:
    #         for doc_index, doc in enumerate(documents):
    #             text = doc.page_content
    #             doc_metadata = doc.metadata
    #
    #             chonkie_doc = ChonkieDocument(content=text)
    #
    #             chunks = self.text_splitter.chunk_document(chonkie_doc)
    #
    #             if hasattr(chunks, 'chunks'):
    #                 chunks = chunks.chunks
    #
    #                 for chunk_index, chunk in enumerate(chunks):
    #                     if hasattr(chunk, 'content'):
    #                         chunk_text = chunk.content
    #                     elif hasattr(chunk, 'text'):
    #                         chunk_text = chunk.text
    #                     else:
    #                         chunk_text = str(chunk)
    #
    #                     cleaned_text = self.clean_page_content(chunk_text)
    #
    #                     chunk_metadata = {
    #                         **doc_metadata,
    #                         'total_chunks': len(chunks),
    #                         'similarity_window': 3
    #                     }
    #
    #                     all_chunks.append(cleaned_text)
    #                     all_metadata.append(chunk_metadata)
    #
    #
    #     except Exception as e:
    #         print(f"Error in create_chunks: {e}")
    #         return [], []
    #
    #     return all_chunks, all_metadata

    def create_chunks(self, documents: list[Document]) -> tuple[list, list]:
        """Split text into chunks with metadata"""

        text_splitter = self.text_splitter

        all_chunks: list = []
        all_metadata: list = []

        try:

            for doc in documents:
                text = doc.page_content
                doc_metadata = doc.metadata

                chunks = text_splitter.create_documents([text], metadatas=[doc_metadata])

                for chunk in chunks:
                    all_chunks.append(self.clean_page_content(chunk.page_content))
                    all_metadata.append(chunk.metadata)

        except Exception as e:
            print(e)

        return all_chunks, all_metadata

    def process_document(self, file_path: str) -> tuple[list, list]:
        """Complete document processing pipeline"""

        text = self.extract_text_from_file(file_path)
        chunks, metadata = self.create_chunks(text)

        return chunks, metadata

if __name__ == "__main__":
    processor = DocumentProcessor()
