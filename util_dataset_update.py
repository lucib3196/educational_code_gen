import ast
from openai import OpenAI
import pandas as pd
import os 
import datetime

class QuestionProcessor:
    def __init__(self, model_name:str, embedding_model:str,api_key:str):
        """
        Initializes the QuestionProcessor with specified OpenAI models.

        Parameters:
        - model_name (str): The name of the OpenAI model used for text generation and classification.
        - embedding_model (str): The name of the OpenAI model used for generating text embeddings.

        Returns:
        - None
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model_name
        self.embedding_model = embedding_model

    def classify_question(self, question): 
        """
        Classifies a given question as 'conceptual' or 'computational'.

        Parameters:
        - question (str): The question text to be classified.

        Returns:
        - str: The classification of the question ('conceptual' or 'computational').
        """
        prompt = f"""
        **Instructions:**
        Determine if the provided question is "conceptual" or "computational". 
        - A "conceptual" question is one that does not require numerical calculations or data manipulation. These questions often test understanding of theories, principles, or ideas and may include multiple-choice or true/false questions.
        - A "computational" question requires numerical calculations, data analysis, or the use of algorithms. These questions often involve solving problems using mathematical methods or computer programs.
        **Example:**
        Question: "What is the capital of France?"
        Answer: Conceptual (This question tests knowledge of a fact and does not require any computational effort.)
        Question: "Calculate the gravitational force between two masses of 5 kg and 10 kg placed 2 meters apart."
        Answer: Computational (This question requires numerical calculations based on a physical formula.)
        **Now, categorize the following question:**
        {question}
        **Answer:**
        question_type:"""

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format= { "type": "json_object" },
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                #print(response)
                classification = ast.literal_eval(response.choices[0].message.content)
                #print("this is the classification",classification)
                return classification["question_type"]
            except ValueError as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_attempts}.")
                if attempt == max_attempts - 1:
                    raise

        return "Unable to classify question after multiple attempts."

    def reformat_conceptual(self, question):
        """
        Reformats a conceptual question into a textbook-like format.

        Parameters:
        - question (str): The HTML content of a conceptual question.

        Returns:
        - str: The reformatted question in a textbook-like format.
        """
        prompt = f"""
        Based on this input HTML, determine the question being asked including any options.
        Format it in a manner reminiscent of a textbook. Do not solve the question 
        Input: {question}
        Return the output in the following format:
        Question: Extracted question + options
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                result = completion.choices[0].message.content.strip()
                if result.lower().startswith("question:"):
                    return result[len("question:"):].strip()
                else:
                    raise ValueError("Response format not as expected.")
            except Exception as e:
                if attempt == max_attempts - 1:
                    return f"Error: {e}"

        return "Error: Unable to process the question."

    def reformat_computational(self, question):
        """
        Reformats a computational question by replacing placeholders with realistic values.

        Parameters:
        - question (str): The computational question with placeholders.

        Returns:
        - str: The reformatted question with placeholders replaced by suitable values.
        """
        prompt = f"""
        **Instructions:**

        You are presented with a series of questions that involve replacing placeholder values in a given context. Your task is to generate suitable and realistic values for these placeholders while preserving the formal structure of textbook-style questions.

        **Guidelines:**

        - Placeholder variables are indicated within double curly braces, like {{{{params.value}}}}.
        - Maintain the original question structure for coherence.
        - Use appropriate units for values (e.g., meters, seconds, kilograms, etc.).
        - Ensure your values align with the context and maintain accuracy.
        - Feel free to use positive or negative numbers as required.

        **Examples:**

        1. Input: Consider two numbers: a = {{params.a}} and b = {{params.b}}. What is the sum c = a + b?
        Output: Consider two numbers: a = 3 and b = -8. What is the sum c = a + b?

        2. Input: A vehicle of mass {{params.md}} kg accelerates from rest to a speed of {{params.vd}} m/s in {{params.t}} seconds. What is the net force (in newtons) on the vehicle? Neglect external forces.
        Output: A vehicle of mass 1500 kg accelerates from rest to a speed of 25 m/s in 6 seconds. What is the net force (in newtons) on the vehicle? Neglect external forces.

        3. Input: A ball is thrown with a speed of {{params.v}} m/s at an angle {{params.theta}} degrees. A player at a distance {{params.r}} meters runs towards the ball to catch it.
        What is the speed (in m/s) at which the player must run to catch the ball?
        How far (in meters) does the player run to catch the ball?
        How long does the player (in seconds) run to catch the ball?
        Output: A ball is thrown with a speed of 20 m/s at an angle 30 degrees. A player at a distance 10 meters runs towards the ball to catch it.
        1. What is the speed (in m/s) at which the player must run to catch the ball?
        2. How far (in meters) does the player run to catch the ball?
        3. How long does the player (in seconds) run to catch the ball?
        

        Input: {question}
        """
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            try:
                completion =self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": prompt}
                    ],
                    #response_format="json_object",
                    temperature=0
                )
                # Assuming the response structure is correct
                result = completion.choices[0].message.content.lower()
                if result.startswith("output"):
                    result = result[7:].strip()
                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                attempts += 1

        return "Could not get a valid response after multiple attempts."
    
    def clean_question(self,question):
            """
            Cleans a given question by classifying and reformating it based on its type.

            Parameters:
            - question (str): The question text to be cleaned.

            Returns:
            - str: The cleaned and reformatted question.
            """
            # Classify Question Type
            question_type = self.classify_question(question).lower()
            
            if question_type == "conceptual":
                cleaned_question = self.reformat_conceptual(question)
                return cleaned_question
            elif question_type == "computational":
                cleaned_question = self.reformat_computational(question)
                return cleaned_question
            
    def embedd_question(self,question):
        """
        Generates embeddings for a given question after cleaning it.

        Parameters:
        - question (str): The question text to generate embeddings for.

        Returns:
        - tuple: A tuple containing the cleaned question and its corresponding embeddings.
        """
        cleaned_question = self.clean_question(question)
        
        response = self.client.embeddings.create(
        input=cleaned_question,
        model=self.embedding_model)
        
        return cleaned_question,response.data[0].embedding
    def pretty_embedding(self,question):
        """
        Generates and displays embeddings for a given question along with the question text.

        Parameters:
        - question (str): The question text for which embeddings are to be generated.

        Returns:
        - None: Prints the cleaned question and a portion of its embeddings.
        """
         # Get the embeddings for the question
        cleaned_question,embeddings = self.embedd_question(question)
        # Print the question
        print(f"Orignal Question in html format", {question},"\n")
        print(f"Cleaned Question: {cleaned_question}","\n")
        # Print a portion of the embeddings
        print("Embeddings (partial):", embeddings[:8])  # Adjust the slice as needed
        
