import sys
import os
import logging
import pandas as pd
import ast
import re
from openai import OpenAI
import numpy as np




class FileHandler:
    """
    FileHandler is a utility class designed for handling CSV files. It allows for 
    reading data from specified CSV paths and provides checks and error-handling 
    mechanisms to ensure the CSV file's integrity and existence.

    Attributes:
    -----------
    csv_path : str
        The path to the CSV file that this handler manages.

    Methods:
    --------
    load_data(**kwargs) -> pd.DataFrame:
        Loads data from the specified CSV path into a Pandas DataFrame. Provides 
        error handling for cases like an empty file or parsing issues.

    _check_file_exists():
        A private method to check the existence of the CSV file and raise an error 
        if not found.
    """
    def __init__(self,csv_path:str):
        """
        Initialize the FileHandler with the provided CSV path.

        Args:
            csv_path (str): Path to the CSV file.
        """
        self.csv_path = csv_path

    def _check_file_exist(self):
        """
        Check if the file exists. Raise a FileNotFoundError if it doesn't.

        Raises:
            FileNotFoundError: If the CSV file doesn't exist.
        """
        if not os.path.isfile(self.csv_path):
            return FileNotFoundError(f"No File Found at {self.csv_path}")

    def load_data(self, **kwargs)-> pd.DataFrame:
        """
        Load data from the provided CSV path.

        Args:
            **kwargs: Arbitrary keyword arguments passed directly to pandas read_csv function.

        Returns:
            pd.DataFrame: Loaded DataFrame from CSV.

        Raises:
            ValueError: If there's an issue with the CSV file content.
            FileNotFoundError: If the CSV file doesn't exist.
        """
        self._check_file_exist()

        try: 
            return pd.read_csv(self.csv_path,**kwargs)
        except pd.errors.EmptyDataError:
            raise ValueError((f"The file at {self.csv_path} is empty."))
        except pd.errors.ParserError:
            raise ValueError(f"Error parsing the file at {self.csv_path}. Ensure it's a valid CSV.")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while reading the file at {self.csv_path}. Original error: {str(e)}")
        
class EmbeddingColumnProcessor:
    """
    EmbeddingColumnProcessor is a utility class aimed at processing an embedding column within a DataFrame.

    This class is designed to handle DataFrames where an embedding column contains string representations
    of lists, which need to be converted into lists of floats. Such processing is often required in
    tasks involving semantic analysis, search, and machine learning where embeddings are used.

    Attributes:
        embedding_column_name (str): The name of the column in the DataFrame containing the embeddings.
    """

    def __init__(self, embedding_column_name: str):
        """
        Initializes the EmbeddingColumnProcessor with the specified embedding column name.

        Args:
            embedding_column_name (str): The name of the embedding column to be processed.
        """
        self.embedding_column_name = embedding_column_name

    def process_embedding_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the embedding column of the given DataFrame.

        The method converts the string representation of lists in the embedding column into actual lists
        of floats. This is typically required when embeddings are loaded from a CSV file where they are
        stored as strings.

        Args:
            df (pd.DataFrame): The DataFrame with the embedding column to process.

        Returns:
            pd.DataFrame: The DataFrame with the processed embedding column.

        Raises:
            ValueError: If the string representation cannot be evaluated or list elements cannot be converted to floats.
        """
        # Convert string representation to list
        try:
            df[self.embedding_column_name] = df[self.embedding_column_name].apply(ast.literal_eval)
        except ValueError as e:
            raise ValueError(f"Failed to evaluate the string representation in {self.embedding_column_name} column.") from e
        
        # Convert list elements to floats
        try:
            df[self.embedding_column_name] = df[self.embedding_column_name].apply(lambda x: [float(i) for i in x])
        except ValueError as e:
            raise ValueError(f"Failed to convert values in {self.embedding_column_name} column to floats.") from e

        return df
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the DataFrame if it contains the specified embedding column.

        This method is a general processor that can be extended to include additional DataFrame
        processing steps. Currently, it checks for the presence of the embedding column and processes it.

        Args:
            df (pd.DataFrame): The DataFrame to process.

        Returns:
            pd.DataFrame: The processed DataFrame.
        """
        if self.embedding_column_name in df.columns:
            df = self.process_embedding_column(df)
        return df
    
