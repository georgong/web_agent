import requests
import json
"""
this file store some function and template for prompting generating
and the total_prompting generating function is in controller class
"""

checker_prompt = """



"""
reader_prompt = """
        You are an intelligence robot aims for function call based on the given function and webpage information.\n\
        {insert_place0}\n\
        here is the informations of the current pages:\n\
        current_url: {current_url}\n\
        {web_info},\
        think of what each elements is and which elements you need to use.\n\
        You can use <function_calls>function(parameter)</function_calls>, eg: <function_calls>click(2)</function_calls>\n\
         to wrapper the function you need to call to preform the task.\
        {insert_place1}\
        here is the functionlist:\n\
        ```
        {function_list}\
        ```
        You can only call one function in each response step by step, and remember to wrapper it with <function_calls>.\
        Since each time you can only call one function, you should think of what the next subtask you need to do, \
        the next subtask is a text content describe roughly what the next step after this function be called.
        your output should be 1.one_function_call:... 2.next_subtask:...
        Now Please complete or answer the user's request: {task} {insert_place2}\n\
        for the total task, your current subtask is: {subtask}\n\
        """



def generate_elements_prompt(interactive_elements):
    prompt = ""
    element_list = []
    for elements_dict in interactive_elements:
        record = {}
        record["id"] = elements_dict["id"]
        if elements_dict["position"][1] <=0 or elements_dict["position"][0] <=0:
            continue;
        if elements_dict["tag_name"] == "a":
            record["type"] = "link"
            record["link"] = elements_dict["href"]
        else:
            if elements_dict["tag_name"] != None:
                record["type"] = elements_dict["tag_name"]
            else:
                record["type"] = elements_dict["type"]
        if elements_dict["text"] != "":
            record["innertext"] = elements_dict["text"]
        #check if there is alt_label
        if elements_dict["alt_label"] != None:
            record["innertext"] = elements_dict["alt_label"]
        #check if there is aria-label
        if "aria-label" in elements_dict["aria_label"]:
            record["innertext"] = elements_dict["aria_label"]["aria-label"]
        if elements_dict["role"] != None:
            record["role"] = elements_dict["role"]
        
            
        if len(record) > 1:
            prompt += str(record) + "\n"
            element_list.append(str(record))
    return prompt,element_list

plan_prompt = """
based on the current task, you need to make a plan to decompose it into many subtasks, you should return a list of subtasks 
based on the decomposition of the tasks given to you. if the tasks is too simple to decompose, just return the tasks itself
"""

reasoning_prompt = """
for the action you choose, you need to given the reason why you use this action. output your thought and your observation and then determine your action based on this.
"""

summary_prompt = """
System: You are an intelligence robot aims for analyzing the web_contents and text, then summary what the page content is. roughly 30 word
{web_content}{text}, 
Agents: Based on the web_content, you are now in a page in which:
"""


def generate_functions_descriptions(func_dict):
    """
    Generate function definitions from a dictionary of function names, parameters, and descriptions.

    :param func_dict: dict, where keys are function names and values are lists with [parameter, description].
    :return: str, formatted function definitions.
    """
    function_definitions = []

    for func_name, (params, description) in func_dict.items():
        # Format the parameters
        if params:
            formatted_params = ", ".join([f"{param}:{ptype}" for param, ptype in params.items()])
        else:
            formatted_params = ""

        # Generate the function definition
        function_def = f"def {func_name}({formatted_params}):\n    \"\"\"\n    {description}\n    \"\"\"\n    pass\n"
        function_definitions.append(function_def)

    return "\n".join(function_definitions)

reflection_prompt = """
        You are an intelligence robot aims for checking the function call based on the given function and webpage information.\n\
        {insert_place0}
        here is the informations of the current pages:\
        current_url: {current_url}\n\
        {web_info},\
        The text shown on web is {text}
        {insert_place1}\
        here is the functionlist can be chosed to call to preform the task:\
        ```
        {function_list}\
        ```
        Notice that typing() means click and then type
        here is the function another agent used for the task {task}:{function}
        related_web_elements is {related_web_elements}
        Now please check if this is on the correct way or not, Notice there are usually many correct answers to prefrom a task
        generated the thinking process, and finally, 
        if correct, return this function itself, if not correct, return your function_call.
        Your answer should looks like this,"thought:... function_call:..."
        """


def generate_reflection(subtask,function_str,action,web_content,text,llm_url,model,related_web_elements,insert_place0,insert_place1,insert_place2):
    prompt = reflection_prompt.replace("{web_info}",web_content).replace("{text}",text).replace("{insert_place0}",insert_place0).replace("{function_list}",function_str).replace("{related_web_elements}",related_web_elements)
    final_prompt = prompt.replace("{insert_place1}",insert_place1).replace("{insert_place2}",insert_place2).replace("{task}",subtask).replace("{function}",action)
    print(final_prompt)
    response = requests.post(llm_url, json={
                    "model": model,
                    "prompt": final_prompt,
                    "streaming": False,
                    "options": {
                        "temperature": 0
                    },
                }, stream=False)
    result = ""
    for i in response.iter_lines():
        #print(i.decode('utf-8'))
        result += json.loads(i.decode('utf-8'))["response"]
    return result






def summerization(web_content,text,llm_url,model):
    final_prompt = summary_prompt.replace("{web_content}",web_content).replace("{text}", text) + ""
    response = requests.post(llm_url, json={
                    "model": model,
                    "prompt": final_prompt,
                    "streaming": False,
                    "options": {
                        "temperature": 0
                    },
                }, stream=False)
    result = ""
    for i in response.iter_lines():
        result += json.loads(i.decode('utf-8'))["response"]
    return result








# Example dictionary
function_data = {
    "click": [{"id": "integer"}, "Click on the elements with specific id"],
    "typing": [{"id": "integer", "text": "string"}, "Click on the elements and then type on the elements with the input text"],
    "back": [None, "Get back to the previous page"],
    "response": [{"text": "string"}, "The word you give back to user, report what you have done or answer the user's QA question"],
    "done": [None,"the task is already complete, end the task"]
}
#"jumpto": [{"url": "string"}, "Jump to a new URL in the web page"],



external_instruction = ["for search somethings start from google.com, you need to typing on the elements with innertext 'search', and then analyze or click in the search result"]