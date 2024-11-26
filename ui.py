import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import threading
import json

API_URL = "http://localhost:11434/api/generate"

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("大模型对话系统")
        self.root.geometry("800x400")

        # 创建左侧的 Node Tree Frame
        self.left_frame = tk.Frame(root, bg="#f2f2f2", width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 添加 Treeview 到左侧框架
        self.tree_label = tk.Label(self.left_frame, text="Node Tree", font=("Arial", 14), bg="#f2f2f2")
        self.tree_label.pack(pady=5)
        self.tree = ttk.Treeview(self.left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建右侧的 Chat Frame
        self.right_frame = tk.Frame(root, bg="#f2f2f2")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 添加聊天窗口
        self.chat_box = scrolledtext.ScrolledText(
            self.right_frame, wrap=tk.WORD, state=tk.DISABLED, width=60, height=20,
            font=("Courier", 12), bg="#ffffff", fg="#000000"
        )
        self.chat_box.pack(padx=10, pady=10)

        # 添加输入框和发送按钮
        self.entry_frame = tk.Frame(self.right_frame, bg="#f2f2f2")
        self.entry_frame.pack(pady=10)
        self.entry = tk.Entry(self.entry_frame, width=50, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", self.handle_enter)
        self.send_button = tk.Button(
            self.entry_frame, text="发送", command=self.send_message,
            font=("Arial", 12), activebackground="#45a049"
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

        # 示例对象：存储节点和边
        self.graph_data = {
            "nodes": [
                {"id": "1", "name": "Node 1"},
                {"id": "2", "name": "Node 2"},
                {"id": "3", "name": "Node 3"}
            ],
            "edges": [
                {"source": "1", "target": "2", "name": "Edge 1-2"},
                {"source": "2", "target": "3", "name": "Edge 2-3"}
            ]
        }

        # 初始化 Treeview 显示
        self.update_treeview()

    def update_treeview(self):
        # 清空当前 Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加节点到 Treeview
        nodes = {node["id"]: self.tree.insert("", "end", text=node["name"]) for node in self.graph_data["nodes"]}

        # 添加边为子项
        for edge in self.graph_data["edges"]:
            source_node = nodes.get(edge["source"])
            if source_node:
                self.tree.insert(source_node, "end", text=edge["name"])

    def send_message(self):
        user_input = self.entry.get()
        if user_input:
            self.entry.delete(0, tk.END)
            self.update_chat_box(f"You: {user_input}\n")
            self.update_chat_box("--" * 30 + "\n")
            threading.Thread(target=self.get_streamed_response, args=(user_input,)).start()

    def handle_enter(self, event):
            """Handle Enter key event."""
            self.send_message()

    def get_streamed_response(self, user_input):
        final_prompt = user_input
        try:
            response = requests.post(API_URL, json={
                "model": "qwen2.5:3b",
                "prompt": final_prompt,
                "streaming": True,
                "options": {
                    "temperature": 0.5
                },
            }, stream=True)
            self.update_chat_box("Model:\n")

            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        res = chunk.decode('utf-8')
                        result = json.loads(res)
                        if not result["done"]:
                            self.update_chat_box(f"{result['response']}")
                        else:
                            self.update_chat_box("\n")
                            self.update_chat_box("--" * 30 + "\n")
            else:
                self.update_chat_box("Error: Unable to get response from the server.\n")
        except Exception as e:
            self.update_chat_box(f"Error: {str(e)}\n")

    def update_chat_box(self, text):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text)
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)


# 创建主窗口
root = tk.Tk()
app = ChatApp(root)
root.mainloop()

