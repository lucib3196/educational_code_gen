import sys
from typing import List, Optional, Union, Type
import logging

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from openai import OpenAI


# My Module Imports
from util_example_based_prompt import ExampleBasedPromptFormatter
from util_semantic_search import CSVDataHandler, SemanticSearch
import asyncio
from langchain_core.output_parsers import StrOutputParser
from util_validation import validate_question_html_format
from util_javascript_generator import js_generator
from util_string_extraction import extract_javascript_generate_code
output_parser = StrOutputParser()

class PromptFormatterFromRepository():
    EXAMPLE_OPTIONS_STRUCTURE = {
        "embedding_column": str,
        "search_column": str,
        "output_column": str,
        "n_examples": int
    }

    LLM_OPTIONS_STRUCTURE = {
        "llm_model": str,
        "temperature": str,
        "embedding_model": str
    }
    
    def __init__(self, api_key: str, csv_path: str, example_options: dict, llm_options: dict,prompt):
        # super().__init__()  # Call this only if inheriting from another class

        self._validate_options(example_options, self.EXAMPLE_OPTIONS_STRUCTURE, "Example Options")
        self._validate_options(llm_options, self.LLM_OPTIONS_STRUCTURE, "LLM Options")

        self.api_key = api_key
        self.csv_path = csv_path
        self.example_options = example_options
        self.llm_options = llm_options
        self.prompt = prompt

        self.data_handler = CSVDataHandler(csv_path=self.csv_path, embedding_column_name=self.example_options["embedding_column"])
        self.semantic_search_instance = SemanticSearch(csv_path=self.csv_path, embedding_column_name=self.example_options["embedding_column"], embedding_engine=self.llm_options["embedding_model"],api_key=self.api_key)

    def _validate_options(self, options, structure, option_name):
        if not all(key in options and isinstance(options[key], structure[key]) for key in structure):
            raise ValueError(f"Incorrect structure for {option_name}")

    def _extract_examples(self, question: str) -> str:
        examples = self.semantic_search_instance.extract_examples(
            input_string=question,
            search_column=self.example_options["search_column"],
            output_column=self.example_options["output_column"],
            n_examples=self.example_options["n_examples"]
        )
        return examples
    
    def _format_prompt(self,examples: List) -> str:
        prompt = self.prompt
        template = ExampleBasedPromptFormatter.run(examples,prompt)
        return template
    
    async def _get_responses_for_prompt(self, prompt: str, input_question: str) -> str:
        combined_prompt = f"{prompt}\ninput: {{input}}"
        prompt_instance = PromptTemplate(template=combined_prompt, input_variables=["input"])
        
        LLM = ChatOpenAI(
            model=self.llm_options["llm_model"],
            temperature=self.llm_options["temperature"],
            openai_api_key=self.api_key  # Assuming API key is used here
        )

        chain = LLMChain(
            llm=LLM,
            prompt=prompt_instance,
            output_parser=output_parser
        )

        # Ensure that the chain.invoke method is awaited
        response = chain.invoke({"input": input_question})
        return response
        
    async def _arun(self, question: str):
        examples = self._extract_examples(question)
        prompt = self._format_prompt(examples)
        
        # If prompt is a list of prompts
        if isinstance(prompt, list):
            responses = []
            for individual_prompt in prompt:
                string_prompt = ' '.join(individual_prompt)
                print(string_prompt)
                response = await self._get_responses_for_prompt(string_prompt, question)
                print(response)
                responses.append(response)
            
            # Return a single response or the list of responses
            return responses[0] if len(responses) == 1 else responses

        # If prompt is a single prompt
        else:
            response = await self._get_responses_for_prompt(prompt, question)
            return response["text"]
    

def builder_question_html(question:str,api_key:str,csv_path:str):
    example_options = {
        "embedding_column": "question_embedding",
        "search_column": "question",
        "output_column": "question.html",
        "n_examples": 4
    }

    llm_options = {
        "llm_model": "gpt-4",
        "temperature": "0",
        "embedding_model": "text-embedding-ada-002"
    }
    prompt = """
    Generate a html code based on the following examples"""
    
    code_generator = PromptFormatterFromRepository(api_key=api_key,csv_path=csv_path, example_options=example_options, llm_options=llm_options,prompt=prompt)
    html_generated = asyncio.run(code_generator._arun(str(question))).replace("{", "{{")
    html_generated = html_generated.replace("}","}}")
    return html_generated



