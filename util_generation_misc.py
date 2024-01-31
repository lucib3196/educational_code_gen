from openai import OpenAI
def create_variation_solution(original_question,original_solution_guide,question_variation,new_unknown,api_key):
    client = OpenAI(api_key=api_key)
    prompt = """
    Original Question: {original_question}
        Solution Guide: {original_solution_guide}
        New Task:
        You are presented with a variation of the original question, focusing on a new unknown: {new_unknown}. The following steps are to be undertaken:

        1. Analyze Original Solution:
        Review the original solution and the formula it uses.
        2. Modify Formula:
        Adapt the formula to solve for the new unknown: {new_unknown}.
        3. 3. Symbolic Representation:
        Instead of substituting numerical values, use symbolic representations for the known variables in the new problem when applying them to the modified formula."
        4. Solve for New Unknown:
        5. Compute the solution for the new unknown: {new_unknown}.
        Clear Explanation:
        6. 
        Provide a step-by-step explanation of the entire process, ensuring clarity and understanding.
        Use of LaTeX:
        7. 
        Present all equations and mathematical symbols using LaTeX for readability and precision.
        Question Variation: {question_variation}

        Task:
        Create a new solution guide that adheres to these guidelines, aiding students in comprehending and solving the problem variation.

        Output:
        '''insert new_solution_guide'''"""
    completion = client.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    )
    response = completion.choices[0].message.content
    return response