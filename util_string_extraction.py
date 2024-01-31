import re

def extract_javascript_generate_code(javascript_code):
    """
    Extracts a specific section of JavaScript code that defines a 'generate' function,
    starting with 'const generate =' and ending just before 'module.exports', from a
    larger string of JavaScript code.

    This function assumes the JavaScript code is enclosed within triple backticks (```)
    as used in Markdown or similar formats.

    Parameters:
    javascript_code (str): String containing the entire JavaScript code block.

    Returns:
    str: The extracted JavaScript code defining the 'generate' function, or an error message if the
         required code block or the specific 'generate' function definition is not found.
    """
    # Attempt to extract the JavaScript code block enclosed in triple backticks
    code_block_match = re.search(r'```javascript(.*?)```', javascript_code, re.DOTALL)

    if code_block_match:
        code_within_backticks = code_block_match.group(1)

        # Attempt to extract the 'generate' function code
        generate_function_match = re.search(r'(const generate = .*?)module\.exports', code_within_backticks, re.DOTALL)

        if generate_function_match:
            # Return the extracted 'generate' function code
            return generate_function_match.group(1).strip()
        else:
            # Return an error message if the 'generate' function definition is not found
            return "Pattern for generate() to module.exports not found."
    else:
        # Return an error message if the code block is not enclosed in triple backticks
        return "Triple backtick JavaScript code block not found."

# # Example usage:
# js_code = """
# ```javascript
# // Some comment
# const generate = function() {
#     // Function body
# };
# module.exports = generate;
# ```"""

# print(extract_javascript_generate_code(js_code))


def extract_content_from_triple_quote(input_string):
    """
    Extracts content from a string that is wrapped in triple quotes.

    Parameters:
    input_string (str): The string containing the triple quoted content.

    Returns:
    str: The extracted content, or an empty string if no triple quoted content is found.
    """
    

    # Regular expression to match triple quoted strings (both single and double quotes)
    pattern = r'(""".*?"""|\'\'\'.*?\'\'\'|```.*?```)'

    # Using re.DOTALL to make . match newlines as well
    matches = re.findall(pattern, input_string, re.DOTALL)

    # Extracting content inside the triple quotes
    extracted_contents = [match[3:-3] for match in matches]

    return extracted_contents