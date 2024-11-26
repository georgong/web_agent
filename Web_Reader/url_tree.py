class URLNode:
    def __init__(self, url):
        self.url = url
        self.children = []  # 子节点，表示链接的 URL
        self.element_dict = {}  # 存储元素及其 XPath

    def add_child(self, child_node):
        """添加子节点"""
        self.children.append(child_node)

    def add_element(self, element, xpath):
        """添加元素及其对应的 XPath 到 element_dict"""
        self.element_dict[element] = xpath

class URLHierarchy:
    def __init__(self):
        self.root = None  # 根节点

    def set_root(self, url):
        """设置根节点"""
        self.root = URLNode(url)

    def find_node(self, url, node=None):
        """递归查找特定 URL 的节点"""
        if node is None:
            node = self.root

        if node.url == url:
            return node

        for child in node.children:
            found_node = self.find_node(url, child)
            if found_node:
                return found_node
        return None

    def add_url(self, parent_url, child_url):
        """为父 URL 添加一个子 URL 节点"""
        parent_node = self.find_node(parent_url)
        if not parent_node:
            raise ValueError(f"Parent URL '{parent_url}' not found.")
        
        # 创建子节点并添加到父节点的 children 列表中
        child_node = URLNode(child_url)
        parent_node.add_child(child_node)
        return child_node

    def add_element_to_url(self, url, element, xpath):
        """为特定 URL 添加元素及其 XPath"""
        node = self.find_node(url)
        if not node:
            raise ValueError(f"URL '{url}' not found.")
        node.add_element(element, xpath)

    def display_structure(self, node=None, level=0):
        """打印 URL 层级结构及其元素"""
        if node is None:
            node = self.root
        
        print("  " * level + f"URL: {node.url}")
        print("  " * level + f"Elements:")
        for element, xpath in node.element_dict.items():
            print("  " * (level + 1) + f"{element}: {xpath}")
        
        for child in node.children:
            self.display_structure(child, level + 1)

# 示例用法
if __name__ == "__main__":
    hierarchy = URLHierarchy()
    hierarchy.set_root("https://root-url.com")

    # 添加子 URL
    page1_node = hierarchy.add_url("https://root-url.com", "https://root-url.com/page1")
    page2_node = hierarchy.add_url("https://root-url.com", "https://root-url.com/page2")

    # 添加元素及 XPath 到特定 URL
    hierarchy.add_element_to_url("https://root-url.com", "header", "/html/body/header")
    hierarchy.add_element_to_url("https://root-url.com/page1", "search_box", "/html/body/div[1]/input")
    hierarchy.add_element_to_url("https://root-url.com/page2", "login_button", "/html/body/div[2]/button")

    # 展示 URL 层级结构
    hierarchy.display_structure()


    #url
    # child_url child_url