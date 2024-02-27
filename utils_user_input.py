import os
import re
from util_validation import validate_image_path, validate_email
from util_image_extraction import extract_question,extract_solution

            
            
def getCreatedBy_userinput():
    """
    Continuously prompts the user to enter an email until a valid format is provided.
    
    Returns:
        dict: A dictionary with the key 'createdBy' and the valid email as its value.
    """
    while True:
        email = input("Please Enter Email: ")
        if validate_email(email):
            return {"createdBy": email}
        else:
            print("Invalid email format. Please try again.")

def getCodeGenerationPreference():
    """
    Asks the user to specify their code generation preference among JavaScript, Python, both, or none.
    
    Returns:
        dict: A dictionary with the key 'codePreference' and the user's choice as its value.
    """
    while True:
        code_choice = input("Do you want to generate code in JavaScript, Python, both, or none? Enter 'JavaScript', 'Python', 'both', or 'none': ").strip().lower()
        if code_choice in ['javascript', 'python', 'both', 'none']:
            return {"codePreference": code_choice}
        else:
            print("Invalid choice. Please enter 'JavaScript', 'Python', 'both', or 'none'.")
            
def get_input_question_type_choice():
    """
    Prompts the user to choose whether to input a question directly or provide an image path, then captures the input accordingly.

    Returns:
        dict: A dictionary with keys 'type' and 'data' containing the type of input ('str' or 'image') and the actual input data or error message.
    """
    choice = input("Do you want to input a question directly or provide an image path? Enter 'question' or 'image': ").strip().lower()

    if choice == 'question':
        question = input("Enter your question: ")
        return {"type": "str", "data": question}
    elif choice == 'image':
        image_path = input("Enter the path to your image: ")

        try:
            process_result = validate_image_path(image_path)
            return {"type": "image", "data": process_result}
        except FileNotFoundError as e:
            return {"type": "error", "data": str(e)}
        except Exception as e:
            return {"type": "error", "data": f"An error occurred while processing the image: {e}"}
    else:
        return {"type": "error", "data": "Invalid choice. Please enter 'question' or 'image'."}
    
    
def collect_user_preferences() -> dict:
    """
    Collects various pieces of data from the user, including their input type preference 
    (text or image), email address, and code generation preference.

    The function gathers this information by calling other functions that prompt the user for:
    - The type of input they will provide for a question.
    - Their email address for identification purposes.
    - Their preference for code generation language.

    Returns:
        dict: A dictionary containing the user's input type choice, email, and code generation preference.
    """
    # Gather the user's input type choice (text or image)
    user_input = get_input_question_type_choice()
    
    # Gather the user's email
    user_email = getCreatedBy_userinput()
    
    # Gather the user's code generation preference
    user_code_preference = getCodeGenerationPreference()
    
    # Combine all gathered data into a single dictionary and return it
    return {**user_input, **user_email, **user_code_preference}


def extract_question_based_on_type(user_data: dict, api_key: str):
    """
    Extracts a question based on the user-provided data type (text or image).

    Args:
        user_data (dict): A dictionary containing 'type' and 'data' keys, where 'type' specifies the data type
                          ('str' for text or 'image' for image) and 'data' contains the input data.
        api_key (str): An API key required for extracting questions and solutions from images.

    Returns:
        str or tuple: If the data type is 'str', returns the extracted text question as a string.
                      If the data type is 'image', returns a tuple containing the extracted image question and solution as strings.
                      If an error occurs during extraction, returns None and prints an error message.
    """
    data_type = user_data.get("type")
    data_content = user_data.get("data")

    if data_type == "str":
        text_question = data_content
        return text_question
    elif data_type == "image":
        try:
            image_question = extract_question(image_path=data_content, api_key=api_key)
            image_solution = extract_solution(image_path=data_content, api_key=api_key)
            return image_question, image_solution
        except Exception as e:
            print(f"Error extracting question from image: {e}")
            return None
    else:
        print("Error: Invalid data type. Expected 'str' or 'image'.")
        return None

def prompt_generate_question_variations():
    """
    Prompts the user if they would like to generate question variations.

    Returns:
        bool: True if the user chooses to generate variations, False otherwise.
    """
    print("Generating question variations is an experimental feature and may not be suitable for all questions.\n")
    while True:
        choice = input("Do you want to generate question variations? (yes/no): ").strip().lower()
        if choice == "yes":
            return True
        elif choice == "no":
            return False
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")    
    


def gather_user_information():
    """
    Gathers information from the user through a series of interactive prompts, excluding email and code preferences.
    """
    valid_responses = {"text", "image"}
    valid_yes_no = {"yes", "no"}

    # Determine if the question is text or image
    question_type = ""
    while question_type not in valid_responses:
        question_type = input("Are you uploading a question as text or as an image? (Enter 'text' or 'image'): ").strip().lower()
        if question_type not in valid_responses:
            print("Invalid response. Please enter 'text' or 'image'.")
    
    # Collect the question text or image path based on the question type
    question_text, question_image_paths = "", []
    if question_type == "text":
        question_text = input("Please input your question: ")
    elif question_type == "image":
        # Ask for multiple paths, separated by commas
        input_paths = input("Please submit paths to the images, separated by commas (or press enter to skip): ").strip()
        if input_paths:  # Check if anything was input
            # Split the input string into a list by commas
            paths_list = input_paths.split(',')
            # Iterate over the list to validate and store each path
            for path in paths_list:
                path = path.strip()  # Remove any leading/trailing whitespace
                try:
                    validate_image_path(path)
                    # If the path is valid, append it as a list to question_image_paths
                    question_image_paths.append([path])
                except Exception as e:
                    print(f"Invalid image path: {e}. Skipping image upload.")
    # Flattening the list of lists after all paths have been collected and validated
    flattened_image_paths = [item for sublist in question_image_paths for item in sublist]
    # Optional external image upload
    external_image = input("If you are uploading any external images, please enter the path location (or press enter to skip): ").strip()
    if external_image:  # Validate path if provided
        try:
            validate_image_path(external_image)
        except Exception as e:
            print(f"Invalid external image path: {e}. Skipping external image upload.")
            external_image = ""  # Clear path on failure

    # Inquiry about question variations
    question_variations = ""
    while question_variations not in valid_yes_no:
        question_variations = input("Are you interested in generating question variations? (Enter 'yes' or 'no'): ").strip().lower()
        if question_variations not in valid_yes_no:
            print("Invalid response. Please enter 'yes' or 'no'.")

    user_info = {
        "QuestionType": question_type,
        "QuestionText": question_text if question_type == "text" else "",
        "QuestionImagePath": flattened_image_paths if question_type == "image" else "",
        "ExternalImage": external_image,
        "QuestionVariations": question_variations,
    }

    return user_info



def extract_question_image_or_text(user_info:dict,api_key:str):
    question_image_path = user_info.get("QuestionImagePath")
    question_str = user_info.get("QuestionText")
    #print(question_image_path)
    if question_str != "":
        return question_str
    elif question_image_path != "":
        try:
            image_question = extract_question(image_path=question_image_path, api_key=api_key)
            image_solution = extract_solution(image_path=question_image_path, api_key=api_key)
            return image_question, image_solution
        except Exception as e:
            print(f"Error extracting question from image: {e}")
            return None
    else:
        print("Error: Invalid data type. Expected 'str' or 'image'.")
        return None
        
        