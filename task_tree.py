"""
目标: 完成树逻辑的构造

TaskTree: 
path: strategy, action, if_correct
TaskNode: web_content, subtask, previous_node,  
"""
from web_reader import web_reader
class TaskNode():
    def __init__(self, subtask, web_content=None):
        self.subtask = subtask  # 当前节点对应的子任务
        self.history_action = []  # 当前路径上的所有动作
        self.history_strategy = []  # 当前路径上的所有策略
        self.web_content = web_content  # 当前节点的网页内容
        self.strategy_dict = {}  # strategy -> {action -> (successor_node, if_correct)}
        self.previous_node = None  # 父节点
        self.parent_relation = None  # 父节点到当前节点的 (strategy, action)

    def add_action(self, strategy, action, next_node):
        """
        添加一个strategy-action对应的后续节点
        """
        if strategy not in self.strategy_dict:
            self.strategy_dict[strategy] = {}
        self.strategy_dict[strategy][action] = (next_node, None)  # 初始if_correct为None
        next_node.previous_node = self  # 设置父节点
        next_node.parent_relation = (strategy, action)  # 记录父节点到当前节点的关系
        return True

    def update_if_correct(self, strategy, action, if_correct):
        """
        更新路径上某个action的if_correct状态
        """
        if strategy in self.strategy_dict and action in self.strategy_dict[strategy]:
            self.strategy_dict[strategy][action] = (
                self.strategy_dict[strategy][action][0],
                if_correct
            )
            return True
        return False

    def visit_next(self, strategy, action):
        """
        根据策略和动作访问后续节点
        """
        if strategy in self.strategy_dict and action in self.strategy_dict[strategy]:
            return self.strategy_dict[strategy][action][0]
        return None

    def visit_previous(self):
        """
        访问父节点及其相关的(strategy, action)
        """
        if self.previous_node:
            return self.previous_node, self.parent_relation
        return None, None

    def update_web_content(self, web_content):
        """
        更新当前节点的网页内容
        """
        self.web_content = web_content


class TaskNode():
    def __init__(self, subtask, web_content,web_text):
        self.subtask = subtask  # 当前节点对应的子任务
        self.subtask_list = [subtask]  # 当前路径上的所有子任务
        self.history_action = []  # 当前路径上的所有动作
        self.history_strategy = []  # 当前路径上的所有策略
        self.web_content = web_content  # 当前节点的网页内容
        self.web_text = web_text
        self.strategy_dict = {}  # strategy -> {action -> (successor_node, if_correct)}
        self.previous_node = None  # 父节点
        self.parent_relation = None  # 父节点到当前节点的 (strategy, action)

    def add_action(self, strategy, action, next_node):
        """
        添加一个strategy-action对应的后续节点
        """
        strategy = "|".join(sorted(strategy))
        if strategy not in self.strategy_dict:
            self.strategy_dict[strategy] = {}
        self.strategy_dict[strategy][action] = (next_node, None)  # 初始if_correct为None
        next_node.previous_node = self  # 设置父节点
        next_node.parent_relation = (strategy, action)  # 记录父节点到当前节点的关系
        return True

    def update_if_correct(self, strategy, action, if_correct):
        """
        更新路径上某个action的if_correct状态
        """
        if strategy in self.strategy_dict and action in self.strategy_dict[strategy]:
            self.strategy_dict[strategy][action] = (
                self.strategy_dict[strategy][action][0],
                if_correct
            )
            return True
        return False

    def visit_next(self, strategy, action):
        """
        根据策略和动作访问后续节点
        """
        if strategy in self.strategy_dict and action in self.strategy_dict[strategy]:
            return self.strategy_dict[strategy][action][0]
        return None

    def visit_previous(self):
        """
        访问父节点及其相关的(strategy, action)
        """
        if self.previous_node:
            return self.previous_node, self.parent_relation
        return None, None

    def update_web_content(self, web_content):
        """
        更新当前节点的网页内容
        """
        self.web_content = web_content


class TaskTree():
    def __init__(self, total_task, root_subtask, root_web_content,root_web_text):
        self.total_task = total_task  # 总任务
        self.root_node = TaskNode(root_subtask, root_web_content,root_web_text)  # 根节点绑定第一个子任务
        self.cur_node = self.root_node  # 当前节点初始化为根节点

    def add_node(self, parent_node, strategy, action, web_content, web_text, new_subtask):
        """
        根据父节点、策略、动作生成新的后续节点，并绑定网页内容和新子任务
        """
        next_node = TaskNode(new_subtask, web_content,web_text)  # 创建新节点并绑定网页内容
        next_node.history_action = parent_node.history_action + [action]  # 继承历史动作
        next_node.history_strategy = parent_node.history_strategy + [strategy]  # 继承历史策略
        next_node.subtask_list = parent_node.subtask_list + [new_subtask]  # 继承并添加新子任务
        parent_node.add_action(strategy, action, next_node)  # 父节点记录新路径
        return next_node

    def evaluate_node(self, node, success):
        """
        根据任务完成情况，更新节点路径的if_correct标记
        """
        if success:
            # 更新路径上的if_correct为True
            for strategy, actions in node.strategy_dict.items():
                for action, (next_node, _) in actions.items():
                    node.update_if_correct(strategy, action, True)
        else:
            # 更新路径上的if_correct为False
            for strategy, actions in node.strategy_dict.items():
                for action, (next_node, _) in actions.items():
                    node.update_if_correct(strategy, action, False)


if __name__ == "__main__":
    # 示例使用
    tree = TaskTree("Handle Emails", "open gmail", "<html>Root content of Gmail</html>")

    # 根节点
    root = tree.root_node
    print(f"Root Subtask: {root.subtask}")
    print(f"Root Web Content: {root.web_content}")

    # 添加新节点
    next_node = tree.add_node(root, "strategy_1", "action_1", "<html>Content 1</html>", "read email")
    next_node = tree.add_node(next_node, "strategy_2", "action_2", "<html>Content 2</html>", "reply email")

    print(f"Current Node Subtask: {next_node.subtask}")
    print(f"Subtask List: {next_node.subtask_list}")
    print(f"Web Content: {next_node.web_content}")

    # 访问父节点
    parent, relation = next_node.visit_previous()
    print(f"Parent Subtask: {parent.subtask}")
    print(f"Parent Relation (strategy, action): {relation}")

    # 更新任务完成状态
    tree.evaluate_node(next_node, success=True)
    print(f"Action List: {next_node.history_action}")
    print(f"Strategy List: {next_node.history_strategy}")
