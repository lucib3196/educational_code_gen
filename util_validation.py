import re
import os

def validate_image_path(image_path:str):
    """Process image path, if successful prints out message

    Args:
        image_path (str): path to image

    Raises:
        FileNotFoundError: Returns error message, indicating if image is found

    Returns:
        str: image_path if succesful
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No file found at {image_path}")
    else: print("Image processed successfully")
    return image_path

def validate_email(email:str)->bool:
    """_summary_

    Args:
        email (str): _description_

    Returns:
        bool: True if the email is valid according to the pattern, False otherwise.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    return re.match(pattern=pattern,string = email) is not None


def validate_question_html_format(html_string:str):
    """
    Validates if the provided HTML string contains specific required patterns.
    
    This function checks if the HTML content for a question adheres to a required format by searching for specific patterns. 
    It ensures that the string contains '{{params.<somevalue>}}' patterns and '<pl' tags, which are indicative of valid PrairieLearn HTML elements.
    
    Parameters:
    data_str (str): A string containing the HTML data to validate.
    
    Returns:
    str: The original `data_str` if it passes all the format validations.
    
    Raises:
    ValueError: If `data_str` does not contain the required patterns.
    """
    # Define a dictionary of patterns and their corresponding error messages
    patterns = {
        r'\{\{params\..+?\}\}': "Invalid format: Missing '{{params.<somevalue>}}' pattern.",
        '<pl': "Invalid format: Missing '<pl' tag indicative of PrairieLearn HTML element."
    }

    # Iterate through the patterns and check each one
    for pattern, error_message in patterns.items():
        if not re.search(pattern, html_string):
            raise ValueError(error_message)
    return html_string