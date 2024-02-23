import asyncio

# Custom Modules
from util_metadata_generator import QuestionMetaDataGenerator
from util_code_generation import builder_question_html,builder_server_js,builder_solution_html,builder_server_py
from utils_user_input import collect_user_preferences,extract_question_based_on_type,prompt_generate_question_variations,prompt_generate_question_variations
from util_generate_variations import GenerateVariation
from util_generation_misc import create_variation_solution
from util_string_extraction import extract_javascript_generate_code
from util_file_export import create_folder,export_files
from util_validation import validate_question_html_format
from util_javascript_generator import js_generator


# API Key
api_key = "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"
# LLM model
model = "gpt-4-0125-preview"

# Csv path 
csv_path = r"Question_Embedding_20240128.csv"

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
        print(question_html)
        try:
            validate_question_html_format(question_html)
            return question_html
        except ValueError as e:
            print(f"Attempt {attempt + 1}: HTML format validation failed: {e}")
    raise ValueError("Maximum validation attempts reached. Validation failed.")
def generate_code(input_question, isAdaptive, codelang, solution_guide=None, csv_path=csv_path, api_key=api_key, model=model):
    """
    Generates code and solution HTML based on the question, adaptiveness, language preference, and solution guide.

    Parameters:
    input_question (str): The question content or text.
    isAdaptive (bool or str): Indicates whether the question content is adaptive.
    codelang (str): The preferred coding language ('python', 'javascript', or 'both').
    solution_guide (str, optional): An optional solution guide.
    csv_path (str): Path to the CSV file.
    api_key (str): API key for the service.
    model (str): The model used for generating code.

    Returns:
    tuple: HTML for the question, Python code, JavaScript code, and solution HTML. 
           Returns None for each element that isn't generated.
    """
    question_html, server_python, server_javascript, solution_html = None, None, None, None

    is_adaptive_true = str(isAdaptive).lower() == "true"

    if is_adaptive_true:
        print("This is the input question",input_question)
        question_html = attempt_generate_html(str(input_question), api_key, csv_path)

        if codelang in ["python", "both"]:
            server_python = builder_server_py(str(question_html), api_key, csv_path, solution_guide)
        if codelang in ["javascript", "both"]:
            server_javascript = js_generator(question_html,api_key,csv_path=csv_path,solution_guide=solution_guide)

        extracted_code = extract_javascript_generate_code(str(server_javascript)) if server_javascript else None
        solution_html = builder_solution_html(str(question_html), api_key, csv_path, solution_guide, code_reference=extracted_code)
        solution_html.replace("\n", "\\n").replace('"', '\\"')
        return question_html, server_python, server_javascript, solution_html
    else:
        question_html = builder_question_html(question=input_question,api_key=api_key,csv_path=csv_path)
        
        return question_html, server_python, server_javascript, solution_html


def generate_metadata(question, user_data):
    """
    Generates metadata for a given question based on user's code language preference.

    Parameters:
    question (str): The question for which metadata is to be generated.
    user_data (dict): User data containing the code language preference and creator information.

    Returns:
    Depending on the code language preference, it returns either metadata for one language,
    or a tuple of metadata for both JavaScript and Python.
    """
    # Initialize the metadata generator
    metadata_generator = QuestionMetaDataGenerator(api_key)

    # Retrieve the user's preferred coding language
    code_lang_preference = user_data.get("codePreference")

    # If the user prefers a specific language (not both), generate metadata for that language
    if code_lang_preference != "both":
        return metadata_generator.extract(question=question, createdBy=user_data.get("createdBy"), codelang=code_lang_preference)

    # If the user prefers both languages, generate metadata for JavaScript
    metadata_js, usage = metadata_generator.extract(question=question, createdBy=user_data.get("createdBy"), codelang="javascript")
    
    # Create a copy of the JavaScript metadata for Python
    metadata_python = metadata_js.copy()
    metadata_python["codelang"] = "python"

    # Return the metadata for both JavaScript and Python
    return metadata_js, metadata_python

