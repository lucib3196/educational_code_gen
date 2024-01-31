import os
from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain.agents import create_openai_functions_agent, AgentExecutor
import asyncio
# Set up file management tools
file_tools = FileManagementToolkit(selected_tools=["read_file", "write_file", "list_directory"]).get_tools()
total_tools = file_tools 

from langchain import hub


def create_folder(folder_name, target_path):
    """
    Create a folder with a specified name at a given path. If a folder with the same name already exists,
    a new folder with a unique number appended to its name is created instead.

    Parameters:
    folder_name (str): The name of the folder to be created.
    target_path (str): The path where the folder should be created.

    Returns:
    str: The full path of the created folder, or None if an error occurs.
    """
    full_path = os.path.join(target_path, folder_name)

    try:
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Folder '{full_path}' created successfully.")
            return full_path
        else:
            index = 1
            while True:
                new_folder_name = f"{folder_name}_{index}"
                new_full_path = os.path.join(target_path, new_folder_name)
                if not os.path.exists(new_full_path):
                    os.makedirs(new_full_path)
                    print(f"Folder '{new_full_path}' created successfully.")
                    return new_full_path
                index += 1
    except Exception as e:
        print(f"Error creating folder '{full_path}': {str(e)}")
    return None


async def export_files(file_name: str, file_content: str, file_location: str, api_key: str, model_name: str):
    """
    Asynchronously exports file content to a specified location with a given file name, using a conversational AI agent.

    Parameters:
    file_name (str): The name of the file to be saved.
    file_content (str): The content to be written in the file.
    file_location (str): The location where the file should be saved.
    api_key (str): The API key for the ChatOpenAI service.
    model_name (str): The name of the model to be used in the ChatOpenAI service.

    Returns:
    The output from the conversational AI agent after processing the export command.
    """
    # Set up ChatOpenAI parameters
    llm = ChatOpenAI(temperature=0, model_name=model_name, api_key=api_key)
    
    # Define the tools (replace 'tools' with actual tools)
    tools = total_tools
    
    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/openai-functions-agent")

    # Set up the agent
    agent = create_openai_functions_agent(llm, tools,prompt)

    # Set up the AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True)
    
    #file_content = file_content.replace("\n", "\\n").replace('"', '\\"')
    # Run the agent to export files
    output = agent_executor.invoke({"input": f"Given the following {file_content} save the file as {file_name} in the following folder {file_location}. Modify the file content to ensure it is capable of being exported"})
    return output


# # Test the function
# async def test_export_files():
#     file_name = "test.txt"
#     file_content = "This is a test file content"
#     file_location = "test_output"
#     api_key = "insert-api_key"
#     model_name = "gpt-3.5-turbo"

#     output = await export_files(file_name, file_content, file_location, api_key=api_key, model_name=model_name)
#     print(output)

# # Run the test
# asyncio.run(test_export_files())