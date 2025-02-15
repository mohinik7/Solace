from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def initialize_llm():
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        temperature=0,
        groq_api_key="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",
        model_name="llama-3.3-70b-versatile"
    )
    return llm

def create_vector_db():
    # Loads all PDFs in the current directory
    loader = DirectoryLoader("pdfs/", glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceBgeEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_db = Chroma.from_documents(texts, embeddings, persist_directory='./chroma_db')
    vector_db.persist()
    print("ChromaDB created and data saved")
    return vector_db

def setup_qa_chain(vector_db, llm):
    retriever = vector_db.as_retriever()
    prompt_templates = (
        "You are a compassionate mental health chatbot. Respond thoughtfully to the following question:\n"
        "{context}\nUser: {question}\nChatbot:"
    )
    PROMPT = PromptTemplate(template=prompt_templates, input_variables=['context', 'question'])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain

# Initialize the chatbot once when this module is imported.
print("Initializing Chatbot.........")
llm = initialize_llm()

db_path = "./chroma_db"
if not os.path.exists(db_path):
    vector_db = create_vector_db()
else:
    embeddings = HuggingFaceBgeEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    
qa_chain = setup_qa_chain(vector_db, llm)

def chatbot_response(user_input):
    if not user_input.strip():
        return "Please provide a valid input."
    assistant_response = qa_chain.run(user_input)
    return assistant_response
