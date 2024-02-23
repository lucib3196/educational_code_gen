# Import Requires Modules
# Standard library imports
import warnings
from pprint import pprint
import re

# Third-party library imports
import bs4
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from util_code_generation import PromptFormatterFromRepository,builder_server_js
import asyncio
from util_semantic_search import SemanticSearch
from util_example_based_prompt import ExampleBasedPromptFormatter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from util_semantic_search import CSVDataHandler, SemanticSearch
# Suppress warnings
from typing import List, Optional, Union, Type
warnings.filterwarnings("ignore")

# API Key
api_key = "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"

def js_generator(question, api_key, csv_path=None,solution_guide=None):

    chat_history = []
    example_options = {
    "embedding_column": "question_embedding",
    "search_column": "question.html",
    "output_column": "server.js",
    "n_examples": 1}

    llm_options = {
        "llm_model": "gpt-4-turbo-preview",
        "temperature": 0,  # Assuming temperature should be an integer or float, not a string
        "embedding_model": "text-embedding-ada-002"
    }
    llm = ChatOpenAI(model_name=llm_options["llm_model"], temperature=0,api_key=api_key)
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

    def contextualized_question(input: dict):
        if input.get("chat_history"):
            return contextualize_q_chain
        else:
            return input["question"]
        
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question.
    Use the code database context \
    If you don't know the answer, just say that you don't know. \
    \

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    loader = GenericLoader.from_filesystem(
    "stable_properties",
    glob="*",
    suffixes=[".js"],
    parser=LanguageParser(),)
    docs = loader.load()
    vectorstore = Chroma.from_documents(documents=docs, embedding=OpenAIEmbeddings(api_key=api_key))
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6},api_key=api_key)
    
    rag_chain = (
        RunnablePassthrough.assign(
            context=contextualized_question | retriever | format_docs
        )
        | qa_prompt
        | llm
    )
    
    
    initial_question = f"I am planning on creating a javascript module for the following question {question}, only return the modules that I have "
    improvements_response  = rag_chain.invoke({"question": initial_question, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=question), improvements_response])
    return improvements_response

question = """<pl-question-panel>
  <p> A car is traveling along a road winding around sea-side cliffs (like Highway 1 between Carmel and San Luis Obispo) at {{params.speed}} {{params.unitsSpeed}}. The road has an upward slope of {{params.slope}}° to the horizontal. On a particularly sharp curve, the driver loses control, drives off the road and becomes air-borne. If the cliff is sheer so that it can be assumed to be vertical and is {{params.height}} {{params.unitsDist}} above the ocean below, at what angle to the horizontal does it hit the water? (Use the acute angle) </p>
</pl-question-panel>

<pl-number-input answers-name="angle" comparison="sigfig" digits="3" label="Angle (in degrees)"></pl-number-input>"""
print(js_generator(question,api_key))