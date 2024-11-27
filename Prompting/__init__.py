
reader_prompt = """
        You are an intelligence robot aims for function call based on the given function and webpage information. here is the informations of the current pages:
        current_url: {current_url}
        {web_info},
        think of what each elements is and which elements you need to use.
        You can use <function_calls>function(parameter)</function_calls>, eg: <function_calls>click(2)</function_calls>
         to wrapper the function you need to call to preform the task.
        here is the functionlist:
        ```
        def click(id:integer):
            #click on the elements with specific id
        def typing(id:integer,text:string):
            #click on the elements and then type on the elements with the input text
        def jumpto(url:string):
            #jump to a new url in the web page
        def back():
            #get back to the previous page
        def response(text:string):
            #the word you give back to user, report what you have done or answer the user's QA question.
        ```

        You can only call one function in each response step by step, and remember to wrapper it with <function_calls>.
        Now Please complete or answer the user's request: {task}     
        """

checker_prompt = """



"""




def generate_elements_prompt(interactive_elements):
    prompt = ""
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
        
            
        if len(record) > 1:
            prompt += str(record) + "\n"
    return prompt
