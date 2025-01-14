#import logging
import os
import ollama
import streamlit as st
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Configure logging
#logging.basicConfig(level=logging.INFO)

DOC_PATH = "./PDFs/B-0507.pdf"
MODEL_LLM = "llama3.2"
MODEL_EMBED = "nomic-embed-text"
COLLECTION_NAME = "simple-rag"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 300
PERSIST_DIRECTORY = "./chroma_db"

def LoadPdf(doc_path):
    if os.path.exists(doc_path):
        loader = UnstructuredPDFLoader(file_path=doc_path)
        data = loader.load()
        #logging.info("PDF loaded successfully.")
        print("done loading....")
        st.error("PDF file not found.")
        #content = data[0].page_content
        return data
    else:
        #logging.error(f"PDF file not found at path: {doc_path}")      
        return None
    
#print(content[:100])

def SplitDataIntoChunks(data):
    print(f"/nData : {data[:100]}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    chunks = text_splitter.split_documents(data)
    print("done splitting...")
    #logging.info("Documents split into chunks.")
    return chunks
    # print(f"Number of chunks:{len(chunks)}")
    # print(f"Example chunks:{chunks[0]}")

@st.cache_resource
def AddChunksToVectorDB():
    #ollama.pull(MODEL_EMBED)
    embedding = OllamaEmbeddings(model=MODEL_EMBED)
    if os.path.exists(PERSIST_DIRECTORY):
        vector_db = Chroma.from_documents(
            embedding_function=embedding,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIRECTORY
        )
        #logging.info("Loaded existing vector database.")
    else:
        data = LoadPdf(DOC_PATH)
        if data is None:
            return None
        chunks = SplitDataIntoChunks(data=data)
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )
        vector_db.persist()
        #logging.info("Vector database created and persisted.")
    return vector_db

 

def GetRetriever(vector_db,llm):

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
        vector_db.as_retriever(),llm,prompt=QUERY_PROMPT
    )
    #logging.info("Retriever created.")
    return retriever

# RAG prompt
def GetTheChain(retriever,llm):
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context":retriever,"question":RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    #logging.info("Chain created successfully.")
    return chain

def main():
    st.title("Document Assistant")
    userInput = st.text_input("Enter your query: ","")
    if userInput:
        with st.spinner("Generating response..."):
            try:
                llm = ChatOllama(model=MODEL_LLM)

                #content = LoadPdf(DOC_PATH)
                #chunks = SplitDataIntoChunks(content)
                vector_db = AddChunksToVectorDB()
                if vector_db is None:
                    st.error("Failed to load or create the vector Database.")
                    return
                
                retriever = GetRetriever(vector_db,llm)
                chain = GetTheChain(retriever,llm)
    
                #userInput= "what is the document about?"
                res = chain.invoke(input=(userInput,))
                st.markdown("***Assistant:*")
                st.write(res)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please enter a question to get started.")


if __name__ =="__main__":
    main()