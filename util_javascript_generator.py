# Standard library imports
import asyncio
import os
import re
import warnings
from pprint import pprint

# Suppress warnings
warnings.filterwarnings("ignore")

# Third-party library imports
import bs4

# langchain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import hub
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from util_question_html_generator import question_html_generator
# langchain_community imports
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
# Utility imports
from util_semantic_search import SemanticSearch
from util_example_based_prompt import ExampleBasedPromptFormatter
from langchain.retrievers.multi_query import MultiQueryRetriever

def js_generator(question:str, api_key:str, csv_path:str,retrieval_optimization:bool,solution_guide:str=None,):

    example_options = {
    "embedding_column": "question_embedding",
    "search_column": "question.html",
    "output_column": "server.js",
    "n_examples": 1}

    llm_options = {
        "llm_code_generation_model": "gpt-4-turbo-preview",
        "agent_model": "gpt-4-turbo-preview",
        "retriever_model": "gpt-3.5-turbo-0125",
        "temperature": 0,  # Assuming temperature should be an integer or float, not a string
        "embedding_model": "text-embedding-ada-002"
    }
    retriever_path = r"stable_properties"
    
    semantic_search_instance = SemanticSearch(
        csv_path=csv_path,
        embedding_column_name=example_options["embedding_column"],
        embedding_engine=llm_options["embedding_model"],
        api_key=api_key
    )
    def extract_examples(question: str) -> str:
        examples = semantic_search_instance.extract_examples(
            input_string=question,
            search_column=example_options["search_column"],
            output_column=example_options["output_column"],
            n_examples=example_options["n_examples"]
        )
        return examples
    examples = extract_examples(question)
    
     # Construct the prompt
    guide_section = (f"Utilizing the provided step-by-step guide, craft a JavaScript function that executes the computations as detailed in the guide: {solution_guide}\n" 
                     if solution_guide else 
                     "Construct a JavaScript function that derives its logic from the computational problem at hand.\n")
    base_template = f"""
        Design a robust JavaScript module adept at generating computational problems for various STEM disciplines. This module will ingest an HTML file containing a structured query and will output a JavaScript snippet that carries out the calculation for the problem described. The JavaScript code must conform to the following outline:

        const generate = () => {{
            // 1. Dynamic Parameter Selection:
            // - Thoroughly analyze the HTML or data source to identify an extensive range of categories and units for computation.
            // - Ensure the inclusion of a wide variety of units and values, covering different global measurement systems.
            // - Develop a randomized selection algorithm to fairly choose a category or unit system, ensuring equitable representation.
            // - When applicable ensure that it is between SI and USCS for unit selection

            // 2. Appropriate Transformations:
            // - Implement precise and tailored conversion processes for each unit, ensuring accuracy in the transformation.
            // - Adapt the computations to maintain integrity, taking into account the specific characteristics of each unit system.
            // - Include robust validation and error handling to manage unusual or incorrect unit inputs, preserving computation reliability.

            // 3. Value Generation:
            // Produce random values relevant to the problem's context.
            // These values are the basis for the problem's arithmetic or logical operations.

            // 4. Solution Synthesis:
            // Utilize the selected parameters and the generated values to formulate the solution.
            // The computation should honor the problem's context, limitations, and nature to guarantee its validity.

            return {{
                params: {{
                    // Input parameters relevant to the problem's context and the chosen category/unit system.
                    // Export all calculated variables
                }},
                correct_answers: {{
                    // Calculate the correct answer(s) using the selected parameters and generated values.
                }},
                nDigits: 3,  // Define the number of digits after the decimal place.
                sigfigs: 3   // Define the number of significant figures for the answer.
            }};
        }}

        module.exports = {{
            generate
        }}

        Your mission is to flesh out the 'generate' function within this framework. It should dynamically select parameters and units, apply necessary transformations, spawn values, and deduce a legitimate solution. The function must return an object containing 'params' and 'correct_answers' properties, which abide by the prescribed structure. This alignment ensures that the HTML and JavaScript components integrate seamlessly. Below is a sample illustration:
        
        ```insert code here```
        """
    # Completes prompt for code generation 
    complete = guide_section+base_template
    template = ExampleBasedPromptFormatter.run(examples,complete)
    complete_template = f"{template}\ninput: {question}"
    
    # LLM Code Generation Set Up 
    llm = ChatOpenAI(openai_api_key=api_key,model=llm_options["llm_code_generation_model"])
    generated_code = llm.invoke(complete_template)
    #print("This is the original code \n", generated_code,"\n")
    if retrieval_optimization:
        # Set Up Retriever 
        # Load documents from the filesystem with specific criteria (JS files)
        loader = GenericLoader.from_filesystem(
            path=retriever_path,
            glob="*",
            suffixes=[".js"],
            parser=LanguageParser(language=Language.JS)
        )
        docs = loader.load()
        child_js_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=300, chunk_overlap=200)
        parent_js_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=2000, chunk_overlap=200)
        # The vectorstore to use to index the child chunks
        vectorstore = Chroma(
            collection_name="split_parents", embedding_function=OpenAIEmbeddings()
        )
        # The storage layer for the parent documents
        store = InMemoryStore()
        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=child_js_splitter,
            parent_splitter=parent_js_splitter,)
        
        retriever.add_documents(docs)
        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 10})
        template = """As a developer with access to our extensive code database, your goal is to effectively find and utilize information for the tasks at hand. This concise guide outlines a streamlined approach to optimize your workflow:
        1. Understanding the Query: Grasp the essence of the provided question or task.
        2. Accessing the Code Database: Conduct a targeted search within the database.
        3. Evaluating the Results: Assess the relevance and utility of each potential match.
        4. Handling Unknown Answers: Acknowledge the absence of direct answers without speculation.
        You will return any information about the code base
        {context}


        Answer:"""
        
        # Intiailize Agent 
        retriever_tool = create_retriever_tool(
        retriever,
        "Database_Retriever",
        template,
        )
        tools = [retriever_tool]
        message_history = ChatMessageHistory()
        agent_llm = ChatOpenAI(model=llm_options["agent_model"], temperature=0,)
        prompt = hub.pull("hwchase17/openai-functions-agent")
        agent = create_openai_functions_agent(agent_llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,)
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: message_history,
            input_message_key = "input",
            history_messages_key="chat_history"
        )
        # Define the search query question
        text_step1 = f"""
        Step 1: Database Query Integration:
            - Utilize the Database_Retriever tool to generate 3 search queries aimed at improving the provided code by finding  ways to utilize our existing code base.
            - Search specifically for modules, classes, and functions that are relevant to your task. 
            - If the import syntax is unclear, use the Database_Retriever to look up the correct format.
            - To ensure you're importing correctly, formulate your query like this: 'How to import [item to import]'.
            - Verify that imports are implemented as per the documentation, and maintain the structural integrity of the pre-existing code.
            - To maintain data integrity, the search query must focus on checking the database for the required tabular data, ensuring that specific values are drawn from accurate sources rather than using random data.Be specific of what value you need
            for example "I need tabular data on ex 'specific gravity,latent heat, thermodynamic properties of water etc"
            - Only use modules sourced from our database, if non exit that match the functionality you are trying to achieve do not import them or referebce them

        HTML Question Reference:
        {question}

        Previous Code:
        {generated_code}
        """

        query_search = agent_with_chat_history.invoke({"input": text_step1},config={"configurable": {"session_id": "<foo>"}},)
        
        text_step2 = f"""
        Step 2: Code Generation:
            - Using the search queries utilize the database_retriever tool
            - Develop an upgraded version of the code that integrates the  identified components.
            - Confirm that all imported modules are sourced from the database; refrain from including external or non-existent imports.
            - The updated code should reflect the desired functionality and include any new optimizations.
            - Document any modifications and provide instructions for the updated code's usage.
            - Focus on importing these elements into your current codebase instead of copying their content
            - To maintain data integrity, ensure that specific values are either defined or  drawn from accurate sources rather than using random data/generation
            - Preserve the original code's structure and functionality throughout the update process.

        HTML Question Reference:
        {question}

        Previous Code:
        {generated_code}

        Only return the code, and Please enclose the finalized version of the improved code within the 'improved code' markers for clarity and seamless integration.
        """

        content = agent_with_chat_history.invoke({"input": text_step2},config={"configurable": {"session_id": "<foo>"}},)
        generated_code = content["output"]
    return generated_code


# question = """How much heat is needed to melt completely 12 kg of ice at 0°C ? Assume the latent heat of fusion of ice is 335 kJ/kg"""
# api_key = "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"
# csv_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\educational_code_gen\Question_Embedding_20240128.csv"
# html = question_html_generator(question=question,api_key=api_key,csv_path=csv_path)
# print(html)
# print(js_generator(html,api_key,csv_path,retrieval_optimization=True))