def generate_metadata_and_folder(question: str, user_data: dict, export_path: str):
    """
    Generates metadata for a given question and creates a folder based on the metadata title.

    Parameters:
    question (str): The question for which metadata is to be generated.
    user_data (dict): User data to be used for metadata generation.
    export_path (str): The path where the new folder should be created.

    Returns:
    tuple: A tuple containing the path of the created folder and the generated metadata, or (None, None) in case of an error.
    """
    try:
        # Generate metadata for the question using provided user data
        metaData,usage = generate_metadata(question, user_data)
        # Uncomment the line below to print the generated metadata
        print("Metadata Generated:", metaData)

        # Extract the folder title from the metadata
        # The structure of metaData is checked to ensure correct extraction
        folder_title = metaData[0]["title"] if isinstance(metaData, list) else metaData["title"]
        #print(folder_title)
        # Create a folder with the extracted title in the specified export path
        created_folder_path = create_folder(folder_title, target_path=export_path)
        print(created_folder_path)

        # Return the path of the created folder and the generated metadata
        return created_folder_path, metaData
    except Exception as e:
        # Print the error message and return None for both folder path and metadata
        print(f"Error during metadata/folder generation: {e}")
        return None, None
    
def generate_adaptive_code(question:str, solution_guide, user_data, metaData):
    """Generates adaptive code based on the question and user preferences."""
    try:
        is_adaptive = metaData[0].get("isAdaptive", "").lower() if isinstance(metaData, tuple) else metaData.get("isAdaptive", "").lower()
        codelang = user_data.get("codePreference")
        return generate_code(question, is_adaptive, codelang, solution_guide)
    except Exception as e:
        print(f"Error during code generation: {e}")
        return None
    
def export_files_to_folder(created_folder, files):
    """Exports a set of files to the specified folder."""
    for file_name, file_content in files.items():
        if file_content:
            asyncio.run(export_files(file_name, file_content, created_folder,api_key=api_key,model_name="gpt-4"))

def process_question(question, solution_guide, user_data):
    export_path = r"question_output"
    created_folder, metaData = generate_metadata_and_folder(question, user_data,export_path=export_path)
    if not created_folder:
        return False

    files_tuple = generate_adaptive_code(question, solution_guide, user_data, metaData)
    #print(files_tuple)

    # Map tuple elements to filenames, skipping None values
    file_names = ["question.html", "server.py", "server.js", "solution.html"]
    files_dict = {name: content for name, content in zip(file_names, files_tuple) if content is not None}
    #print("\n Files dict\n ",files_dict)
    export_files_to_folder(created_folder, files_dict)
    
    if isinstance(metaData, tuple):
        # Handle the case where metaData is a tuple
        for index, data in enumerate(metaData, start=1):
            export_data = {key: value for key, value in data.items() if key != "question"}
            file_name = f"info_{index}.json"
            asyncio.run(export_files(file_name, export_data, created_folder))
    else:
        # Handle the case where metaData is a single dictionary
        export_data = {key: value for key, value in metaData.items() if key != "question"}
        asyncio.run(export_files("info.json", export_data, created_folder,api_key=api_key,model_name=model))

    return True

def main():
    """Main function orchestrating the question processing and handling variations."""
    # Step 1: Gather User Data and Extract Question
    user_data = collect_user_preferences()
    # Extract question based on wether image or text based question
    extracted_data = extract_question_based_on_type(user_data, api_key)

    if not extracted_data:
        print("Failed to extract question or solution.\n")
        return

    question, solution_guide = extracted_data if isinstance(extracted_data, tuple) else (extracted_data, None)

    # Step 2: Prepare a List for Questions and Variations
    questions_to_process = [(question, solution_guide)]
    #print(questions_to_process)

    # Step 3: Check for Question Variations
    generate_variations_input = prompt_generate_question_variations()
    if generate_variations_input:
        print("User chose to generate question variations.")
        variation_generator = GenerateVariation(api_key)
        
        
        question_variations = variation_generator.generate_question_variation(question[0])

        for data in question_variations:
            question_variation = data.get("question_variation")
            new_unknown = data.get("new_unknown")
            new_solution = create_variation_solution(question, solution_guide, question_variation, new_unknown, api_key) if solution_guide else None
            questions_to_process.append((question_variation, new_solution))
            
    # Step 4: Display All Questions and Solutions
    for idx, (q, sol) in enumerate(questions_to_process, start=1):
        print(f"Question {idx}: {q}")
        # if sol:
        #     print(f"Solution Guide for Question {idx}: {sol}\n")

    # Step 5: Ask User to Review and Remove Questions
    remove_indices = input("""Before generation begins please review the questions. If there is any question you want removed  
                           Enter the number of the question you want to remove (comma-separated), or press Enter to continue: """)
    
    if remove_indices:
        indices_to_remove = [int(idx) - 1 for idx in remove_indices.split(",") if idx.isdigit()]
        questions_to_process = [q for idx, q in enumerate(questions_to_process) if idx not in indices_to_remove]

    # Step 6: Process Each Question
    for q, sol in questions_to_process:
        if not process_question(q, sol, user_data):
            print(f"Failed to process question: {q}")

if __name__ == "__main__":
    main()
