import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import base64
import traceback

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def load_model(animal_type):
    try:
        model_path = f'{animal_type}.pt'  # 根据动物类型加载对应的模型
        model = YOLO(model_path)  # 确保模型路径正确
        logging.info(f"{animal_type.capitalize()} model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Failed to load {animal_type} model: %s", str(e))
        raise


@app.route('/predict/<animal_type>', methods=['POST'])  # 修改了这里以支持动物类型
def predict(animal_type):
    if animal_type not in ['cat', 'dog']:  # 验证动物类型
        return jsonify({'error': 'Invalid animal type'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # 使用 PIL 读取图像
        image = Image.open(file.stream).convert('RGB')

        # 转换为 NumPy 数组（OpenCV 格式）
        image_np = np.array(image)

        # BGR 格式转换为 RGB
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # 使用 OpenCV 处理图像（例如，调整大小）
        image_resized = cv2.resize(image_np, (640, 640))

        # 转换为 PIL 图像以供 YOLO 进行预测
        image_pil = Image.fromarray(cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB))

        # 根据动物类型加载模型
        model = load_model(animal_type)

        # 使用 YOLO 模型进行预测
        results = model(image_pil)  # 使用 ultralytics 模型进行预测

        logging.debug("Model output: %s", results)

        # 获取检测结果
        detections = results[0]  # 获取第一张图像的检测结果

        # 绘制检测框
        predictions = []
        for result in detections.boxes:
            boxes = result.xyxy.tolist()  # 获取边框坐标
            confs = result.conf.tolist()  # 获取置信度
            clss = result.cls.tolist()  # 获取类别索引

            for box, conf, cls in zip(boxes, confs, clss):
                # 将边框坐标从 YOLO 格式转换为 OpenCV 格式
                x1, y1, x2, y2 = [int(coord) for coord in box]
                # 绘制矩形框
                cv2.rectangle(image_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 在图像上绘制类别和置信度
                label = f"{model.names[int(cls)]} {conf:.2f}"
                cv2.putText(image_resized, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 将预测结果添加到列表中
                predictions.append({
                    'class': model.names[int(cls)],
                    'confidence': float(conf),
                    'box': [x1, y1, x2, y2]
                })

        # 将处理后的图像转换为 PIL 图像以便于保存
        image_with_boxes = Image.fromarray(cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB))

        # 保存处理后的图像到 BytesIO 对象
        buffered = io.BytesIO()
        image_with_boxes.save(buffered, format="JPEG")
        buffered.seek(0)

        # 将图像转换为 Base64 编码
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 返回预测结果和处理后的图像
        response = {
            'predictions': predictions,
            'image': img_base64  # 返回图像的 Base64 编码
        }

        return jsonify(response)

    except Exception as e:
        logging.error("Error occurred: %s", str(e))
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)