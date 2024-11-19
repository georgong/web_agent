import numpy as np
#import cv2
#import pytesseract
#from sklearn.cluster import KMeans
import math
import random


def image_read(image,debug=False):
    image = image.copy()
    height,width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # OCR 识别文本区域
    detection_boxes = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    text_boxes = []
    for i in range(len(detection_boxes['text'])):
        if int(detection_boxes['conf'][i]) > 60:  # 过滤低置信度的检测结果
            x, y, w, h = (detection_boxes['left'][i], detection_boxes['top'][i],
                          detection_boxes['width'][i], detection_boxes['height'][i])
            text_boxes.append((x, y, w, h))

    # 合并密集排列的文本框为 text_line
    text_lines = []
    visited_text = [False] * len(text_boxes)

    for i in range(len(text_boxes)):
        if visited_text[i]:
            continue
        x1, y1, w1, h1 = text_boxes[i]
        merged_x, merged_y, merged_w, merged_h = x1, y1, w1, h1
        merged = False

        for j in range(i + 1, len(text_boxes)):
            x2, y2, w2, h2 = text_boxes[j]
            if abs(y1 - y2) < 5 and abs((merged_x + merged_w) - x2) < 10:
                merged_x = min(merged_x, x2)
                merged_y = min(merged_y, y2)
                merged_w = max(merged_x + merged_w, x2 + w2) - merged_x
                merged_h = max(merged_y + merged_h, y2 + h2) - merged_y
                visited_text[j] = True
                merged = True

        if merged:
            text_lines.append((merged_x, merged_y, merged_w, merged_h))
        else:
            cv2.rectangle(image, (merged_x, merged_y), (merged_x + merged_w, merged_y + merged_h), (0, 0, 255), 2)
            cv2.putText(image, "text", (merged_x, merged_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # 将垂直间距相似的 text_line 合并为 text_area
    text_areas = []
    visited_lines = [False] * len(text_lines)

    for i in range(len(text_lines)):
        if visited_lines[i]:
            continue
        x1, y1, w1, h1 = text_lines[i]
        area_x, area_y, area_w, area_h = x1, y1, w1, h1

        for j in range(i + 1, len(text_lines)):
            x2, y2, w2, h2 = text_lines[j]
            vertical_spacing = abs(y2 - (area_y + area_h))
            if vertical_spacing < 10 and abs(area_x - x2) < 5:
                area_x = min(area_x, x2)
                area_y = min(area_y, y2)
                area_w = max(area_x + area_w, x2 + w2) - area_x
                area_h = max(area_y + area_h, y2 + h2) - area_y
                visited_lines[j] = True

        text_areas.append((area_x, area_y, area_w, area_h))

    # 分割背景和前景（图标检测）
    reshaped_img = gray.reshape(-1, 1)
    kmeans = KMeans(n_clusters=2).fit(reshaped_img)
    clustered_img = kmeans.labels_.reshape(gray.shape)

    # 找出前景区域并检测可能的图标
    contours, _ = cv2.findContours(clustered_img.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    icon_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # 检查该 icon 是否在 text_areas 或 text_lines 内部
        inside_text_area = any((x >= bx and x + w <= bx + bw and y >= by and y + h <= by + bh) for (bx, by, bw, bh) in text_areas)
        inside_text_line = any((x >= bx and x + w <= bx + bw and y >= by and y + h <= by + bh) for (bx, by, bw, bh) in text_lines)
        inside_text_box = any((x >= bx and x + w <= bx + bw and y >= by and y + h <= by + bh) for (bx, by, bw, bh) in text_boxes)

        if w * h > 50 and not inside_text_area and not inside_text_line and not inside_text_box:
            icon_boxes.append((x, y, w, h))

    # 将所有 text_areas, text_lines 和 icon_boxes 组合
    all_components = text_areas + text_lines + icon_boxes

    for (x, y, w, h) in text_boxes:
        inside_any_area_or_line = any((x >= bx and x + w <= bx + bw and y >= by and y + h <= by + bh) 
                                      for (bx, by, bw, bh) in text_areas + text_lines)
        if not inside_any_area_or_line:
            all_components.append((x, y, w, h))

    # 标注小组件区域（先标注，避免覆盖）
    for (x, y, w, h) in text_areas:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(image, "text_area", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    for (x, y, w, h) in text_lines:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(image, "text_line", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    for (x, y, w, h) in icon_boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, "icon", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 找出具有相同 y 轴且 x 间距相等的组件组，满足一定大小要求
    grouped_rectangles = []
    for i in range(len(all_components)):
        for j in range(i + 1, len(all_components)):
            (x1, y1, w1, h1) = all_components[i]
            (x2, y2, w2, h2) = all_components[j]

            y_aligned = abs(y1 - y2) < 10 or abs((y1 + h1 // 2) - (y2 + h2 // 2)) < 5
            x_distance = abs((x1 + w1) - x2)
            if y_aligned and x_distance < 20:
                min_x = min(x1, x2)
                min_y = min(y1, y2)
                max_x = max(x1 + w1, x2 + w2)
                max_y = max(y1 + h1, y2 + h2)
                rect_w = max_x - min_x
                rect_h = max_y - min_y
                if rect_w >= width / 2 or rect_h >= height / 2:
                    grouped_rectangles.append((min_x, min_y, rect_w, rect_h))

    # 绘制符合大小要求的矩形框
    for (x, y, w, h) in grouped_rectangles:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(image, "rectangle", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    # 显示标注后的图像
    if debug:
        cv2.imshow("final_img", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        return all_components, grouped_rectangles
    

def annotate_text_centers(image, text_boxes, debug=False):
    min_distance = 30
    label_distance = 60
    max_offset=40
    # 深拷贝原始图像，避免直接修改
    annotated_image = image.copy()
    overlay = image.copy()
    overlay[:, :] = (255, 255, 255)
    annotated_image = cv2.addWeighted(overlay, 0.5, annotated_image, 1 - 0.5, 0)
    text_boxes = [i for i in text_boxes if len(i) == 4]
    used_positions = []
    used_centers = []


    # 遍历每个文本框，计算中心点并绘制到图像上
    for (x, y, w, h) in text_boxes:
        # 计算中心点
        center_x = x + w // 2
        center_y = y + h // 2

        # 检查是否有足够远的注释存在
        if any(math.sqrt((center_x - ux) ** 2 + (center_y - uy) ** 2) < min_distance for ux, uy in used_centers):
            continue  # 如果有较近的注释，则跳过当前注释

        # 随机生成偏移位置
        count = 0
        while True:
            offset_x = random.randint(-max_offset, max_offset)
            offset_y = random.randint(-max_offset, max_offset)
            label_x = center_x + offset_x
            label_y = center_y + offset_y
            count += 1
            if label_x < 20 or label_y < 20 or label_x > image.shape[1] - 10 or label_y > image.shape[0] - 10:
                count -=1 
                break;
            if not any(math.sqrt((label_x - ux) ** 2 + (label_y - uy) ** 2) < label_distance for ux, uy in used_positions) or count > 5: 
                break;

        

        # 标记已使用的位置
        used_positions.append((label_x, label_y))
        used_centers.append((center_x, center_y))

        # 绘制箭头指向中心点
        cv2.arrowedLine(annotated_image, (label_x, label_y), (center_x, center_y), (255, 0, 0), 1, tipLength=0.1)

        # 在偏移位置绘制注释
        cv2.putText(annotated_image, f"Center ({center_x}, {center_y})", (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Debug 模式下显示图像
    if debug:
        cv2.imshow("Annotated Image with Text Centers", annotated_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # 返回标注后的图像
    return annotated_image



    

if __name__ == "__main__":
    image = cv2.imread('ui_image2.png')
    height, width = image.shape[:2]
    textboxes = image_read(image,debug = False)[0]
    annotate_text_centers(image, textboxes, debug=True)

    

    






