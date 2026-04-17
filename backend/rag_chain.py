from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

class RAGChain:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        # Using Ollama for local LLM (install Ollama first)
        # For OpenAI: from langchain.chat_models import ChatOpenAI
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="llama2", temperature=0.7)
        self.vectorstore = None
        
    def create_vectorstore(self, documents: list):
        """Create vector store from documents"""
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()
        return self.vectorstore
    
    def add_documents(self, documents: list):
        """Add documents to existing vectorstore"""
        if self.vectorstore is None:
            return self.create_vectorstore(documents)
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
    
    def get_qa_chain(self):
        """Create retrieval QA chain"""
        if self.vectorstore is None:
            raise Exception("No vectorstore available. Please add documents first.")
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )
        
        # Custom prompt template
        prompt_template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}

        Question: {question}
        Answer: """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        return qa_chain
    
    def query(self, question: str):
        """Query the RAG system"""
        qa_chain = self.get_qa_chain()
        result = qa_chain({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.metadata.get("source", "Unknown") 
                       for doc in result["source_documents"]]
        }