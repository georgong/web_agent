import requests
from web_reader import web_reader
import json
import re
import time
import traceback
from prompting import generate_elements_prompt,reader_prompt
from controller import controller


class BaseLLM():
    def __init__(self,url = "http://localhost:11434/api/generate",model = "qwen2.5:3b"):
        self.url = url
        self.model = model
        self.web_reader = web_reader("https://www.youtube.com")
        self.basic_prompt = reader_prompt
        self.controller = controller({"click":"",
                                      "typing":"",
                                      "jumpto":"",
                                      "response":""})
        
    
    def generate_prompt(self,task):
        interactive_elements, annotations,full_page_text = self.web_reader.read()
        prompt = generate_elements_prompt(interactive_elements)
        final_prompt = self.basic_prompt.replace("{web_info}",prompt).replace("{task}",task).replace("{current_url}",self.web_reader.current_url)
        print(final_prompt)
        result = ""
        req = requests.post(self.url,json = {"model":self.model,#"arcee-ai/arcee-agent",
                                             "prompt":final_prompt,"streaming":True,"options": {
    "temperature": 0.5
  },},stream=True)
        
        for i in req.iter_lines():
            print(output:=json.loads(i.decode("utf-8"))["response"],end = "")
            result += output
        # 使用 re.findall 查找所有匹配的内容
        self.controller.call_function(result,self.web_reader)

    def debug_test(self):
        while True:
            time.sleep(1)
            interactive_elements, annotations,full_page_text = self.web_reader.read()
            prompt = generate_elements_prompt(interactive_elements)
            print(prompt)
            test_input = str(input())
            if test_input == "/quit":
                break;
            else:
                print("self.web_reader." + test_input)
                try:
                    eval("self.web_reader." + test_input)
                except Exception as e:
                    print(e)



if __name__ == "__main__":
    llm = BaseLLM()  #
    llm.debug_test()
    while True:
        user_input = input()
        llm.generate_prompt(user_input)



        
        