def builder_server_js(question_html, api_key, csv_path, solution_guide=None, external_data=None):
    example_options = {
        "embedding_column": "question_embedding",
        "search_column": "question.html",
        "output_column": "server.js",
        "n_examples": 1
    }

    llm_options = {
        "llm_model": "gpt-4-0125-preview",
        "temperature": "0",
        "embedding_model": "text-embedding-ada-002"
    }

    # Construct the prompt
    guide_section = (f"Utilizing the provided step-by-step guide, craft a JavaScript function that executes the computations as detailed in the guide: {solution_guide}\n" 
                     if solution_guide else 
                     "Construct a JavaScript function that derives its logic from the computational problem at hand.\n")

    data_section = (f"// External Data Integration:\n"
                    f"// Utilize the following external data properties as needed: {external_data}\n"
                    f"// If specific properties or values are not provided, insert placeholder values accordingly.\n" 
                    if external_data else 
                    "// External Data Integration:\n"
                    "// If required, import external data properties or insert placeholder values as applicable.\n")

    base_template = f"""
        Design a robust JavaScript module adept at generating computational problems for various STEM disciplines. This module will ingest an HTML file containing a structured query and will output a JavaScript snippet that carries out the calculation for the problem described. The JavaScript code must conform to the following outline:

        const generate = () => {{
            {data_section}
            // 1. Dynamic Parameter Selection:
            // - Thoroughly analyze the HTML or data source to identify an extensive range of categories and units for computation.
            // - Ensure the inclusion of a wide variety of units and values, covering different global measurement systems.
            // - Develop a randomized selection algorithm to fairly choose a category or unit system, ensuring equitable representation.

            // 2. Appropriate Transformations:
            // - Implement precise and tailored conversion processes for each unit, ensuring accuracy in the transformation.
            // - Adapt the computations to maintain integrity, taking into account the specific characteristics of each unit system.
            // - Include robust validation and error handling to manage unusual or incorrect unit inputs, preserving computation reliability.

            // 3. Value Generation:
            // Produce random values relevant to the problem's context.
            // These values are the basis for the problem's arithmetic or logical operations.

            // 4. Solution Synthesis:
            // Utilize the selected parameters and the generated values to formulate the solution.
            // The computation should honor the problem's context, limitations, and nature to guarantee its validity.

            return {{
                params: {{
                    // Input parameters relevant to the problem's context and the chosen category/unit system.
                    // Export all calculated variables
                }},
                correct_answers: {{
                    // Calculate the correct answer(s) using the selected parameters and generated values.
                }},
                nDigits: 3,  // Define the number of digits after the decimal place.
                sigfigs: 3   // Define the number of significant figures for the answer.
            }};
        }}

        module.exports = {{
            generate
        }}

        Your mission is to flesh out the 'generate' function within this framework. It should dynamically select parameters and units, apply necessary transformations, spawn values, and deduce a legitimate solution. The function must return an object containing 'params' and 'correct_answers' properties, which abide by the prescribed structure. This alignment ensures that the HTML and JavaScript components integrate seamlessly. Below is a sample illustration:
        
        ```insert code here```
        """
    prompt = guide_section + base_template

    code_generator = PromptFormatterFromRepository(api_key=api_key, csv_path=csv_path, example_options=example_options, llm_options=llm_options, prompt=prompt)
    
    return asyncio.run(code_generator._arun(question_html))
def builder_server_py(question_html, api_key, csv_path, solution_guide=None, external_data=None):
    example_options = {
        "embedding_column": "question_embedding",
        "search_column": "question.html",
        "output_column": "server.py",
        "n_examples": 1
    }

    llm_options = {
        "llm_model": "gpt-4-0125-preview",
        "temperature": "0",
        "embedding_model": "text-embedding-ada-002"
    }

    # Construct the prompt
    guide_section = ""
    if solution_guide:
        guide_section = f"Utilize the provided step-by-step guide to construct a Python function that executes the computations as detailed in the guide: {solution_guide}\n"
    else:
        guide_section = "Create a Python function based on the computational problem provided.\n"

    data_section = ""
    if external_data:
        data_section = f"# External Data Integration:\n" \
                       f"# Use the following external data properties as needed: {external_data}\n" \
                       f"# If specific properties or values are not provided, insert placeholder values accordingly.\n"
    else:
        data_section = "# External Data Integration:\n" \
                       "# If required, import external data properties or insert placeholder values as applicable.\n"

        base_template = f"""
        Develop a Python module skilled in generating computational problems for various STEM disciplines. This module will process a structured query and will output a Python dictionary containing the parameters and solutions to the problem. Adhere to the following structure in the Python function:

        def generate_problem():
            {data_section}
            # Initialize the data dictionary to store parameters and answers
            data = {{'params': {{}}, 'correct_answers': {{}}}}

            # 1. Dynamic Parameter Selection:
            # Examine the structured query to identify suitable categories or units for computation.
            # Encompass a broad range of units and values.
            # Implement a random mechanism for choosing the appropriate category or unit system.

            # 2. Appropriate Transformations:
            # Execute necessary transformations based on the selected category or unit system.
            # Ensure these transformations preserve accuracy and computational validity.

            # 3. Value Generation:
            # Produce random values that align with the problem's context.
            # These values form the base of the problem's arithmetic or logical operations.

            # 4. Solution Synthesis:
            # Employ the selected parameters and generated values to derive the solution.
            # The computation should respect the problem's constraints, ensuring its validity and relevance.

            # Example: Storing parameters and solutions in the data dictionary
            # data['params']['example_param'] = generated_value
            # data['correct_answers']['example_answer'] = computed_solution

            return data

        Your responsibility is to complete the 'generate_problem' function following this framework. It must dynamically select parameters and units, perform transformations, generate values, and calculate a correct solution. The function should return a dictionary with 'params' and 'correct_answers' keys, abiding by the outlined structure. This methodology ensures a cohesive link between the structured query and the Python computation. Below is an illustration of how it might be implemented:
        """

    prompt = guide_section + base_template

    code_generator = PromptFormatterFromRepository(api_key=api_key, csv_path=csv_path, example_options=example_options, llm_options=llm_options, prompt=prompt)
    
    return asyncio.run(code_generator._arun(question_html))


