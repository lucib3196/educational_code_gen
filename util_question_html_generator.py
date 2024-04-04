# Standard library imports
import os
import re
import warnings
from pprint import pprint

# Suppress warnings
warnings.filterwarnings("ignore")

# Third-party library imports
import bs4

# Langchain imports
from langchain import hub
from langchain.agents import create_openai_functions_agent, AgentExecutor, create_openai_tools_agent
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_core.output_parsers import StrOutputParser

# Langchain OpenAI imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Langchain Community imports
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader

# Utility imports
from util_semantic_search import SemanticSearch
from util_example_based_prompt import ExampleBasedPromptFormatter
from credential import api_key

def question_html_generator(question: str, api_key: str, csv_path: str, additional_instructions: str = None) -> str:
    example_options = {
        "embedding_column": "question_embedding",
        "search_column": "question",
        "output_column": "question.html",
        "n_examples": 3
    }

    llm_options = {
        "llm_code_generation_model": "gpt-4",
        "agent_model": "gpt-3.5-turbo-0125",
        "retriever_model": "gpt-3.5-turbo-0125",
        "temperature": 0,
        "embedding_model": "text-embedding-ada-002"
    }

    # Initialize SemanticSearch instance
    semantic_search_instance = SemanticSearch(
        csv_path=csv_path,
        embedding_column_name=example_options["embedding_column"],
        embedding_engine=llm_options["embedding_model"],
        api_key=api_key
    )

    def extract_examples(question: str) -> str:
        return semantic_search_instance.extract_examples(
            input_string=question,
            search_column=example_options["search_column"],
            output_column=example_options["output_column"],
            n_examples=example_options["n_examples"]
        )

    examples_dict = extract_examples(question)
    
    base_template = "Generate a html code based on the following examples"
    prompt = ExampleBasedPromptFormatter.run(examples_dict, base_template) + \
             f"\n new_question_input = {question}  delimit the generated html with ```insert_code_here```"
    
    # Define LLM and chain for HTML generation
    llm = ChatOpenAI(model=llm_options["llm_code_generation_model"], api_key=api_key, temperature=llm_options["temperature"])
    output_parser = StrOutputParser()
    chain = llm | output_parser
    html_generated = chain.invoke(prompt)
    
    return html_generated

# Example usage of the function
csv_path = "Question_Embedding_20240128.csv"  # Replace with your actual CSV path
question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # Replace with your actual question
print(question_html_generator(question, api_key, csv_path))

