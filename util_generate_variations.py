import json
from pydantic import BaseModel, Field, validator,root_validator
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

class QuestionKnownsUnknownsExtractor(BaseModel):
    # The original question from which the information is extracted.
    question: str = Field(description = "This is the original input question")
    # Represents the primary variable or subject the question aims to determine.
    unknown: str = Field(description = "This field represents the primary subject or variable that the question aims to determine. It's what the question is fundamentally asking about. For example, in the question 'What is the speed of the car?', the unknown would be 'speed'.")
    # Lists the provided data or conditions within the question used to derive the unknown.
    knowns: List[str] = Field( description="This field lists all the provided data or preconditions within the question. These are the facts or values available to derive the unknown. Each known can be directly or indirectly used to determine the unknown. For instance, in the question 'A car travels a distance of 120 km in 2 hours. What is its speed?', the knowns would be 'distance' and 'time', and they can be used to solve for the unknown 'speed'")
    # Validator to ensure that a known is not the same as the unknown.    
    @validator('knowns', pre=True, each_item=True)
    def check_knowns(cls, known):
        assert known != cls.unknown, f"{known} cannot be both a known and the unknown."
        return known

    # Validator to ensure that the list of knowns is not empty.
    @validator('knowns')
    def ensure_non_empty_list(cls, knowns):
        assert len(knowns) > 0, "The list of knowns should not be empty."
        return knowns
    
    # Validator to ensure that there are no duplicate values in the knowns list.
    @validator('knowns')
    def ensure_unique_values(cls, knowns):
        assert len(knowns) == len(set(knowns)), "Duplicate values detected in knowns."
        return knowns
    
