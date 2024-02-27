from util_metadata_generator import question_metadata_generator
from util_javascript_generator import js_generator
from util_question_html_generator import question_html_generator
from util_solution_html_generator import question_solution_guide
from util_validation import validate_question_html_format
from util_file_export import export_files, create_folder
from util_generate_variations import GenerateVariation
from utils_user_input import gather_user_information
from utils_user_input import extract_question_image_or_text
from util_generation_misc import create_variation_solution

import os

import shutil
import os

def copy_and_export_image(source_path, destination_path):
    """
    Copies an image from the source path to the destination path.
    
    Parameters:
    - source_path: The path to the image file to be copied.
    - destination_path: The target path where the image file will be copied to.
    """
    try:
        # Ensure the destination directory exists; if not, create it
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        # Copy the image to the destination path
        shutil.copy2(source_path, destination_path)
        print(f"Image successfully copied to {destination_path}")
    except Exception as e:
        print(f"Error during copying: {e}")
        
        
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
        
def update_config_with_user_input(config):
    """
    Updates the provided configuration dictionary based on user inputs
    regarding additional instructions and retrieval optimization.

    Parameters:
    - config (dict): The initial configuration dictionary.

    Returns:
    - dict: The updated configuration dictionary.
    """
    print("You can add specific instructions such as requesting multiple choice additions or any specific formatting.")
    print("Note: These are work in progress methods and may not work as intended, so please be wary.")

    # Ask for additional instructions
    additional_instructions = input("Would you like to add any specific instructions? (yes/no): ").strip().lower()
    if additional_instructions == 'yes':
        config['additional_instructions'] = input("Please enter your specific instructions: ")

    # Ask for retrieval optimization
    print("You can request optimization of the external file by incorporating internal libraries.")
    print("Note: This optimization is a work in progress method and may not work as intended, so please be wary.")
    retrieval_optimization = input("Would you like to enable retrieval optimization? (yes/no): ").strip().lower()
    config['retrieval_optimization'] = True if retrieval_optimization == 'yes' else False

    return config

def attempt_generate_html(question, api_key, csv_path, max_attempts=3,additional_instructions=None):
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
        question_html = question_html_generator(question, api_key, csv_path,additional_instructions)
        try:
            validate_question_html_format(question_html)
            return question_html
        except ValueError as e:
            print(f"Attempt {attempt + 1}: HTML format validation failed: {e}")
    raise ValueError("Maximum validation attempts reached. Validation failed.")

def process_question(question: str, config: dict, export_path: str):
    # Unpack configuration dictionary
    api_key = config['api_key']
    csv_file = config['csv_file']
    created_by = config['created_by']
    code_language = config['code_language']

    # Generate metadata and determine the path
    meta_data = question_metadata_generator(api_key, question, created_by, code_language)
    is_adaptive = meta_data.get("isAdaptive", "").lower()
    question_path = os.path.join(export_path, meta_data.get("title"))
    create_folder(meta_data.get("title"),export_path)
    
    # Exports image path 
    if config["ExternalImage"] != "":
        copy_and_export_image(config["ExternalImage"],question_path)

    # Process based on the question type
    if is_adaptive == "true":
        process_adaptive(question,meta_data, question_path,config=config)
    else:
        process_non_adaptive(question, question_path, config)
def process_adaptive(question, meta_data, question_path, config):
    # Generate content once to avoid redundancy
    generated_html = attempt_generate_html(
        question, 
        api_key=config['api_key'], 
        csv_path=config['csv_file'], 
        additional_instructions=config.get('additional_instructions')
    )
    generated_js = js_generator(
        question=generated_html, 
        api_key=config['api_key'], 
        csv_path=config['csv_file'], 
        solution_guide=config.get('solution_guide'), 
        retrieval_optimization=config.get('retrieval_optimization', False)
    )
    generated_solution = question_solution_guide(
        question, 
        api_key=config['api_key'], 
        csv_path=config['csv_file'], 
        solution_guide=config.get('solution_guide'), 
        code_guide=generated_js
    )
    print(generated_js)
    # Define content for each file type using pre-generated content
    content_generators = {
        "question.html": lambda: generated_html,
        "server.js": lambda: generated_js,
        "solution.html": lambda: generated_solution,
        "info.json": lambda: meta_data
    }

    # Export generated content for each file
    for file_name, generator in content_generators.items():
        content = generator()  # Call the generator function to get content
        export_files(file_name, content, question_path, config['api_key'],model_name=config["export_model"])

def process_non_adaptive(question, question_path,meta_data, config):
    # Generate HTML content
    generated_html = question_html_generator(
        question=question, 
        api_key=config['api_key'], 
        csv_path=config['csv_file'], 
        additional_instructions=config.get('additional_instructions')
    )
    # Export the generated HTML
    export_files("question.html", generated_html, question_path, config['api_key'],model_name=config["export_model"])
    # Export the metadata as JSON
    export_files("info.json", meta_data, question_path, config['api_key'],model_name=config["export_model"])

# Example usage
def main():
    config = {
        "api_key": "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",  # Replace with your actual API key
        "csv_file": "Question_Embedding_20240128.csv",
        "created_by": "user123",  # Replace with the actual creator identifier
        "code_language": "javascript",  # Replace with the actual code language
        "export_model": "gpt-4-turbo-preview",
        "solution_guide": None,  # Placeholder for solution guide path or content
        "additional_instructions": None,  # Placeholder for any additional instructions
        "retrieval_optimization": False,  # Placeholder for retrieval optimization flag
        "export_path": r"question_output" # Replace with where you want questions to be exported
    }
    # Initialize classes
    variation_generator = GenerateVariation(config["api_key"])
    
    user_data = gather_user_information()
    
    # Extract question data
    question_data = extract_question_image_or_text(user_data,config["api_key"])
    question, solution_guide = question_data if isinstance(question_data, tuple) else (question_data, None)
    print("Question Data Extracted Successfully")
    print(config)
    config = {**config, **user_data}
    # print(config)
        
    
    # Generate variations if requested
    generate_variations_response = config.get("QuestionVariations")
    questions_to_process = [(str(question), solution_guide)]
    if generate_variations_response.lower() == "yes":
        question_variations = variation_generator.generate_question_variation(question if isinstance(question, str) else question[0])
        for data in question_variations:
            question_variation = data.get("question_variation")
            new_unknown = data.get("new_unknown")
            new_solution = create_variation_solution(question, solution_guide, question_variation, new_unknown, config["api_key"]) if solution_guide else None
            questions_to_process.append((question_variation, new_solution))
            
    # Display all questions and solutions
    display_questions(questions_to_process)
    # Ask user to review and remove questions
    remove_questions(questions_to_process)
    
    config = update_config_with_user_input(config)
    
    # Check if there's an external image and update additional_instructions accordingly
    if config.get("ExternalImage"):
        additional_message = f"You are also tasked with embedding the following image path: {config.get('ExternalImage')}."
        # Ensure additional_instructions is initialized
        if config["additional_instructions"] is None:
            config["additional_instructions"] = additional_message
        else:
            config["additional_instructions"] += " " + additional_message

    
    # print(config)
    
    export_path = config["export_path"]
    for question,solutions in questions_to_process:
        config["solution_guide"] = solutions
        
        if not process_question(question=question,config=config,export_path=export_path):
            print(f"Failed to process question: {question}")
            
            
if __name__ == "__main__":
    main()
