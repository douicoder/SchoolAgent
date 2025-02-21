# imports
import os
import logging
import hashlib
import json
import time
from docx import Document
from pptx import Presentation
import pandas as pd
import pytesseract
import faiss
import numpy as np
from langchain_community.vectorstores import FAISS
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import pdfplumber

# Constants
DOCS_FOLDER = "./data"
MODEL_NAME = "mistral"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_STORE_NAME = "fast-rag"
PERSIST_DIRECTORY = "./faiss_fast_db"
HASH_FILE = "./faiss_file_hashes.json"

# error logging for debugging
logging.basicConfig(level=logging.INFO)


class Chatbot:
    def __init__(
        self,
        docs_folder=DOCS_FOLDER,
        model_name=MODEL_NAME,
        embedding_model=EMBEDDING_MODEL,
        vector_store_name=VECTOR_STORE_NAME,
        persist_directory=PERSIST_DIRECTORY,
        hash_file=HASH_FILE,
    ):
        self.docs_folder = docs_folder
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.vector_store_name = vector_store_name
        self.persist_directory = persist_directory
        self.hash_file = hash_file
        self.existing_hashes = self.load_existing_hashes()
        self.vector_db = self.load_vector_db()

    # generates hash for documents
    def calculate_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    # checks existing hashes
    def load_existing_hashes(self):
        if os.path.exists(self.hash_file):
            with open(self.hash_file, "r") as f:
                return json.load(f)
        return {}

    # save and update hashes
    def save_hashes(self, file_hashes):
        with open(self.hash_file, "w") as f:
            json.dump(file_hashes, f, indent=4)

    # extract text from files
    def extract_from_file(self, file_path):
        """Extract text based on file type."""
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                return [
                    page.extract_text() for page in pdf.pages if page.extract_text()
                ]
        elif file_path.endswith(".docx"):
            return [
                para.text
                for para in Document(file_path).paragraphs
                if para.text.strip()
            ]
        elif file_path.endswith(".pptx"):
            return [
                shape.text
                for slide in Presentation(file_path).slides
                for shape in slide.shapes
                if hasattr(shape, "text")
            ]
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            return [" ".join(map(str, row)) for row in df.values]
        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return [text] if text.strip() else []
        return []

    # check for new files and process them
    def ingest_documents(self):
        start_time = time.time()
        new_hashes = self.existing_hashes.copy()
        extracted_texts = []

        files = [
            f for f in os.listdir(self.docs_folder) if f not in self.existing_hashes
        ]

        if not files:
            logging.info("No new files to process.")
            return None, 0

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda file: (
                    file,
                    self.extract_from_file(os.path.join(self.docs_folder, file)),
                ),
                files,
            )

        for file_name, text in results:
            if text:
                new_hashes[file_name] = self.calculate_file_hash(
                    os.path.join(self.docs_folder, file_name)
                )
                extracted_texts.extend(text)

        if extracted_texts:
            self.save_hashes(new_hashes)
            self.existing_hashes = new_hashes

        processing_time = time.time() - start_time
        return extracted_texts if extracted_texts else None, processing_time

    # split documents into smaller chunks for embedding
    def split_documents(self, texts):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=100
        )
        return [chunk for text in texts for chunk in text_splitter.split_text(text)]

    # load or create FAISS vector store
    def load_vector_db(self):
        embedding = OllamaEmbeddings(model=self.embedding_model)

        os.makedirs(self.persist_directory, exist_ok=True)
        index_file = f"{self.persist_directory}/faiss_index"

        if os.path.exists(index_file):
            vector_db = FAISS.load_local(self.persist_directory, embedding)
            logging.info("Loaded existing FAISS index.")
        else:
            vector_db = FAISS.from_texts([""], embedding)
            logging.info("Created a new FAISS index.")

        return vector_db

    # update FAISS vector database
    def update_vector_db(self):
        texts, processing_time = self.ingest_documents()
        if texts:
            start_time = time.time()
            chunks = self.split_documents(texts)

            # Generate embeddings
            embeddings = self.vector_db.embedding_function.embed_documents(chunks)

            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Add to FAISS index
            self.vector_db.index.add(embeddings_array)

            # Save FAISS index
            self.vector_db.save_local(self.persist_directory)

            db_update_time = time.time() - start_time
            logging.info("FAISS vector database updated.")
            return f"New documents processed! (Processing: {processing_time:.2f}s, DB Update: {db_update_time:.2f}s)"
        else:
            return "No new documents found."

    # get language model
    def get_llm(self):
        return ChatOllama(model=self.model_name)

    # create retriever for vector search
    def create_retriever(self):
        return self.vector_db.as_retriever(search_kwargs={"k": 2})

    # create response chain
    def create_chain(self):
        template = """Answer based on this context:
        {context}
        Question: {question}
        Keep responses under 30 words.
        """
        prompt = ChatPromptTemplate.from_template(template)
        return (
            {"context": self.create_retriever(), "question": RunnablePassthrough()}
            | prompt
            | self.get_llm()
            | StrOutputParser()
        )

    def get_response(self, user_input):
        try:
            chain = self.create_chain()
            start_time = time.time()
            response = chain.invoke(input=user_input)
            query_time = time.time() - start_time
            return response, query_time
        except Exception as e:
            return f"Error: {str(e)}", None
