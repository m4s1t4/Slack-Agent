import sys
import os
import shutil
from dataclasses import dataclass
from typing import List
import argparse

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
# ---- Constants ---- #
CHROMA_PATH = "data\\vectorDB"
DATA_SOURCE_PATH = "data\\knowledge"
CHROMA_PATH = os.environ.get("CHROMA_PATH", "data\\vectorDB")
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
CHROMA_DB_INSTANCE = None
OLLAMA_MODEL_ID = "llama3.2"
EMBEDDING_MODEL_ID = "nomic-embed-text"

# ---- Prompt ---- #
RAG_PROMPT_TEMPLATE = """
## Introduction

- **YOU ARE** an **ASSISTANT FOR QUESTION-ANSWERING TASKS** with access to scientific literature and resources.

(Context: "Your role is to provide precise, well-explained answers based on retrieved scientific context.")

## Task Description

- **YOUR TASK** is to **USE** the following pieces of retrieved context to **ANSWER** the question. If you don't know the answer, state clearly that you don't know.

(Context: "Providing accurate and reliable information is crucial for maintaining credibility and trust.")

## Important Instructions

1. **THINK** carefully before you respond.
2. **ENSURE** the text is ready to be copied and pasted.
3. **RESPOND PRECISELY** and provide the best explanation possible with a technical tone.
4. **VERIFY** the relevance and accuracy of the context before formulating your answer.

(Context: "Clear and precise responses enhance user satisfaction and trust.")

## Context
- **Question**: {question}
- **Context**: {context}

## Important

- "Your attention to detail and accuracy is paramount. Strive for precision and clarity in every response."
- "Remember, providing well-supported and accurate answers helps maintain the integrity and reliability of the information."
- **INCLUDE** Source references.
- Always respond in Spanish

**EXAMPLES of required response**

<examples>

<example1>

(Answer: Mitochondria play a crucial role in cellular respiration by generating ATP through oxidative phosphorylation. They are often referred to as the powerhouses of the cell due to their role in energy production.)

</example1>

<example2>


(Answer: Enzymes facilitate chemical reactions by lowering the activation energy required for the reactions to occur. This enables the reactions to proceed more quickly and efficiently.)

</example2>

</examples>


"""


# ---- Structured Output
@dataclass
class QueryResponse:
    response_text: str
    sources: List[str]


def get_embedding_function():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_ID)
    return embeddings


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_SOURCE_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def get_db():
    global CHROMA_DB_INSTANCE
    if not CHROMA_DB_INSTANCE:

        # Hack needed for AWS Lambda's base Python image (to work with an updated version of SQLite).
        # In Lambda runtime, we need to copy ChromaDB to /tmp so it can have write permissions.
        if IS_USING_IMAGE_RUNTIME:
            __import__("pysqlite3")
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
            copy_chroma_to_tmp()

        # Prepare the DB.
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=get_runtime_chroma_path(),
            embedding_function=get_embedding_function(),
        )

    return CHROMA_DB_INSTANCE


def copy_chroma_to_tmp():
    dst_chroma_path = get_runtime_chroma_path()

    if not os.path.exists(dst_chroma_path):
        os.makedirs(dst_chroma_path)

    tmp_contents = os.listdir(dst_chroma_path)
    if len(tmp_contents) == 0:
        print(f"Copying ChromaDB from {CHROMA_PATH} to {dst_chroma_path}")
        os.makedirs(dst_chroma_path, exist_ok=True)
        shutil.copytree(CHROMA_PATH, dst_chroma_path, dirs_exist_ok=True)
    else:
        print(f"ChromaDB already exists in {dst_chroma_path}")


def get_runtime_chroma_path():
    if IS_USING_IMAGE_RUNTIME:
        return f"/tmp/{CHROMA_PATH}"
    else:
        return CHROMA_PATH


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)
    for chunk in chunks:
        print(f"Chunk Page Sample: {chunk.metadata['id']}\n{chunk.page_content}\n\n")

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the chunk meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def query_rag(query_text: str) -> QueryResponse:
    db = get_db()

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOllama(model=OLLAMA_MODEL_ID, temperature=0)
    response = model.invoke(prompt)
    response_text = response.content

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    return f"\nResponse:\n{response_text}\n\nSources: {sources}"


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)
    while True:
        preg = input("Mensaje: ")
        if preg.lower() == "exit":
            break
        else:
            rta = query_rag(preg)
            print(rta)


if __name__ == "__main__":
    main()