class CSVDataHandler:
    """
    CSVDataHandler is a class responsible for managing and processing data from a specified CSV file. 
    It uses a FileHandler for loading the data and an EmbeddingColumnProcessor for processing specific 
    columns in the data.

    This class is designed with a lazy loading mechanism, where the DataFrame is only loaded and processed 
    when needed. It also supports a manual refresh to reload and reprocess the data.
    
    Attributes:
        file_handler (FileHandler): Instance of FileHandler for handling file operations.
        embedding_column_name (str): The name of the embedding column to be processed.
        embedding_processor (EmbeddingColumnProcessor): Processor for the embedding column.
        _dataframe (pd.DataFrame): Internal variable to store the loaded and processed DataFrame.
    """

    def __init__(self, csv_path: str, embedding_column_name: str):
        """
        Initialize the CSVDataHandler with the provided CSV file path and the embedding column name.

        Args:
            csv_path (str): Path to the CSV file.
            embedding_column_name (str): Name of the column containing embeddings.
        """
        self.file_handler = FileHandler(csv_path)
        self.embedding_column_name = embedding_column_name
        self.embedding_processor = EmbeddingColumnProcessor(embedding_column_name)
        self._dataframe = None

    def dataframe(self) -> pd.DataFrame:
        """
        Lazily loads and processes the DataFrame from the CSV file. If the DataFrame is already loaded, 
        it returns the existing DataFrame; otherwise, it loads and processes it first.

        Returns:
            pd.DataFrame: The processed DataFrame from the CSV file.
        """
        if self._dataframe is None:
            self._load_and_process_data()
        return self._dataframe

    def _load_and_process_data(self):
        """
        Private method to load data from the CSV file and process it using the EmbeddingColumnProcessor.
        """
        self._dataframe = self.file_handler.load_data()
        self._dataframe = self.embedding_processor.process_dataframe(self._dataframe)

    def refresh_data(self):
        """
        Refreshes the data by setting the internal DataFrame to None and then reloading and reprocessing it.
        This is useful if the CSV file has been updated or if a reprocessing is required.
        """
        self._dataframe = None
        self._load_and_process_data()
        


class SemanticSearch:
    """
    The SemanticSearch class provides methods to perform semantic-based searches on a DataFrame.
    It utilizes embeddings (e.g., from OpenAI) to find and extract examples that are semantically
    similar to a provided input string.

    Attributes:
        csv_path (str): Path to the CSV file.
        embedding_column_name (str): Name of the column containing embeddings in the DataFrame.
        embedding_engine (str): Name or type of the embedding engine to be used.
        csv_data_handler (CSVDataHandler): Instance of CSVDataHandler to handle CSV data operations.
        dataframe (pd.DataFrame): DataFrame loaded and processed from the CSV file.
    """

    def __init__(self, csv_path: str, embedding_column_name: str, embedding_engine: str,api_key:str):
        """
        Initializes the SemanticSearch class with the specified CSV path, embedding column name, 
        and embedding engine.

        Args:
            csv_path (str): Path to the CSV file.
            embedding_column_name (str): Name of the column containing embeddings in the DataFrame.
            embedding_engine (str): Name or type of the embedding engine to be used.
        """
        self.csv_path = csv_path
        self.embedding_column_name = embedding_column_name
        self.embedding_engine = embedding_engine
        self.csv_data_handler = CSVDataHandler(csv_path, embedding_column_name)
        self.dataframe = self.csv_data_handler.dataframe()
        self.client = OpenAI(api_key=api_key)

    def _validate_column(self, column_name: str):
        """
        Validates if the specified column name exists in the DataFrame.

        Args:
            column_name (str): The name of the column to validate.

        Raises:
            ValueError: If the column name does not exist in the DataFrame.
        """
        if column_name not in self.dataframe.columns:
            raise ValueError(f"'{column_name}' is not a valid column name in the DataFrame.")

    def _validate_input_string(self, input_string: str):
        """
        Validates if the input is a string.

        Args:
            input_string (str): The input string to validate.

        Raises:
            TypeError: If the input is not a string.
        """
        if not isinstance(input_string, str):
            raise TypeError("Expected input to be a string.")

    def semantic_search(self, input_string: str, search_column: str, n_examples: int, similarity_threshold=0.8):
        """
        Performs a semantic search on the DataFrame, returning examples similar to the input string.

        Args:
            input_string (str): The input string for semantic comparison.
            search_column (str): The name of the column in the DataFrame to search against.
            n_examples (int): Number of similar examples to return.
            similarity_threshold (float, optional): The threshold for considering an example as similar. Defaults to 0.7.

        Returns:
            list: A list of tuples with the format (index, value from search_column, similarity score).

        Notes:
            This method requires an external service or library to calculate embeddings.
        """
        self._validate_input_string(input_string)
        self._validate_column(search_column)
        self._validate_column(self.embedding_column_name)

        if self.dataframe.empty:
            print("Dataframe is empty.")
            return []

        try:
            # Replace the following line with actual embedding generation using the specified engine
            question_embedding_response = self.client.embeddings.create(input = input_string, model=self.embedding_engine)  # Placeholder function

            question_embedding = question_embedding_response.data[0].embedding
             
            similarities = [
                (index, row[search_column], np.dot(row[self.embedding_column_name], question_embedding))
                for index, row in self.dataframe.iterrows() 
                if self.embedding_column_name in row and isinstance(row[self.embedding_column_name], list)
            ]

            filtered_similarities = [entry for entry in similarities if entry[2] >= similarity_threshold]
            sorted_matches = sorted(filtered_similarities, key=lambda x: x[2], reverse=True)[:n_examples]

            return sorted_matches

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
    def extract_examples(self, input_string: str, search_column: str, output_column: str, n_examples: int) -> list:
        """
        Extracts examples from the DataFrame based on semantic search results.

        Args:
            input_string (str): The input string for semantic comparison.
            search_column (str): The name of the column in the DataFrame to search against.
            output_column (str): The column from which to extract outputs.
            n_examples (int): Number or similar examples to return
            Returns:
        list: A list of dictionaries containing 'input' and 'output' pairs from the semantic search results.
    """
        # Column Validation for 'search_column', 'output_column', and 'question_embedding'
        self._validate_column(search_column)
        self._validate_column(output_column)
        self._validate_column(self.embedding_column_name)

        # Exclude rows with missing values for the output_column
        valid_rows = self.dataframe.dropna(subset=[output_column])
        self.dataframe = valid_rows

        semantic_results = self.semantic_search(input_string, search_column, n_examples)

        all_examples = []
        for results in semantic_results:
            if isinstance(results, tuple) and len(results) == 3:
                index, input_answer, _ = results
                example = {
                    "input": input_answer,
                    "output": self.dataframe.loc[index, output_column]
                }
                all_examples.append(example)
            else:
                print(f"Unexpected format for 'results': {results}")

        return all_examples
    

    def pretty_print_semantic_results(self, input_string: str, search_column: str, n_examples: int):
        """
        Prints the semantic search results in a formatted and readable manner.

        Args:
            input_string (str): The original input string used for the semantic search.
            search_column (str): The name of the column in the DataFrame to search against.
            n_examples (int): Number of similar examples to display.
        """
        semantic_results = self.semantic_search(input_string, search_column, n_examples)
        print(f"Semantic Search Results for: '{input_string}'\n")
        print(f"{'Index':<10}{'Similarity Score':<20}{'Semantic Example':<60}")
        print("-" * 90)

        for index, example, similarity_score in semantic_results:
            display_example = (example[:100] + '...') if len(example) > 60 else example
            print(f"{index:<10}{similarity_score:<20.2f}{display_example:<60}")

        print("\n")
        
    def pretty_print_extracted_examples(self, input_string: str, search_column: str, output_column: str, n_examples: int):
        """
        Retrieves and prints the extracted examples in a formatted and readable manner.

        Args:
            input_string (str): The input string for semantic comparison.
            search_column (str): The name of the column in the DataFrame to search against.
            output_column (str): The column from which to extract outputs.
            n_examples (int): Number of similar examples to retrieve and display.
        """
        print(f"Extracted Examples for: '{input_string}'\n")
        print(f"{'Input Example':<60}{'Output Example':<60}")
        print("-" * 120)
        
        extracted_examples = self.extract_examples(input_string, search_column, output_column, n_examples)

        for example in extracted_examples:
            # Truncate long strings for display
            display_input = (example['input'][:57] + '...') if len(example['input']) > 60 else example['input']
            display_output = (example['output'][:57] + '...') if len(example['output']) > 60 else example['output']
            print(f"{display_input:<60}{display_output:<60}")

        print("\n")
        
        
