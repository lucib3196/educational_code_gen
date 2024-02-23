from openai import OpenAI
import json

def parse_json_from_markdown(content):
    # Check for and remove Markdown code block syntax
    if content.startswith("```json") and content.endswith("```"):
        # Remove the first line (```json) and the last three characters (```)
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        # Convert the JSON string into a dictionary
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("Invalid JSON format:", e)
        return None
    

class QuestionMetaDataGenerator:
    """
    A class to generate and process question metadata using OpenAI's GPT model.

    Attributes:
        system_template (str): A preset template message for the system role.
        user_template (str): A preset template message for the user role, detailing the expected metadata fields.
        client (OpenAI): An instance of the OpenAI client for API interaction.

    Methods:
        __init__(self): Initializes the QuestionMetaDataGenerator class with default templates and OpenAI client.
        
        generate_question_metadata(self, question: str) -> Tuple[str, str, int]:
            Generates metadata for a given question using a structured conversational approach with the OpenAI API.
            Args:
                question (str): The input question for which metadata is to be generated.
            Returns:
                Tuple containing the generated metadata (str), the model used (str), and the total number of tokens consumed (int).

        extract(self, question: str, createdBy: str, codelang: str) -> Tuple[dict, dict]:
            Extracts and structures the question metadata along with additional information like creator, code language, etc.
            Args:
                question (str): The input question for which metadata is to be structured.
                createdBy (str): Identifier for the creator of the question.
                codelang (str): The programming language associated with the question.
            Returns:
                Tuple containing the structured metadata dictionary and usage information dictionary.
            Raises:
                ValueError: If non-empty metadata generation fails after specified retries.
                json.JSONDecodeError: If JSON parsing fails after specified retries.
                Exception: For any other unexpected errors.
    """

    def __init__(self,api_key:str):
        self.system_template = "You are a helpful assistant designed to output JSON."
        self.user_template = """
        Given the following input question
        Generate the following
        - uuid: A universally unique identifier (UUID) for this item
        - title: The title or name of the educational content
        - stem: Additional context or a subtopic related to the main topic
        - topic: The main topic or subject of the educational content
        - tags: An array of keywords or tags associated with the content for categorization
        - prereqs: Prerequisites needed to access or understand the content
        - isAdaptive: Designates whether the content necessitates any form of numerical computation. Assign as 'true' if the question involves any numerical computation; return 'false' if no computational effort is required. Note: This is a string value, not a boolean.
        """.strip()
        self.client = OpenAI(api_key=api_key)

    def generate_question_metadata(self, question):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            temperature=0,
            messages=[
                {"role": "system", "content": self.system_template},
                {"role": "user", "content": self.user_template + str(question)}
            ],
            stop=None 
        )
        metadata = response.choices[0].message.content
        model =  response.model
        total_tokens = response.usage.total_tokens
        return metadata, model,total_tokens
    
    def extract(self, question:str, createdBy:str, codelang:str):
        total_tokens = 0
        retries = 3
        attempt = 0
        while attempt < retries:
            try:
                content, model, tokens = self.generate_question_metadata(question)
                total_tokens += tokens  # Increment the token count for each attempt

                # Check if metadata is not empty
                if content.strip():  # This checks if the content is not just whitespace
                    metadata_dict = parse_json_from_markdown(content)
                    #metadata_dict = json.loads(content)
                    metadata_structure = {
                        **metadata_dict,
                        "createdBy": createdBy,
                        "qType": "num",
                        "nSteps": 1,
                        "updatedBy": "",
                        "dificulty": 1,
                        "codelang": codelang
                    }
                    usage_info = {
                        "model": model,
                        "totalTokens": total_tokens
                    }
                    return metadata_structure, usage_info
                else:
                    print("Metadata is empty, retrying...")
                    attempt += 1

            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1} failed to parse JSON: {str(e)}")
                attempt += 1
                if attempt >= retries:
                    raise e  # Re-raise exception if all retries fail

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                attempt += 1
                if attempt >= retries:
                    raise e  # Re-raise unexpected exceptions

        # If retries are exhausted and metadata is still empty
        raise ValueError("Failed to generate non-empty metadata after retries.")

def question_metadata_generator(api_key, question, created_by, code_lang):
    """
    Test function to generate metadata for a question.

    Parameters:
    api_key (str): API key for the service.
    question (str): The question to process.
    created_by (str): The identifier for who created the question.
    code_lang (str): The code language associated with the question.
    """
    classifier = QuestionMetaDataGenerator(api_key=api_key)
    metadata,usage = classifier.extract(question, created_by, code_lang)
    return metadata

# # Example usage
# api_key = "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"  # Replace with your actual API key
# test_question = "What is the capital city of France?Options:A) London B) Berlin C) Paris D) Madrid"
# created_by = "user123"  # Replace with the actual creator identifier
# code_lang = "javascript"  # Replace with the actual code language

# print(question_metadata_generator(api_key, test_question, created_by, code_lang))