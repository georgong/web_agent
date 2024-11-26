from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
import time
#from lxml import etree
from selenium.webdriver.common.action_chains import ActionChains
from .url_tree import URLHierarchy
import numpy as np
#import cv2
#import pytesseract
#from sklearn.cluster import KMeans
#import math
#import random
#import numpy as np
#from .annotation import image_read,annotate_text_centers
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import MoveTargetOutOfBoundsException, WebDriverException


# 假设已经找到需要点击的元素
#selenium_element = driver.find_element(By.XPATH, xpath_selector)
#location = selenium_element.location
#size = selenium_element.size

# 计算点击位置 (点击元素的中心位置)
#x_offset = size['width'] / 2
#y_offset = size['height'] / 2

# 使用 ActionChains 模拟点击元素的中心位置
#action = ActionChains(driver)
#action.move_to_element_with_offset(selenium_element, x_offset, y_offset).click().perform()
def get_xpath(element):
    """
    辅助函数，根据 BeautifulSoup 元素生成 XPath。
    """
    components = []
    for parent in element.parents:
        siblings = parent.find_all(element.name, recursive=False)
        if len(siblings) == 1:
            components.append(element.name)
        else:
            position = siblings.index(element) + 1
            components.append(f"{element.name}[{position}]")
        element = parent
    components.reverse()
    return '/' + '/'.join(components)


