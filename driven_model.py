class llm_driven_model():
    def __init__(self):
        pass
        
    def predict(self,web_content,web_screen,web_text,strategy_list,new_subtask,task):
        pass



class simple_baseline():
    def __init__(self,strategy_list):
        self.strategy_list = strategy_list
        pass
    
    def predict(self,web_content,web_screen,web_text,strategy_list,new_subtask,task):
        return self.strategy_list


