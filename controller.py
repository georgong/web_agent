"""
controller is a class for long term managements of TaskTree and Prompt generating
it need to deal with complex strategys and finally output a string for LLM
and receive the respond from LLM to extract the agent_function and check result 
"""
import re
from prompting import checker_prompt, generate_elements_prompt,function_data,generate_functions_descriptions,reasoning_prompt,summerization,reader_prompt
from web_reader import web_reader
from task_tree import TaskTree
#from ui import ChatApp
#import tk
import ast
import requests
import json


class controller():
    def __init__(self,llm_url,model):
        self.task_tree = None #当用户给予命令后, 初始化这个
        self.history = [] #记录所有代理任务产生的树结构
        self.agent_function = function_data #记录所有代理函数名和它的description,可以在文件里修改
        self.current_node = None
        self.llm_url = llm_url #处理部分需要LLM 参与的prompting engineering
        self.model = model
        #self.ui_root = tk.Tk()
        #self.front_ui = ChatApp(llm_url,model,self.ui_root)
        self.control_model = None
        self.web_reader = None

    def total_prompt_generate(self,strategy_list):
        task = self.task_tree.total_task
        web_content,record = generate_elements_prompt(self.task_tree.cur_node.web_content)
        print(type(web_content))
        text = self.task_tree.cur_node.web_text
        subtask = self.task_tree.cur_node.subtask
        history_action = self.task_tree.cur_node.history_action
        history_stratety = self.task_tree.cur_node.history_strategy
        function_data = self.agent_function
        insert_place0 = "" #before the web_content
        insert_place1 = "" #after the web content
        insert_place2 = "" #after all of the content
        function_str = generate_functions_descriptions(function_data)
        if "reasoning" in strategy_list: #如果使用reasoning, 那么在prompt中加入引导大模型思考的语句
            insert_place2 += reasoning_prompt
        if "external_memory" in strategy_list:
            insert_place0 += ""
        if "summerization" in strategy_list:
            insert_place1 += summerization(web_content,text, self.llm_url,self.model)
        if "filtering" in strategy_list:
            pass
        print(type(web_content))
        assert isinstance(insert_place0,str),"insert_place0 is not string"
        assert isinstance(insert_place1,str),"insert_place1 is not string"
        assert isinstance(insert_place2,str),"insert_place2 is not string"
        final_prompt = reader_prompt.replace("{web_info}",str(web_content)).replace("{text}",str(text)).replace("{insert_place0}",str(insert_place0)).replace("{function_list}",str(function_str)).replace("{insert_place1}",str(insert_place1)).replace("{insert_place2}",str(insert_place2)).replace("{task}",str(task)).replace("{subtask}",str(subtask))
        if "self-reflection" in strategy_list:
            pass
        return final_prompt

        

        

    def extract_output(self, string):
        # 提取函数调用
        function_names = list(self.agent_function.keys())
        func_pattern = r"(" + "|".join(function_names) + r")\((.*?)\)"
        func_match = re.search(func_pattern, string)

        one_function_call = None
        if func_match:
            func_name = func_match.group(1)
            params = func_match.group(2)

            # 解析并构造函数调用
            call_string = f"self.web_reader.{func_name}({params})"
            try:
                eval(call_string)  # 动态调用函数
                one_function_call = f"{func_name}({params})"  # 返回函数调用字符串
            except Exception as e:
                print(f"Error calling function '{func_name}': {e}")

        # 提取 next_subtask
        subtask_pattern = r"(?i)\bnext_subtask[:\- ]\s*([\w_ ]+)"
        subtask_match = re.search(subtask_pattern, string)
        next_subtask = subtask_match.group(1).strip() if subtask_match else None

        return (one_function_call, next_subtask)





    def query(self, task, inital_website):
        self.web_reader = web_reader(inital_website)
        root_web_content,_,root_web_text = self.web_reader.read()
        self.task_tree = TaskTree(task,"initial state, haven't generate subtask, wait for start",root_web_content,root_web_text)
        strategy_list = self.select_strategy()
        total_prompt = self.total_prompt_generate(strategy_list)
        print("input:",total_prompt)
        llm_output = self.generate_output(total_prompt)
        print("output:",llm_output)
        action,new_subtask = self.extract_output(llm_output)
        print("result:",action,new_subtask)
        web_content,web_text = None,None
        while True:
            web_content,_,web_text = self.web_reader.read()
            self.task_tree.cur_node = self.task_tree.add_node(self.task_tree.cur_node, strategy_list, action, web_content, web_text, new_subtask)
            print("text:",web_text)
            strategy_list = self.select_strategy()
            total_prompt = self.total_prompt_generate(strategy_list)
            print("input:",total_prompt)
            llm_output = self.generate_output(total_prompt)
            print("output:",llm_output)
            action,new_subtask = self.extract_output(llm_output)
            print("result:",action,new_subtask)
            #break;
            if new_subtask == "done":
                break;



    def select_strategy(self):
        """
        THis is the function to select strategy
        """
        return ["reasoning"]
    
    def generate_output(self,total_prompt):
        response = requests.post(self.llm_url, json={
                    "model": self.model,
                    "prompt": total_prompt,
                    "streaming": False,
                    "options": {
                        "temperature": 0
                    },
                }, stream=False)
        result = ""
        for i in response.iter_lines():
            result += json.loads(i.decode('utf-8'))["response"]
        return result
        
        
        



        
if __name__ == "__main__":
    model = "arcee-ai/arcee-agent"
    llm_url = "http://localhost:11434/api/generate"
    c = controller(llm_url,model)
    c.query("search and open ucsd","http://google.com")