class web_reader():

    def __init__(self,init_webset,function_list = []):
        option = webdriver.ChromeOptions()
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=option)
        self.driver.get(init_webset)
        self.device_pixel_ratio = self.driver.execute_script("return window.devicePixelRatio")
        self.function_list = function_list
        self.url_tree = URLHierarchy()
        self.current_url = init_webset
        self.url_tree.set_root(init_webset)
        self.current_webpage = None
        pass

    def annotation(self,visualize = True):
        return None
        #screenshot = self.driver.get_screenshot_as_png()
        #image_array = np.frombuffer(screenshot, dtype=np.uint8)
        #cv2_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        #height,weight = int(cv2_image.shape[0]/self.device_pixel_ratio),int(cv2_image.shape[1]/self.device_pixel_ratio)
        #cv2_image = cv2.resize(cv2_image, (weight,height), interpolation=cv2.INTER_AREA)
        #textbox = image_read(cv2_image)[0]
        #print(textbox)
        #if visualize:
        #    return textbox, annotate_text_centers(cv2_image,text_boxes=textbox,debug=False)
        #return textbox


    
    def read(self,visualize = False):
        # 配置 Chrome WebDriver
        # 等待设定的加载时间（2 秒）
        time.sleep(1)
        print("reading...")
        self.current_url = self.driver.current_url
        # 获取页面的 HTML 快照
        page_source = self.driver.page_source
        annotations = None#self.annotation(visualize)
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(page_source, "html.parser")
        # 查找所有可交互元素，包括超链接和带有 alt 属性的图像
        interactive_elements = []
        count = 0
        for element in soup.find_all(["button", "input", "a", "textarea", "select", "img"]):
            try:
                # 获取元素的基本属性
                element_id = count
                xpath = get_xpath(element)
                try:
                    # 使用 Selenium 定位元素
                    selenium_element = self.driver.find_element(By.XPATH, xpath)
                    location = selenium_element.location
                    size = selenium_element.size
                    #print(location)
                    #print(size)
                except (NoSuchElementException, StaleElementReferenceException):
                    # 如果定位失败，location 和 size 设为 None
                    location = {'x': None, 'y': None}
                    size = {'width': None, 'height': None}
                aira_label = {attr: value for attr, value in element.attrs.items() if attr.startswith("aria-")}
                tag_name = element.name
                element_type = element.get("type")  # 元素的 type 属性，默认 link 对于 <a>
                alt_label = element.get("alt")  # 从 aria-label 或 alt 中获取 label
                element_text = element.get_text(strip=True) if tag_name != "img" else ""  # 获取非图片元素的内部文字
                element_href = element.get("href") if tag_name == "a" else None  # 如果是超链接，获取 href 属性
                # 判断是否为可交互元素或超链接、图片
                if (tag_name in ["button", "textarea", "select", "img"] or 
                (tag_name == "input" and element_type in ["text", "password", "checkbox", "radio", "submit", "button"]) or
                (tag_name == "a" and element_href)) or alt_label or aira_label:
                    if location["x"] == None or location["y"] == None or size["width"] == None or size["height"] == None:
                         continue;
                
                # 将元素添加到 interactive_elements 列表，包含 tag_name, element_type, label, element_text, element_href
                    interactive_elements.append({
                        "id":element_id,
                        "tag_name": tag_name,
                        "type": element_type,
                        "alt_label": alt_label,
                        "aria_label":aira_label,
                        "text": element_text,
                        "href": element_href,
                        "position":(int(location["x"] + size["width"]/2) , int(location["y"] + size["height"]/2))
                    })
                count +=1
                    
            except StaleElementReferenceException:
                continue
        
        full_page_text = soup.get_text(separator=" ", strip=True)
        #if visualize:
        self.current_webpage = interactive_elements
        return interactive_elements, annotations,full_page_text
        #return interactive_elements,full_page_text
    
    def close(self):
    # 保持页面打开以便查看效果
        # 关闭 WebDriver
        self.driver.quit()

    def click(self,id):
        #print(type(id))
        x,y = (self.current_webpage[id]["position"])
        self.click_position(x,y)

    def typing(self,id,text):
        x,y = (self.current_webpage[id]["position"])
        self.typing_position(x,y,text)

    def back(self):
        self.driver.back()

        

    def typing_position(self,x,y,text):
        action = ActionChains(self.driver)
        # 将鼠标移动到指定坐标并点击
        window_size = self.driver.get_window_size()
        window_width = window_size['width']
        window_height = window_size['height']
        #print(x,y,window_height,window_width)
        # 检查坐标是否在窗口范围内
        time.sleep(1)
        if x < 0 or x >= window_width or y < 0 or y >= window_height:
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds for window size ({window_width}, {window_height})")
        try:
            action.move_by_offset(x, y).click().perform()
            action.send_keys(text).send_keys(Keys.ENTER).perform()
        except MoveTargetOutOfBoundsException:
            # 捕获 MoveTargetOutOfBoundsException 异常
            print(f"Error: Target position ({x}, {y}) is out of bounds. Please adjust the coordinates or window size.")
        
        except WebDriverException as e:
            # 捕获其他 WebDriver 相关异常
            print(f"WebDriverException occurred: {str(e)}")
        
        finally:
            # 重置鼠标位置，防止影响后续操作
            action.move_by_offset(-x, -y).perform()
            print("Mouse position reset.")
            


        pass

    def click_position(self, x, y):
        """
        使用 Selenium 在浏览器窗口的特定位置点击。
        
        参数:
        - driver: Selenium WebDriver 实例
        - x: 要点击的 X 坐标
        - y: 要点击的 Y 坐标
        """
        # 创建 ActionChains 对象
        action = ActionChains(self.driver)
        # 将鼠标移动到指定坐标并点击
        try:
            # 将鼠标移动到指定坐标并点击
            action.move_by_offset(x, y).click().perform()
            print(f"Clicked at position ({x}, {y}) successfully.")
        
        except MoveTargetOutOfBoundsException:
            # 捕获 MoveTargetOutOfBoundsException 异常
            print(f"Error: Target position ({x}, {y}) is out of bounds. Please adjust the coordinates or window size.")
        
        except WebDriverException as e:
            # 捕获其他 WebDriver 相关异常
            print(f"WebDriverException occurred: {str(e)}")
        
        finally:
            # 重置鼠标位置，防止影响后续操作
            action.move_by_offset(-x, -y).perform()
            print("Mouse position reset.")

    def jumpto(self, url):
        self.driver.get(url)
        

    def response(text):
        print("Agent:" + text)




if __name__ == "__main__":
    web_reader = web_reader("https://www.google.com")
    print(web_reader.read())
    web_reader.click_position(994,18)
    time.sleep(2)

        

    

    