def improve_solution(solution_html: str, code_reference:str,api_key:str,MODEL:str):
    """
    This function takes an existing HTML solution guide and a reference code snippet and
    uses an AI model to suggest improvements to the solution guide. The goal is to enhance
    the HTML guide by making it dynamic, user-friendly, and well-integrated with the provided
    code.

    Parameters:
    solution_html (str): The original HTML content of the solution guide.
    code_reference (str): A string of code that is used as a reference for generating dynamic content.
    api_key (str): The API key for authentication with the OpenAI service.
    MODEL (str): The model identifier to be used for generating the completion.

    Returns:
    str: The improved version of the HTML solution guide after applying the suggested enhancements.

    The function interfaces with the OpenAI API to submit the task and receive an improved version
    of the HTML guide. The improvements include the insertion of placeholders for dynamic content,
    enhancement of user interaction, and ensuring clarity within the guide. The result is an updated
    HTML code that should be effectively integrated with the provided code snippet.
    """
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
        Given the current HTML module for STEM problem-solving, your task is to enhance it using the provided code as a foundational guide. This code is designed to dynamically generate problem parameters and their correct answers. Your objective is to integrate these elements into the HTML solution guide effectively.
        Your Specific Tasks:
        1. **Review the Current ssolution guide  **: 
        Begin by examining the provided HTML solution guide  {solution_html}. 
        2. **Integrate Dynamic Content Using Placeholders**: Insert placeholders into the HTML that correspond to the outputs of the code. Use placeholders like `{{params.placeholder_value}}` or `{{correct_answers.placeholder_value}}` that align with the variable names and data formats in the code. This ensures the HTML will dynamically display the correct data when the module runs.
        4. **Enhance User Interaction and Clarity**: Make the HTML guide more user-friendly and informative. This could involve improving the layout, adding clearer instructions, or providing more detailed explanations within the solution guide.
        5. Ensure that the final correct answer is given as the last hint
        6. **Submit the Revised HTML Code**: Once you have made the necessary enhancements, return the updated HTML code. This revised code should reflect the changes you've made and demonstrate how it effectively integrates with the provided code.
        Reference Code for Integration:
        {code_reference}

        Include your revised HTML code below:
        ```insert revised html code here```
        """
        
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    )
    improved_solution = response.choices[0].message.content
    return improved_solution



def builder_solution_html(question_html, api_key, csv_path, solution_guide=None,code_reference=None):
    example_options = {
        "embedding_column": "question_embedding",
        "search_column": "question.html",
        "output_column": "solution.html",
        "n_examples": 3
    }

    llm_options = {
        "llm_model": "gpt-3.5-turbo-1106",
        "temperature": "0",
        "embedding_model": "text-embedding-ada-002"
    }

    final_template = ""
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
        final_template = template_with_guide
        

    if not final_template:
        # If neither solution_guide nor code was provided, use the default template
        final_template = """
        Create an HTML module for generating solutions to STEM problems. 
        Users will input an HTML file with a structured question, and the module should return an HTML solution. 
        Focus on the solution generation without providing a step-by-step guide. 
        Examine these example HTML questions and formulate corresponding HTML solutions:
        delimit the html  in ```insert_html_solution_guide```
        """

    code_generator = PromptFormatterFromRepository(api_key=api_key, csv_path=csv_path, example_options=example_options, llm_options=llm_options, prompt=final_template)
    first_solution_guide = asyncio.run(code_generator._arun(question_html))
    
    if code_reference:
        return improve_solution(first_solution_guide,code_reference=code_reference,api_key=api_key,MODEL= llm_options["llm_model"])
    return first_solution_guide



# def generate_all_components(api_key, csv_path, question):
#     """
#     Generates HTML, JavaScript, Python, and Solution Guide for a given question.

