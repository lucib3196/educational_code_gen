import base64
import requests
import sys

from util_string_extraction import extract_content_from_triple_quote
    
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_image_and_send_request(text, image_path,api_key,max_tokens = 1000):
    """
    Encodes an image, sends a request to an API, and extracts content from the response.

    Parameters:
    text (str): The text to be included in the payload.
    image_path (str): The path to the image to be encoded.
    api_key (str): The API key for authorization.

    Returns:
    str: Extracted content from the API response.
    """

    # Encoding the image
    base64_image = encode_image(image_path)

    # Setting headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    #Setting headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Creating the payload
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "temperature": 0,
        "max_tokens": max_tokens
    }
    # Sending the request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Parsing the JSON response
    data = response.json()

    # Extracting the content
    if 'choices' in data and data['choices']:
        content = data['choices'][0]['message']['content']

        try:
            extracted_content = extract_content_from_triple_quote(content)
            if not extracted_content:  # Check if extracted content is empty
                raise Exception("Extracted content is empty.")
            return extracted_content
        except Exception as e:
            raise Exception(f"An error has occurred in extraction: {e}")
    else:
        raise Exception("No choices found in data.")



def extract_question(image_path,api_key,max_tokens = 1000):
    extract_question_prompt = 'Extract the complete problem statement from the image, ensuring it includes all details, data, and parameters necessary for solving the problem comprehensively, delimited by triple quotes """insert text here""" ' 
    extracted_question = encode_image_and_send_request(text = extract_question_prompt, image_path = image_path,api_key = api_key,max_tokens = max_tokens)
    return extracted_question

def extract_solution(image_path,api_key,max_tokens = 1000):
    extract_solution_prompt = """
    
    Objective:
    Analyze the following image and extract and Develop a generalized guide to outline the methodical steps for solving the  problem depicted in the provided image. Your guide should focus on extracting and explaining the core principles and equations involved in the problem.

    Solution Guide Format:

    Problem Statement:

    Define the problem's objective as depicted in the image, clearly outlining its context and goal.
    Known Variables Description:

    Describe all discernible variables from the image. Include any relevant mathematical expressions or equations, represented in LaTeX.
    Equation Setup:

    Identify and establish equations or relationships shown or implied in the image, using LaTeX for mathematical representations.
    Solution Process:

    Detail each step of the solution process as inferred from the image, representing all mathematical workings and potential solutions using LaTeX.
    Explanation and Clarification:

    Provide thorough explanations and clarifications based on the image's content, using LaTeX for mathematical justifications.
    Educational Goal:

    Structure the guide to assist in understanding the problem-solving process as depicted, emphasizing a deep comprehension of the principles and methods involved.
    delimited by triple quotes '''Insert text here''' 
    """
    extracted_solution = encode_image_and_send_request(text = extract_solution_prompt, image_path = image_path,api_key = api_key,max_tokens = max_tokens)
    return extracted_solution


# if __name__ == '__main__':
#     test_path = r"test_images\textbook_example.png"
#     api_key = "insert_api_key"

#     solution = extract_solution(test_path, api_key)
#     print("Solution:", solution)

#     question = extract_question(test_path, api_key)
#     print("Question:", question)