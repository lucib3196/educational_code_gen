from utils_user_input import gather_user_information, extract_question_image_or_text
from util_metadata_generator import QuestionMetaDataGenerator
from util_generate_variations import GenerateVariation
from util_generation_misc import create_variation_solution
from util_code_generation import generate_code
from util_javascript_generator import js_generator
from util_validation import validate_question_html_format
from util_string_extraction import extract_javascript_generate_code
from util_file_export import create_folder,export_files
import asyncio

api_key = "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"
csv_path = r"Question_Embedding_20240128.csv"

def display_questions(questions_to_process):
    """
    Displays all questions and solutions in the provided list.

    Parameters:
    questions_to_process (list): A list of tuples containing questions and solutions.
    """
    for idx, (q, sol) in enumerate(questions_to_process, start=1):
        print(f"Question {idx}: {q}")
        # Add solution guide display if needed
        # if sol:
        #     print(f"Solution Guide for Question {idx}: {sol}\n")
def remove_questions(questions_to_process):
    """
    Asks the user to review and remove questions from the provided list.

    Parameters:
    questions_to_process (list): A list of tuples containing questions and solutions.
    """
    remove_indices = input("""Before generation begins please review the questions. If there is any question you want removed  
                           Enter the number of the question you want to remove (comma-separated), or press Enter to continue: """)
    
    if remove_indices:
        indices_to_remove = [int(idx) - 1 for idx in remove_indices.split(",") if idx.isdigit()]
        questions_to_process = [q for idx, q in enumerate(questions_to_process) if idx not in indices_to_remove]

def generate_metadata(question, code_preference, created_by):
    """
    Generates metadata for a given question based on user's code language preference.

    Parameters:
    question (str): The question for which metadata is to be generated.
    code_preference (str): The user's code language preference.
    created_by (str): The creator information.

    Returns:
    Depending on the code language preference, it returns either metadata for one language,
    or a tuple of metadata for both JavaScript and Python.
    """
    # Initialize the metadata generator and classifier
    metadata_generator = QuestionMetaDataGenerator(api_key)
    classifier = QuestionMetaDataGenerator(api_key)

    # If the user prefers a specific language (not both), generate metadata for that language
    if code_preference != "both":
        return classifier.extract(question=question, createdBy=created_by, codelang=code_preference)

    # If the user prefers both languages, generate metadata for JavaScript
    metadata_js, usage = classifier.extract(question=question, createdBy=created_by, codelang="javascript")
    
    # Create a copy of the JavaScript metadata for Python
    metadata_python = metadata_js.copy()
    metadata_python["codelang"] = "python"

    # Return the metadata for both JavaScript and Python
    return metadata_js, metadata_python

def generate_metadata_and_folder(question: str, code_preference: str,created_by: str, export_path: str):
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
        metaData = generate_metadata(question, code_preference, created_by)
        # Uncomment the line below to print the generated metadata
        print("Metadata Generated:", metaData)

        # Extract the folder title from the metadata
        # The structure of metaData is checked to ensure correct extraction
        folder_title = metaData[0]["title"] if isinstance(metaData, tuple) else metaData["title"]

        # Create a folder with the extracted title in the specified export path
        created_folder_path = create_folder(folder_title, target_path=export_path)
        print(created_folder_path)

        # Return the path of the created folder and the generated metadata
        return created_folder_path, metaData

    except Exception as e:
        print("Error:", e)
        # Return None in case of an error
        return None, None
    
def export_files_to_folder(created_folder, files):
    """Exports a set of files to the specified folder."""
    for file_name, file_content in files.items():
        if file_content:
            asyncio.run(export_files(file_name, file_content, created_folder,api_key=api_key,model_name="gpt-4"))
            
def process_question(question, solution_guide,code_preference,created_by,export_path):
    created_folder, metaData = generate_metadata_and_folder(question,code_preference,created_by,export_path)
    if isinstance(metaData,tuple):
        is_adaptive = metaData[0].get("isAdaptive")
    if not created_folder:
        return False
    if isinstance(code_preference,list):
        code_preference = code_preference[0]
        
    print(code_preference)
    files_tuple = generate_code(input_question=question,is_adaptive_str=is_adaptive,codelang=code_preference,csv_path=csv_path,api_key=api_key,solution_guide=solution_guide)
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
            asyncio.run(export_files(file_name, export_data, created_folder,api_key=api_key,model_name="gpt-4"))
    else:
        # Handle the case where metaData is a single dictionary
        export_data = {key: value for key, value in metaData.items() if key != "question"}
        asyncio.run(export_files("info.json", export_data, created_folder,api_key=api_key,model_name="gpt-4"))

    return True
def main():
    # Initialize classes
    variation_generator = GenerateVariation(api_key)

    # Gather user data through interactive prompts.
    user_data = gather_user_information()
    created_by = user_data.get("Email")
    code_preference = user_data.get("CodePreference")
    generate_variations_response = user_data.get("QuestionVariations")

    # Extract question data
    question_data = extract_question_image_or_text(user_data, api_key=api_key)
    question, solution_guide = question_data if isinstance(question_data, tuple) else (question_data, None)
    print("Question Data Extracted Successfully")

    # Generate variations if requested
    questions_to_process = [(question, solution_guide)]
    if generate_variations_response.lower() == "yes":
        question_variations = variation_generator.generate_question_variation(question if isinstance(question, str) else question[0])
        for data in question_variations:
            question_variation = data.get("question_variation")
            new_unknown = data.get("new_unknown")
            new_solution = create_variation_solution(question, solution_guide, question_variation, new_unknown, api_key) if solution_guide else None
            questions_to_process.append((question_variation, new_solution))

    # Display all questions and solutions
    display_questions(questions_to_process)
    # Ask user to review and remove questions
    remove_questions(questions_to_process)
    export_path = r"question_output"

    for question,solutions in questions_to_process:
         if not process_question(question,solutions,code_preference=code_preference,created_by=created_by,export_path=export_path):
            print(f"Failed to process question: {question}")



if __name__ == "__main__":
    main()