class DatasetUpdater:
    def __init__(self, source_folder_path, current_dataset_csv_path,files_to_process,export_directory_path,api_key:str):
        """
        Initializes the DatasetUpdater instance.

        :param source_folder_path: The path to the folder containing source files for data extraction.
        :param current_dataset_csv_path: The file path of the current dataset stored as a CSV file.
        :param files_to_process: A list of filenames to be processed within the source folder.
        :param export_directory_path: The directory path where the updated dataset will be exported as a CSV file.
        """
        self.source_folder_path = source_folder_path
        self.current_dataset_csv_path = current_dataset_csv_path
        self.files_to_process = files_to_process
        self.export_directory_pathpath = export_directory_path
        
        
        self.temp_dataset = None
        self.dataset = None
        self.combined_dataset = None
        self.contents = {}
        
        self.question_processor = QuestionProcessor("gpt-3.5-turbo-1106","text-embedding-ada-002",api_key=api_key)
        
    def load_dataset(self):
        """
        Loads the dataset from the current CSV file into a pandas DataFrame.

        :return: The dataset loaded into a pandas DataFrame, or None if an error occurs.
        """
        try:
            self.dataset = pd.read_csv(self.current_dataset_csv_path)
            return self.dataset
        except FileNotFoundError:
            print(f"File not found: {self.current_dataset_csv_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def extract_specific_files_contents(self):
        """
        Extracts contents of specific files from the source directory and its subdirectories.
        
        :return: A dictionary containing the contents of the specified files, organized by folder names.
        """
        
        for root, dirs,files in os.walk(self.source_folder_path):
            for filename in files:
                if filename in self.files_to_process:
                    folder_name = os.path.basename(root)
                    file_path = os.path.join(root,filename)
                    with open(file_path,"r") as file:
                        if folder_name not in self.contents:
                            self.contents[folder_name] = {}
                        self.contents[folder_name][filename] = file.read()
        return self.contents
    def dict_to_dataframe(self):
        """
        Converts the extracted file contents (self.contents) into a pandas DataFrame.

        :return: A pandas DataFrame with folder names as index and file contents as columns.
        """
        # Convert the nested dictionary into a format suitable for DataFrame
        
        # Ensure that file contents are extracted
        if not self.contents:
            self.extract_specific_files_contents()
            
            
        formatted_data = []
        for folder, files in self.contents.items():
            row_data = {'Question Title': folder}
            row_data.update(files)
            formatted_data.append(row_data)

        # Create the DataFrame
        df = pd.DataFrame(formatted_data)
        df = df.set_index('Question Title')
        self.temp_dataset = df
        return self.temp_dataset
    def create_question_embedding_columns(self):
        """
        Processes each question in the temporary dataset to generate and append question embeddings.

        :return: The temporary dataset with additional columns for cleaned questions and their embeddings.
        """
        if not self.contents:
            self.dict_to_dataframe()

        # Initialize new columns with default values
        self.temp_dataset['question'] = ''
        self.temp_dataset['question_embedding'] = [[] for _ in range(len(self.temp_dataset))]

        for index, row in self.temp_dataset.iterrows():
            cleaned_question, embedding = self.question_processor.embedd_question(row["question.html"])
            
            # Update the DataFrame with the new values
            self.temp_dataset.at[index, 'question'] = cleaned_question
            self.temp_dataset.at[index, 'question_embedding'] = embedding
        return self.temp_dataset
        
    def merge_dataframes(self):
        """
    Merges the existing dataset with the temporary dataset, appending new data and removing duplicates.

    :return: The combined dataset as a pandas DataFrame, or raises a ValueError in case of an error.
    """
        try:
            if not self.contents:
                self.create_question_embedding_columns()
            if not self.dataset:
                self.load_dataset()

                # Reset the index if 'Question Title' is set as index
            if self.dataset.index.name == 'Question Title':
                self.dataset.reset_index(inplace=True)
            if self.temp_dataset.index.name == 'Question Title':
                self.temp_dataset.reset_index(inplace=True)

            # Append temp_dataset to dataset
            self.combined_dataset = pd.concat([self.dataset, self.temp_dataset], ignore_index=True)

            # Remove duplicates if they exist, keeping the last occurrence (which should be from temp_dataset)
            self.combined_dataset.drop_duplicates(subset='Question Title', keep='last', inplace=True)

            # Optionally, you can set 'Question Title' back as the index
            self.combined_dataset.set_index('Question Title', inplace=True)
            
            return self.combined_dataset

        except Exception as e:
            raise ValueError(f"Merge failed: {e}")
            
    def export_to_csv(self):
        """
    Exports the combined dataset to a CSV file in the specified export directory.

    If the combined dataset is None (i.e., not available), prints a message indicating no dataset to export.
    """
        if self.combined_dataset is not None:
            # Format the current date as YYYYMMDD
            current_date = datetime.datetime.now().strftime("%Y%m%d")
            file_name = f"Question_Embedding_{current_date}.csv"
            file_path = os.path.join(self.export_directory_pathpath, file_name)

            # Export the combined dataset to a CSV file
            self.combined_dataset.to_csv(file_path, index=True)

            print(f"Dataset exported to {file_path}")
        else:
            print("No dataset available to export.")      
            
    def run(self):
        self.merge_dataframes()
        self.export_to_csv()
        



# # Configuration variables
# api_key = "your_openai_api_key"  # Replace with your actual API key
# gpt_model_name = "gpt-3.5-turbo-1106"
# embedding_model_name = "text-embedding-ada-002"
# example_text = "\n If the maximum acceleration of a car is {{params.a}} {{params.unitsAcceleration}}. \n What is the 0-60 mph time in seconds?\n\n"

# source_folder_path = "path/to/source/folder"  # Replace with the actual source folder path
# current_dataset_csv_path = "path/to/current/dataset.csv"  # Replace with the actual CSV path
# files_to_process = ["question.html", "server.js", "server.py", "info.json", "solution.html"]
# export_directory_path = "path/to/export/directory"  # Replace with the actual export directory path

# # Initialize the classifier uncomment if needed 
# # classifier = QuestionProcessor(gpt_model_name, embedding_model_name, api_key=api_key)

# # Process the example text (uncomment if needed)
# # classifier.pretty_embedding(example_text)

# # Initialize the dataset updater
# data_set_updater = DatasetUpdater(
#     source_folder_path=source_folder_path,
#     current_dataset_csv_path=current_dataset_csv_path,
#     files_to_process=files_to_process,
#     export_directory_path=export_directory_path,
#     api_key=api_key
# )

# # Run the dataset updater (uncomment if needed)
# # data_set_updater.run()