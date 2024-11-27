
import re
from prompting import checker_prompt
import ast
class controller():
    def __init__(self,function_dict):
        self.actionlist = []
        self.function_dict = function_dict
        assert(isinstance(function_dict,dict)),"function_dict should be an instance of dictionary"

    def __invoke_from_string(self, obj, method_call_str):
        """
        Dynamically invoke a method from a string in the format: method_name(param1, param2, ...)
        """
        # Parse the method name and arguments
        method_name, args_str = method_call_str.split("(", 1)
        args_str = args_str.rstrip(")")  # Remove closing parenthesis
        
        # Convert arguments string to Python objects
        args = ast.literal_eval(f"({args_str},)")  # Use `ast.literal_eval` for safe parsing

        # Get the method by name and invoke it with arguments
        method = getattr(obj, method_name.strip())
        return method(*args)

    def call_function(self,result,web_reader):
        function_names = list(self.function_dict.keys())
        pattern = r"|".join([re.escape(fn) + r"\(.+?\)" for fn in function_names])
        # 使用 re.findall 查找所有匹配的内容
        matches = re.findall(pattern, result, re.DOTALL)
        matches_string = matches[0].replace("'", '"') # invoid of output such as "stupid LLM'
        print(matches_string)
        try:
            #call function if there is this method name
            #TODO add vague matching
            self.__invoke_from_string(web_reader, matches_string)
        except AttributeError:
            # not a valid function
            print(f"{matches_string} is not a valid function")
        

        pass


    def submit(self):
        """
        allow the LLM to submit the task for check
        """
        pass

    def planning(self):
        """
        planning to return a list of subtask/action []
        """
        pass
    def Reasoning(self):
        """
        given a reason for the function call LLM chose3
        """
    def Reflection(self):
        """
        Based on the current error, correct your actions
        """
    def query(self):
        """
        query the user for the result
        """
    def external_memory(self):
        """
        recall the memory 
        """


