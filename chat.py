import streamlit as st
import os
import uuid
import boto3

from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.memory import RedisChatMessageHistory

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
# Set up title and caption of Streamlit web page
st.title("AWS Streamlit Application Prototype")
st.caption("Streamlit chatbot powered by Amazon Bedrock, Langchain and Redis, deployed over EKS. Developer: Jonathan Yeo")

## ----------- LLM Configuration -----------
# Initialize LLM using Bedrock with model configuration
llm = Bedrock(
        client=client,
        model_id="anthropic.claude-v2"
        #streaming=True,
    )

# Set up LLM chain to manage interactions between LLM and prompt template
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
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

    # Displa user's message in the chat interface
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response using the LLM chain
    response = llm_chain.predict(human_input=prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})