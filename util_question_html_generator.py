# Standard library imports
import asyncio
import os
import re
import warnings
from pprint import pprint

# Suppress warnings
warnings.filterwarnings("ignore")

# Third-party library imports
import bs4

# langchain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import hub
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
# langchain_community imports
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
# Utility imports
from util_semantic_search import SemanticSearch
from util_example_based_prompt import ExampleBasedPromptFormatter


def question_html_generator(question:str,api_key:str,csv_path:str,additional_instructions:str=None):
    example_options = {
    "embedding_column": "question_embedding",
    "search_column": "question",
    "output_column": "question.html",
    "n_examples": 4}

    llm_options = {
        "llm_code_generation_model": "gpt-4",
        "agent_model": "gpt-3.5-turbo-0125",
        "retriever_model": "gpt-3.5-turbo-0125",
        "temperature": 0,  
        "embedding_model": "text-embedding-ada-002"
    }
    semantic_search_instance = SemanticSearch(
        csv_path=csv_path,
        embedding_column_name=example_options["embedding_column"],
        embedding_engine=llm_options["embedding_model"],
        api_key=api_key
    )
    def extract_examples(question: str) -> str:
        examples = semantic_search_instance.extract_examples(
            input_string=question,
            search_column=example_options["search_column"],
            output_column=example_options["output_column"],
            n_examples=3
        )
        return examples
    examples_dict = extract_examples(question)
    
    base_template =  """
    Generate a html code based on the following examples"""
    prompt=ExampleBasedPromptFormatter.run(examples_dict,base_template) + f"\n new_question_input = {question}  delimit the generated html with ```insert_code_here```"
    
    # Define LLM 
    llm = ChatOpenAI(model = llm_options["llm_code_generation_model"],api_key=api_key,temperature=llm_options["temperature"])
    output_parser = StrOutputParser()
    chain = llm | output_parser
    html_generated = chain.invoke(prompt)
    
    if additional_instructions:
        ## Define a retrieval for additional instructions
        # Load Prairielearn Format Website
        loader = WebBaseLoader("https://prairielearn.readthedocs.io/en/latest/elements/")
        data = loader.load()

        # Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        splits = text_splitter.split_documents(data)

        # VectorDB
        embedding = OpenAIEmbeddings(api_key=api_key)
        vectordb = Chroma.from_documents(documents=splits, embedding=embedding)
        retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 8})
        # Set up Retriever As a tool
        tool = create_retriever_tool(
        retriever,
        "search_question_elements",
        "You have access to the documentation for formatting question html files",
        )
        tools = [tool]
        
        # Intialize Agent 
        agent_llm = ChatOpenAI(model = llm_options["agent_model"])
        prompt = hub.pull("hwchase17/openai-tools-agent")
        
        agent = create_openai_tools_agent(agent_llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)
        
        agent_input = f""""The user want to modify the following html {html_generated}, you have access to the tool search_question_elements which will
        allow you to modify the html code to their request. Your task is to modify the html to their request, use the search tool as a guide. 
        User Modifications: {additional_instructions}
        return the hmtl 
        delimited by ```generated_html```"""
        
        response = agent_executor.invoke({"input": agent_input})
        html_generated = response["output"]
    return html_generated
    

# # Example usage of the function
# # api_key = "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"  # Replace with your actual API key
# csv_path = r"Question_Embedding_20240128.csv"  # Replace with your actual CSV path
# question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # Replace with your actual question
# print(question_html_generator(question,api_key,csv_path))