# Educational Code Generator

## Getting Started

### Install Python
 Download Python, by heading to the [official Python website](https://www.python.org/downloads/) and downloading the lastest version.

### Cloning Respository
 To clone the github repository to your local machine, use the following command:
 ```
 git clone https://github.com/lucib3196/educational_code_gen.git
 ```
 Then move into the project directory by using:
 ```
 cd educational_code_gen
 ```

### Installing Dependencies
 Install all the dependencies needed for this project
 ```
 pip install -r requirements.txt
 ```

### Creating API Key

 First create an [OpenAI account](https://auth0.openai.com/u/signup/identifier?state=hKFo2SBUaHE3QXZUcnRqamwwaDZqVHJOQ1JVYW05MkVTTG8wdaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEFJTG1BZ25SS0Z5d1dzYkRPS3h6UnczcVRMRXdmeERho2NpZNkgRFJpdnNubTJNdTQyVDNLT3BxZHR3QjNOWXZpSFl6d0Q). Next, navigate to the [API Key Page](https://platform.openai.com/api-keys) and click on `Create new secret key`. After creating your key, save the api key somewhere safe and do not share it with anyone.

### Setting up API Key
 
 In the project folder, create a `.env` file. In the file you just created, write the following lines:
 ```
 OPENAI_API_KEY=<your_api_key>
 model=<llm_model_version>
 ```
 > NOTE: replace `<your_api_key>` with the api key you just created and `<llm_model_version>` with the LLM version associated with your api key (e.g gpt-3.5-turbo)


 You're set! If all the steps were successful you should be ready to run the program

 ## Usage
 In the project folder, type the following command in your terminal to run the program:
 ```
 python main.py
 ```