#     Note this only works for adaptive question, may and will not work for non adaptive questions. This is just a test 
#     Parameters:
#     api_key (str): API key for the service.
#     csv_path (str): Path to the CSV file.
#     question (str): The question to process.
#     """
#     # Generate HTML for the question
#     generated_html = builder_question_html(question, api_key=api_key, csv_path=csv_path)
#     print("Generated HTML:")
#     print(generated_html)

#     # Generate JavaScript
#     generated_javascript = builder_server_js(generated_html, api_key=api_key, csv_path=csv_path)
#     print("Generated JavaScript:")
#     print(generated_javascript)

#     # Generate Python code
#     generate_python = builder_server_py(generated_html, api_key=api_key, csv_path=csv_path)
#     print("Generated Python Code:")
#     print(generate_python)

#     # Generate Solution Guide
#     solution_guide = builder_solution_html(generated_html, api_key=api_key, csv_path=csv_path, code_reference=generated_javascript)
#     print("Generated Solution Guide:")
#     print(solution_guide)
    
    

# # Example usage of the function
# api_key = "insert api key here"  # Replace with your actual API key
# csv_path = r"Question_Embedding_20240128.csv"  # Replace with your actual CSV path
# question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # Replace with your actual question

# generate_all_components(api_key, csv_path, question)


def attempt_generate_html(question, api_key, csv_path, max_attempts=3):
    """
    Attempts to generate HTML for the given question and validates its format.

    Parameters:
    question (str): The question content or text.
    api_key (str): API key for the service.
    csv_path (str): Path to the CSV file.
    max_attempts (int): Maximum number of validation attempts.

    Returns:
    str: Validated HTML content for the question.
    """
    for attempt in range(max_attempts):
        question_html = builder_question_html(question, api_key, csv_path)
        try:
            validate_question_html_format(question_html)
            return question_html
        except ValueError as e:
            print(f"Attempt {attempt + 1}: HTML format validation failed: {e}")
    raise ValueError("Maximum validation attempts reached. Validation failed.")


def generate_code(input_question, is_adaptive_str, codelang, csv_path, api_key, solution_guide=None):
    """
    Generates code and solution HTML based on the question, adaptiveness, language preference, and solution guide.

    Parameters:
    input_question (str): The question content or text.
    is_adaptive_str (str): String representation indicating whether the question content is adaptive.
    codelang (str): The preferred coding language ('python', 'javascript', or 'both').
    solution_guide (str, optional): An optional solution guide.
    csv_path (str): Path to the CSV file.
    api_key (str): API key for the service.

    Returns:
    tuple: HTML for the question, Python code, JavaScript code, and solution HTML.
           Returns None for each element that isn't generated.
    """
    question_html, server_python, server_javascript, solution_html = None, None, None, None

    is_adaptive = is_adaptive_str.lower() == "true"

    if is_adaptive:
        question_html = attempt_generate_html(input_question, api_key, csv_path)

        if codelang in ["javascript", "both"]:
            server_javascript = js_generator(question_html, api_key, csv_path=csv_path, solution_guide=solution_guide)
        if isinstance(codelang, list):
            if codelang[0] in ["python", "both"]:
                server_python = js_generator(str(question_html), api_key, csv_path, solution_guide)

        extracted_code = extract_javascript_generate_code(str(server_javascript)) if server_javascript else None
        solution_html = builder_solution_html(str(question_html), api_key, csv_path, solution_guide, code_reference=extracted_code)
        solution_html = solution_html.replace("\n", "\\n").replace('"', '\\"')

    else:
        if codelang in ["python", "both"]:
            server_python = js_generator(str(question_html), api_key, csv_path, solution_guide)

        extracted_code = extract_javascript_generate_code(str(server_javascript)) if server_javascript else None
        solution_html = builder_solution_html(str(question_html), api_key, csv_path, solution_guide, code_reference=extracted_code)
        solution_html = solution_html.replace("\n", "\\n").replace('"', '\\"')

        question_html = builder_question_html(question=input_question, api_key=api_key, csv_path=csv_path)

    return question_html, server_python, server_javascript, solution_html



# # Example usage of the function
# api_key = ""  # Replace with your actual API key
# csv_path = r"Question_Embedding_20240128.csv"  # Replace with your actual CSV path
# question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # Replace with your actual question
# question_html,server_python,server_javascript,solution_html = generate_code(question,"true",csv_path=csv_path,api_key=api_key,codelang="javascript")
# print(question_html,server_javascript,solution_html)