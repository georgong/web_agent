from controller import controller
from time import time
from driven_model import simple_baseline
def test_result(time = 15):
    result = []
    for i in range(time):
        model = "arcee-ai/arcee-agent"
        driven_model = simple_baseline(strategy_list=["summerization"])
        llm_url = "http://localhost:11434/api/generate"
        c = controller(llm_url,model,driven_model)
        result.append(c.query_test("Check out the wiki description of Chongqing in China","http://google.com",["https://www.google.com/search?","wikipedia.org"],max_limitation=7))
    return sum(i for i in result)/time


if __name__ == "__main__":
    result = test_result()
    print(result)
    with open("result.txt","w+") as f:
        f.write("strategy: "+",".join(["summerization"])+ " hit_rate: "+str(result))