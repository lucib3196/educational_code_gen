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
from langchain import hub
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# langchain_community imports
from langchain_core.output_parsers import StrOutputParser
# Utility imports
from util_semantic_search import SemanticSearch
from util_example_based_prompt import ExampleBasedPromptFormatter


def question_solution_guide(question:str,api_key:str,csv_path:str,solution_guide:str=None,code_guide:str=None):
    example_options = {
    "embedding_column": "question_embedding",
    "search_column": "question",
    "output_column": "solution.html",
    "n_examples": 2}

    llm_options = {
        "llm_code_generation_model": "gpt-4-turbo-preview",
        "agent_model": "gpt-4-turbo-preview",
        "retriever_model": "gpt-4-turbo-preview",
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
    
    base_template = ""
    if solution_guide:
        template_with_guide = f"""
        Objective:
        Develop an HTML module to generate comprehensive solutions and step-by-step guides for STEM problems. Utilize specific HTML tags for structural organization and LaTeX for mathematical equations and symbols.

        HTML Tags and LaTeX Integration:
        - <pl-solution-panel>: Used to encapsulate the entire solution guide.
        - <pl-hint level="1" data-type="text">: Employed for providing hints and detailed step-by-step explanations within the guide.
        - LaTeX Integration: Incorporate LaTeX within the HTML to accurately represent mathematical equations and symbols, enhancing clarity and precision.

        Solution Guide Format:
        1. Problem Statement: 
        - Define the problem's objective clearly within a <pl-solution-panel>.

        2. Known Variables Description: 
        - Use <pl-hint> tags to describe all known variables. Include relevant mathematical expressions or equations formatted in LaTeX.

        3. Equation Setup: 
        - Establish equations or relationships necessary to solve the unknown, utilizing LaTeX for mathematical representations within <pl-hint> tags.

        4. Solution Process: 
        - Detail each step of the solution, employing <pl-hint> tags. Represent all mathematical workings and solutions using LaTeX.

        5. Explanation and Clarification: 
        - Provide thorough explanations and clarifications throughout the guide, using LaTeX within <pl-hint> tags for mathematical justifications.

        6. Educational Goal: 
        - The guide should be structured to assist students in mastering the material, emphasizing a deep understanding of the problem-solving process.

        Task:
        - Develop an HTML module to create solutions and guides for STEM problems based on structured HTML questions.
        - The provided solution guide format is as follows: {solution_guide}.
        - Analyze example HTML questions and create guides that align with the provided format.
        
        delimit the html  in ```insert_html_solution_guide```
        """
        base_template = template_with_guide
        
        # print(base_template)

    if not solution_guide:
        # If neither solution_guide nor code was provided, use the default template
        base_template = """
        Create an HTML module for generationg a  solutions to STEM problems. 
        Users will input an HTML file with a structured question, and the module should return an HTML solution. 
        Examine these example HTML questions and formulate corresponding HTML solutions:
        delimit the html  in ```insert_html_solution_guide```
        """
    
    prompt=ExampleBasedPromptFormatter.run(examples_dict,base_template) + f"\n new_question_input = {question}  delimit the generated html with ```insert_code_here```"
    # Define LLM 
    # print(prompt)
    llm = ChatOpenAI(model = llm_options["llm_code_generation_model"],api_key=api_key,temperature=llm_options["temperature"])
    output_parser = StrOutputParser()
    chain = llm | output_parser
    solution_generated = chain.invoke(prompt)
    
    if code_guide:
        solution_improvement= f"""Given the current HTML module for STEM problem-solving, your task is to enhance it using the provided code as a foundational guide. This code is designed to dynamically generate problem parameters and their correct answers. Your objective is to integrate these elements into the HTML solution guide effectively.
        Your Specific Tasks:
        1. **Review the Current ssolution guide  **: 
        Begin by examining the provided HTML solution guide  {solution_generated}. 
        2. **Integrate Dynamic Content Using Placeholders**: Insert placeholders into the HTML that correspond to the outputs of the code found in the params datastructure. Use placeholders like `{{params.placeholder_value}}` or `{{correct_answers.placeholder_value}}` that align with the variable names and data formats in the code. This ensures the HTML will dynamically display the correct data when the module runs.
         Reference Code for Integration:
         {code_guide}
          Include your revised HTML code below:
        ```insert revised html code here```
        """
        solution_generated = chain.invoke(solution_improvement)
    # print(code_guide)
    return solution_generated

# # Example usage of the function
# api_key = ""  # Replace with your actual API key
# csv_path = r"Question_Embedding_20240128.csv"  # Replace with your actual CSV path
# question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # Replace with your actual question
# print(question_solution_guide(question,api_key,csv_path))