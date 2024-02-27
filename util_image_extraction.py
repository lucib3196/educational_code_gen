import base64
import requests
import sys

from util_string_extraction import extract_content_from_triple_quote
    
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_image_and_send_request(text, image_paths, api_key, max_tokens=1000):
    """
    Encodes images, sends a request to an API, and extracts content from the response.

    Parameters:
    text (str): The text to be included in the payload.
    image_paths (list of str): The paths to the images to be encoded.
    api_key (str): The API key for authorization.

    Returns:
    str: Extracted content from the API response.
    """
    print(image_paths)
    # Encode each image and prepare the image content part of the payload
    image_contents = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_path)}", "detail": "high"}} for image_path in image_paths]

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
                    {"type": "text", "text": text},
                    *image_contents  # Unpacking the list of image contents into the payload
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
    extracted_question =encode_image_and_send_request(text=extract_question_prompt, image_paths=image_path, api_key=api_key, max_tokens=max_tokens)
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
    extracted_solution = encode_image_and_send_request(text=extract_solution_prompt, image_paths=image_path, api_key=api_key, max_tokens=max_tokens)
    return extracted_solution


# if __name__ == '__main__':
#     test_path = [[r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\quetion_output\medley1\medley_1.png"],[r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\quetion_output\medley1\medley_1_solution.png"]]
    
#     # Flatten the list of image paths
#     flattened_image_paths = [item for sublist in test_path for item in sublist]
    
#     api_key = "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"

#     solution = extract_solution(flattened_image_paths, api_key)
#     print("Solution:", solution)

#     question = extract_question(flattened_image_paths, api_key)
#     print("Question:", question)