# Class to extract the knowns and unknown from a given question using the LLM.
class QuestionExtractor:
    """
    Class to extract knowns and unknowns from a given question using the LLM.
    """

    def __init__(self, api_key=None, llm_options=None):
        """
        Initializes the extractor with customizable LLM options and API key.

        Parameters:
        api_key (str): The API key for the ChatOpenAI service. Defaults to environment variable.
        llm_options (dict): Options for configuring the LLM. Defaults to specified model and temperature.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.LLM_OPTIONS = llm_options or {
            "model": "gpt-4-0125-preview",
            "temperature": "0"
        }

        # Initialize Pydantic parser and LLM
        self.pydantic_parser = PydanticOutputParser(pydantic_object=QuestionKnownsUnknownsExtractor)
        self.template_string = self._construct_template()
        self.llm = ChatOpenAI(
            model=self.LLM_OPTIONS["model"],
            temperature=self.LLM_OPTIONS["temperature"],
            api_key=self.api_key)
        
    def _construct_template(self):
        """
        Constructs the template string for formatting the question.

        Returns:
        str: The template string.
        """
        return (
            "Given the following input question, identify and list the names of both the known quantities and the unknown. "
            "\n"
            "Example 1 (Kinematics):\n"
            "Input Question: 'A car travels a distance of 120 km in 2 hours. Find its average speed.'\n"
            "Unknown: Average Speed\n"
            "Knowns: Distance, Time\n"
            "\n"
            "Example 2 (Fluids):\n"
            "Input Question: 'A cylindrical tank with a diameter of 1.5 meters is filled with water to a height of 3 meters. "
            "Calculate the volume of water in the tank.'\n"
            "Unknown: Volume\n"
            "Knowns: Diameter, Height\n"
            "\n"
            "Example 3 (Chemistry):\n"
            "Input Question: '2 moles of hydrogen gas react with 1 mole of oxygen gas to produce water. "
            "Determine the number of moles of water produced.'\n"
            "Unknown: Moles of Water\n"
            "Knowns: Moles of Hydrogen, Moles of Oxygen\n"
            "\n"
            "{question}.\n"
            "{format_instructions}"
        )
        
        
    def extract(self, question):
        """
        Extracts the knowns and unknown from the provided question.

        Parameters:
        question (str): The question to process.

        Returns:
        dict: Extracted knowns and unknown or None in case of an error.
        """
        format_instructions = self.pydantic_parser.get_format_instructions()
        prompt = ChatPromptTemplate.from_template(template=self.template_string)
        messages = prompt.format_messages(question=question, format_instructions=format_instructions)

        try:
            output = self.llm.invoke(messages)
            return self._process_output(output.content)
        except Exception as e:
            print(f"Error in LLM invocation: {e}")
            return None

    def _process_output(self, content):
        """
        Processes the LLM's output to extract required information.

        Parameters:
        content (str): The content returned by the LLM.

        Returns:
        dict: The processed output containing knowns, unknown, and the question.
        """
        # Remove the markdown code block syntax (```json and ```)
        cleaned_content = content.replace("```json\n", "").replace("\n```", "")

        # Parse the cleaned string as JSON
        try:
            output_dict = json.loads(cleaned_content)
            return {
                "question": output_dict["question"],
                "unknown": output_dict["unknown"],
                "knowns": output_dict["knowns"]
            }
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return None

class VariationExtractor(BaseModel):
    question: str = Field(description="Original input question that you want to create variations for.")
    new_unknown: str = Field(description="The new parameter or variable that you want to be the unknown in the question variation.")
    question_variation: str = Field(description="Generated variation of the original question where the specified 'new_unknown' is now the unknown.")
    
    @root_validator(pre=False, skip_on_failure=True)
    def ensure_variation(cls, values):
        question, question_variation = values.get('question'), values.get('question_variation')
        if question == question_variation:
            raise ValueError('The variation is the same as the original question')
        return values
    
class GenerateVariation:
    def __init__(self, api_key=None, llm_options=None):
        """
        Initializes the GenerateVariation instance with customizable LLM options and API key.

        Parameters:
        api_key (str): The API key for the ChatOpenAI service. Defaults to environment variable.
        llm_options (dict): Options for configuring the LLM. Defaults to specified model and temperature.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.LLM_OPTIONS = llm_options or {
            "model": "gpt-4",
            "temperature": "0"
        }

        self.pydantic_parser = PydanticOutputParser(pydantic_object=VariationExtractor)
        self.template_string = (
        """
      
        In this task, you are required to modify a given question to create a new variation. The goal is to change one specific parameter in the original question, making it the new unknown, while adhering to the following criteria:

        1. **Replace Previous Unknown**: If the original question contains an unknown (e.g., a value to be calculated), replace it with a specific, reasonable value in the variation. This ensures that the new variation only has one unknown element.

        2. **Logical Consistency**: The new variation should make logical sense within the context of the original question. It must be a plausible scenario based on the given details.

        3. **Retention of Information**: Retain all essential information from the original question in the variation, except for the parameter that becomes the new unknown.

        4. **Solvability**: The new variation must be solvable with the provided information. Ensure there is only one unknown, and it is clearly defined and supported by details from the original question.

        Examples:

        Example 1 (Math):
        - Input Question: 'A rectangle has a length of 10 units and a width of 5 units. Calculate the area of the rectangle.'
        - New Unknown: Width
        - Generated Variation: 'A rectangle has a length of 10 units and an area of 50 square units. Determine the width of the rectangle.'

        Example 2 (Force):
        - Input Question: 'A circular piston exerts a pressure of 80kPa on a fluid, when the force applied to the piston is 0.2kN. Find the diameter of the piston.'
        - New Unknown: Pressure
        - Generated Variation: 'A circular piston with a diameter of 0.1m has a force of 0.2kN applied to it. Determine the pressure it exerts on the fluid.'

        Example 3 (Chemistry):
        - Input Question: 'When 2 moles of oxygen react with 4 moles of hydrogen, 2 moles of water are produced. If 3 moles of oxygen are available, how many moles of water will be produced?'
        - New Unknown: Hydrogen
        - Generated Variation: 'When oxygen reacts with an unknown amount of hydrogen, 2 moles of water are produced. If you start with 2 moles of oxygen, determine the amount of hydrogen needed.'
        Input Question: {question}.\n
        New Unknown: {unknown}\n
        {format_instructions}"""
        )
        self.llm = ChatOpenAI(
            model=self.LLM_OPTIONS["model"],
            temperature=self.LLM_OPTIONS["temperature"],
            api_key=self.api_key)
        self.Extractor = QuestionExtractor(api_key=self.api_key)

    def _generate_variation(self, question, new_unknown, format_instructions):
        """Generate a single question variation given a new unknown"""
        prompt = ChatPromptTemplate.from_template(template=self.template_string)
        messages = prompt.format_messages(question=question, unknown=new_unknown, format_instructions=format_instructions)
        output = self.llm(messages)

        # Remove '```json' and leading/trailing whitespace
        content = output.content.replace('```json', '').replace('```', '').strip()
        #print(content)
        
        return json.loads(content)

    def generate_question_variation(self, question):
        """Generates multiple question variations by altering the unknowns"""
        format_instructions = self.pydantic_parser.get_format_instructions()
        question_data = self.Extractor.extract(question)
        print("Question data",question_data)
        variations = [
            self._generate_variation(question, known, format_instructions) 
            for known in question_data["knowns"]
        ]
        return variations
        
    
    
# # Example test function
# def test_generate_variation(api_key, question):
#     """
#     Test function to generate question variations.

#     Parameters:
#     api_key (str): API key for the ChatOpenAI service.
#     question (str): The question for which variations are to be generated.
#     """
#     generator = GenerateVariation(api_key=api_key)
#     variations = generator.generate_question_variation(question=question)
#     print(variations)

# # Example usage
# api_key = "insert-api-key"  # Replace with your actual API key
# test_question = "A piece of metal 200 mm long, 150mm wide and 10mm thick has a mass of 2700g. What is the density of the material?"
# test_generate_variation(api_key, test_question)