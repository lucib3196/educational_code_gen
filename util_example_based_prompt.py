# Standard Library Imports
from typing import List, Optional, Union, Type
import logging
import sys
import re

from util_semantic_search import SemanticSearch
import pandas as pd


import re

class ExampleBasedPromptFormatter:
    """
    A class for formatting example-based prompts.
    This class provides functionalities to validate and format examples
    and generate prompts based on a template and a set of examples.
    """

    @staticmethod
    def _validate_input(extracted_examples, template_text):
        """
        Validates the input arguments.

        Args:
            extracted_examples (list): A list of example dictionaries.
            template_text (str): The template text for prompt generation.

        Raises:
            TypeError: If extracted_examples is not a list or template_text is not a string.
        """
        if not isinstance(extracted_examples, list):
            raise TypeError("Expected extracted_examples to be a list.")
        if not isinstance(template_text, str):
            raise TypeError("Expected template_text to be a string.")

    @staticmethod
    def _validate_example(example):
        """
        Validates an individual example dictionary.

        Args:
            example (dict): The example to validate.

        Raises:
            TypeError: If the example is not a dictionary or its 'input'/'output' are not strings.
            ValueError: If the example dictionary does not contain 'input' and 'output' keys.
        """
        if not isinstance(example, dict):
            raise TypeError(f"Expected each example to be a dictionary, but got {type(example)} instead.")
        if 'input' not in example or 'output' not in example:
            raise ValueError("Each example dictionary should have both 'input' and 'output' keys.")
        if not isinstance(example['input'], str) or not isinstance(example['output'], str):
            raise TypeError("Both 'input' and 'output' should be strings.")

    @staticmethod
    def _format_example_set(example_set):
        """
        Formats a set of examples.

        Args:
            example_set (list): A list of example dictionaries.

        Returns:
            str: A string of formatted examples.
        """
        formatted_examples = []
        for example in example_set:
            ExampleBasedPromptFormatter._validate_example(example)
            if pd.isna(example['output']):
                example['output'] = "PLACEHOLDER"
            formatted_example = f"input: {ExampleBasedPromptFormatter._escape_curly_brackets(example['input'])}\noutput: {ExampleBasedPromptFormatter._escape_curly_brackets(str(example['output']).strip())}"
            formatted_examples.append(formatted_example)
        return "\n\n".join(formatted_examples)

    @staticmethod
    def _escape_curly_brackets(text):
        """
        Escapes curly brackets in a string.

        Args:
            text (str): The text to escape curly brackets in.

        Returns:
            str: The text with curly brackets escaped.
        """
        return re.sub(r'(?<!\{)\{(?!\{)', '{{', re.sub(r'(?<!\})\}(?!\})', '}}', text))

    @staticmethod
    def _generate_prompt(formatted_example, template_text):
        """
        Generates a prompt based on formatted examples and a template.

        Args:
            formatted_example (str): The formatted examples.
            template_text (str): The template text for prompt generation.

        Returns:
            str: The generated prompt.
        """
        return [f"{ExampleBasedPromptFormatter._escape_curly_brackets(template_text)}\n{formatted_example}\n"]

    @staticmethod
    def run(examples, template_text):
        """
        Main method to run the prompt formatter.

        Args:
            examples (list): A list of example dictionaries.
            template_text (str): The template text for prompt generation.

        Returns:
            str: The generated prompt.
        """
        ExampleBasedPromptFormatter._validate_input(examples, template_text)
        formatted_examples = ExampleBasedPromptFormatter._format_example_set(examples)
        prompt = ExampleBasedPromptFormatter._generate_prompt(formatted_examples, template_text)
        return prompt[0]
    
    
# # Configuration variables
# api_key = "insert api - key here"  # Replace with your actual API key
# data_csv_path = "Question_Embedding_20240128.csv"  # Previously mentioned CSV path
# embedding_model_name = "text-embedding-ada-002"  # Specify the embedding model name
# input_question = "A car travels for a distance of 5mph for 30 minutes what is the distance traveled?"  # The provided example question
# search_column = "question"  # The previously mentioned search column
# number_of_examples = 3  # Number of examples to extract
# template = "Your formatting template here"  # Replace with your formatting template

# # Initialize the SemanticSearch instance with the API key
# semantic_search_instance = SemanticSearch(data_csv_path, "question_embedding", embedding_model_name, api_key=api_key)

# # Extract examples using SemanticSearch
# examples = semantic_search_instance.extract_examples(
#     input_string=input_question,
#     search_column=search_column,
#     output_column="question.html",
#     n_examples=number_of_examples
# )

# # Use the ExampleBasedPromptFormatter to format the extracted examples
# formatted_prompt = ExampleBasedPromptFormatter.run(examples, template)

# # Print the formatted prompt
# print(formatted_prompt)
