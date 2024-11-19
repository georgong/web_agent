import requests
from Web_Reader import web_reader
import json
import re
import time
import traceback

class ReActLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader
    
    def generate_prompt(self):
        pass

class ToTLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader
    
    def generate_prompt(self):
        pass


class LATSLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader
    
    def generate_prompt(self):
        pass


class COTLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader
    
    def generate_prompt(self):
        pass


class BaseLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader("https://www.google.com")
        self.basic_prompt = """
        You are an intelligence robot aims for function call based on the given function and webpage information. here is the informations of the current pages
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
        
    
    def generate_prompt(self,task):
        prompt = ""
        interactive_elements, annotations,full_page_text = self.web_reader.read()
        print(interactive_elements)
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
            #if elements_dict["aria_label"] != "None":
            #    record["innertext"] = elements_dict["aria_label"]["aria-label"]
            if elements_dict["text"] != "":
                record["innertext"] = elements_dict["text"]
            if elements_dict["alt_label"] != None:
                record["innertext"] = elements_dict["alt_label"]
            if elements_dict["aria_label"] != {}:
                record["innertext"] = elements_dict["aria_label"]["aria-label"]
            
                
            if len(record) > 1:
                prompt += str(record) + "\n"

        final_prompt = self.basic_prompt.replace("{web_info}",prompt).replace("{task}",task)
        print(final_prompt)
        result = ""
        req = requests.post(self.url,json = {"model":"qwen2.5:3b",#"arcee-ai/arcee-agent",
                                             "prompt":final_prompt,"streaming":True,"options": {
    "temperature": 0.5
  },},stream=True)
        for i in req.iter_lines():
            print(output:=json.loads(i.decode("utf-8"))["response"],end = "")
            result += output
        pattern = r"<function_calls>(.*?)</function_calls>"
    
    # 使用 re.findall 查找所有匹配的内容
        matches = re.findall(pattern, result, re.DOTALL)
        for i in matches:
            try:
                eval("self.web_reader." + i)
            except Exception as e:
                print((e))

    def debug_test(self):
        while True:
            time.sleep(1)
            interactive_elements, annotations,full_page_text = self.web_reader.read()
            print(interactive_elements)
            test_input = str(input())
            if test_input == "/quit":
                break;
            else:
                print("self.web_reader." + test_input)
                eval("self.web_reader." + test_input)





if __name__ == "__main__":
    
    llm = BaseLLM()
    llm.debug_test()
    #while True:
        #user_input = input()
        #llm.web_reader.jumpto('https://mail.google.com/mail/&ogbl')
        #llm.generate_prompt(user_input)



        
        