api_key = "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"  # Replace with your actual API key                
# Configuration variables
data_csv_path = "Question_Embedding_20240128.csv"
embedding_model_name = "text-embedding-ada-002"
input_question = "A wire of circular cross-section has a tensile force of 60.0N applied to it and this force produces a stress of 3.06 MPa in the wire determine the diameter of the wire?"
search_column = "question"  # Column name in the CSV
number_of_examples = 3

# Initialize the SemanticSearch instance
semantic_search_instance = SemanticSearch(data_csv_path, "question_embedding", embedding_model_name,api_key=api_key)

# Extract examples using SemanticSearch
extracted_examples = semantic_search_instance.extract_examples(
    input_string=input_question,
    search_column=search_column,
    output_column="solution.html",
    n_examples=number_of_examples
)

# Print the extracted examples (uncomment if needed)
print(extracted_examples)

# Pretty print extracted examples (uncomment if needed)
semantic_search_instance.pretty_print_extracted_examples(
    input_question,
    search_column=search_column,
    output_column="question.html",
    n_examples=number_of_examples
)

# Pretty print semantic search results (uncomment if needed)
semantic_search_instance.pretty_print_semantic_results(
    input_question,
    search_column,
    number_of_examples
)

# ## Questions to modify function 

# # multiple_choice_obvious = On a velocity-time graph, a downward sloping line indicates: these are the options for the multiple choice a body decelerating(correct answer),a body accelerating a body moving in the negative direction ,a body moving at constant speed
# # multiple_choice_implicit = Multiple choice quesiton. A plane has taken off the runway and has gained a speed of 300 mph making an angle 15 degrees with the horizontal. When the plane is 1600 ft off the ground, a loose nut detaches the plane and falls to the ground. Neglect air resistance and assume the plane travels in a straight line at constant speed. Which of the following is true when the nut hits the ground? The plane is vertically above the point at which the nut hits the ground (correct) The plane has travelled a greater horizontal distance than the nut and hence is ahead of the nut.The plane has travelled less horizontal distance than the nut, and hence is behind the nut. There is insufficient information to provide a definite answer
    