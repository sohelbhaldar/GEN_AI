# main.py

import os
import logging
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from chromadb.config import Settings
from ConstantsLib.constants import Constant
import chromadb

#DOC_PATH = "./data/BOI.pdf"

# Configure logging
#logging.basicConfig(level=logging.INFO)

def ingest_pdf(doc_path):
    """Load PDF documents."""
    if os.path.exists(doc_path):
        loader = UnstructuredPDFLoader(file_path=doc_path)
        data = loader.load()
        logging.info("PDF loaded successfully.")
        #logging.info(data[0].page_content)
        return data
    else:
        logging.error(f"PDF file not found at path: {doc_path}")
        return None


def split_documents(documents):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    chunks = text_splitter.split_documents(documents)
    logging.info("Documents split into chunks.")
    logging.info(f"Number of chunks.{len(chunks)}")
    #logging.info(f"Example of chunks.{chunks[0]}")
    return chunks


def create_vector_db(chunks):
    """Create a vector database from document chunks."""
    #ollama.pull(EMBEDDING_MODEL)
    #print(chunks)
    
    #client = chromadb.Client(Settings(anonymized_telemetry=False))
    client = chromadb.PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))
    #client = chromadb.HttpClient(host="chromaDB", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model=Constant.EMBEDDING_MODEL),
        collection_name=Constant.VECTOR_STORE_NAME,
        client=client
    )
    logging.info("Vector database created.")
    return vector_db


def create_retriever(vector_db, llm):
    """Create a multi-query retriever."""
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
different versions of the given user question to retrieve relevant documents from
a vector database. By generating multiple perspectives on the user question, your
goal is to help the user overcome some of the limitations of the distance-based
similarity search. Provide these alternative questions separated by newlines.
Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
    )
    logging.info("Retriever created.")
    return retriever


def create_chain(retriever, llm):
    """Create the chain"""
    # RAG prompt
    template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logging.info("Chain created successfully.")
    return chain

def pdfServiceExe(question):
    # Load and process the PDF document
    print("Ingesting PDF..")
    data = ingest_pdf(Constant.DOC_PATH)
    if data is None:
        return
    
    print("Splitting docs..")
    # Split the documents into chunks
    chunks = split_documents(data)

    print("Creating vector db..")
    # Create the vector database
    vector_db = create_vector_db(chunks)

    # Initialize the language model
    llm = ChatOllama(model=Constant.MODEL_NAME)

    print("Creating retriever..")
    # Create the retriever
    retriever = create_retriever(vector_db, llm)

    print("Creating chain..")
    # Create the chain with preserved syntax
    chain = create_chain(retriever, llm)

    print("Creating answer..")
    # Get the response
    res = chain.invoke(input=question)
    if res:
        return res
    else:
        return None

if __name__ == "__main__":
    pdfServiceExe()
