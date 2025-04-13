import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.chats import Chat

import github_api_invoker

load_dotenv()

search_code_limit = 10
gemini_model_id = "gemini-2.0-flash"
gemini_system_instruction = \
    f"""
    You are a documentation generator tasked with explaining a piece of code. You will be provided with a function
    which you may call, "search_code". If you think you need more information or context about
    the code, you may use the search_code function to search for content of relevant files in Github. 
    If you believe you already have sufficient information, you can provide an explanation of the code in technical
    documentation style. If you failed to obtain relevant information from code_search, please tell me so and do not
    explain code if you are not sure about its meaning or context. Due to API limits, please do not invoke search_code more than 10 times.
    You don't have to answer with greetings or formalities, just invoke search_code or explain the code is enough.
    You don't have to quote the code you found, unless you think it is vital in understanding your explanation.
    
    If the provided code is a class, the code explanation should look like this:
    **<class_name> (Class):**
    
    <description of the class and its features and functions>
    
    **Declared methods:**
    <method_1 signature>: <method_1 summary>
    <method_2 signature>: <method_2 summary>
    ...
    
    If the provided code is a function, the code explanation should look like this:
    **<function_name> (Function):**
    
    <summary of the function>
    
    **Parameters:**
    <parameter_1_name> (<parameter_1_type>): <parameter_1_summary>
    ...
    **Return:**
    (<return_type>) <return value meaning> [If the function does not return anything, leave this as blank.]
    
    If the provided code is a normal code segment, you may decide the presentation of the explanation.
    
    Please provide an explanation in Markdown format (be mindful of line breaks!).
    If you think there are multiple matching results, list all of them in the most-relevant-first order.
    """

search_code_function = {
    'name': 'search_code',
    'description': 'Search and retrieve content of files matching search criteria provided in the parameter',
    'parameters': {
        'type': 'object',
        'properties': {
            'keyword': {
                'type': 'string',
                'description': 'Key words or search phrase for the search.'
            },
            'repo': {
                'type': 'string',
                'description': 'Full name of the Github repository where the search will take place, e.g. "facebook/react".'
            },
            'language': {
                'type': 'string',
                'description': 'Only search code of the specified language.'
            },
            'search_keyword_in_path': {
                'type': 'boolean',
                'description': 'If you want to search files whose names or path match the keyword, set this to true. Otherwise, set it to false.'
            },
            'search_exact': {
                'type': 'boolean',
                'description': 'Specify true to search for the exact keyword, false otherwise.'
            }
        },
        'required': ['keyword']
    }
}


def new_gemini_chat() -> Chat:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tools = types.Tool(function_declarations=[search_code_function])
    config = types.GenerateContentConfig(system_instruction=gemini_system_instruction, tools=[tools])
    return client.chats.create(model=gemini_model_id, config=config)


def handle_code_explanation(code: str, additional_info: str='') -> str:
    chat = new_gemini_chat()
    response = chat.send_message(message=f"""
**Code to explain:** 
{code}

**Additional information about the code:** 
{additional_info}

You could invoke search_code, or provide an explanation of the given code, documentation-style.
"""
    )
    search_code_invocation = 0
    while response.function_calls:
        files = ''
        for function_call in response.function_calls:
            if function_call.name == 'search_code':
                if search_code_invocation < search_code_limit:
                    files += github_api_invoker.search_code(**function_call.args)
                    search_code_invocation += 1
            else:
                print(f'An invalid function {function_call.name} is requested. Skipping...')
        if search_code_invocation >= search_code_limit:
            response = chat.send_message(message=f"""
Here is the result of the function call you invoked in the previous reply. Please provide an explanation of the code 
provided in the first request. search_code cannot be invoked anymore.

**search_code result (each file starts with "--- <full_repo_name>/<path_to_file>" and ends with "---" on a single line):**
{files}
"""
            )
            break
        else:
            response = chat.send_message(message=f"""
Here is the result of the function call you invoked in the previous reply. You may continue to invoke search_code, 
or provide an explanation of the code provided in the first request.

**search_code result (each file starts with "--- <full_repo_name>/<path_to_file>" and ends with "---" on a single line):**
{files}
{'No file found. Try searching with a different keyword instead? Or maybe search broader?' if len(files) == 0 else ''}
"""
            )
    return response.text
