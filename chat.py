import streamlit as st
import os
import uuid
import boto3

# Libraries for handling base chat functionality
from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.memory import RedisChatMessageHistory

# Extension libraries for handling RAG functionality on PDF
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain

## ----------- AWS Configurations -----------
client = boto3.client("bedrock-runtime", region_name = "us-east-1")

## ----------- Template and Prompt Configuration -----------
template = "{chat_history}\n\nHuman:{human_input}\n\nAssistant:"
prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)

## ----------- Session and Chat ID Initialization -----------
# Initialize unique chat session ID using UUID stored in Streamlit session state
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

## ----------- Redis Configuration -----------
# Retrieve Redis connection string from environment variables
redis_conn_string = os.environ.get("REDIS_CONN_STRING")
# Set up Redis-backed chat history management
redis_chat_memory = RedisChatMessageHistory(url=redis_conn_string,session_id=st.session_state.chat_id)

## ----------- Memory Management -----------
# Initialize conversation memory to manage chat history
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=redis_chat_memory, ai_prefix="\n\nAssistant", human_prefix="\n\nHuman")

## ----------- Streamlit Page Setup -----------

# Page Configuration
st.set_page_config(
    page_title="Chatbot",
    page_icon="👋",
)

# Set up title and caption of Streamlit web page
st.title("Streamlit LLM Application Prototype")
st.caption("Developer: Jonathan Yeo")

# Selection Pane
st.sidebar.success("Select an application above.")

# Collapsible container box.
with st.expander('About this app'):
  st.write('Streamlit chatbot powered by Amazon Bedrock, Langchain and Redis. Updated with PDF QA functionality.')

## ----------- LLM Configuration -----------
# Initialize LLM using Bedrock with model configuration
llm = Bedrock(
        client=client,
        model_id="anthropic.claude-v2"
        #streaming=True,
    )

# Set up LLM chain
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

## ----------- ConversationalRetrievalChain RAG Component -----------
uploaded_file = st.file_uploader("Upload PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded PDF file temporarily
    with open("/tmp/uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.read())

    pdf_loader = PyPDFLoader("/tmp/uploaded_file.pdf")
    document_text = pdf_loader.load()
    
    # Define chunk size and overlap for splitting the document
    chunk_size = 512
    chunk_overlap = 50

    # Split the document text into sections
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    document_sections = splitter.split_documents(document_text)
    
    # Embed the text sections using BedrockEmbeddings
    embedder = BedrockEmbeddings(client=client, model_id="amazon.titan-embed-text-v2:0")
    
    # Create a FAISS vector store from the embeddings
    vector_store = FAISS.from_documents(document_sections, embedder)
    
    # Initialize ConversationalRetrievalChain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        verbose=True,
        get_chat_history=lambda h : h
        )

## ----------- Message Handling -----------
# Initialize the message storage in session state if it hasn't been set up
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture and process user input
if prompt := st.chat_input("Enter your message"):

    # Display user's message in the chat interface
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Use RAG chain for response generation if available
    if 'rag_chain' in locals():
        response = rag_chain.invoke({"question": prompt})
        response_text = response["answer"]
    else:
        response_text = llm_chain.predict(human_input=prompt)

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
