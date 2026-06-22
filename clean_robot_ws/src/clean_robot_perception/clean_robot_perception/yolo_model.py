from ultralytics import YOLO

class YoloModel:

    def __init__(self):

        pass

    def detect(self, image):

        detections = []

        detections.append({

            "class_name": "bottle",

            "confidence": 0.92,

            "x": 100,

            "y": 120,

            "width": 80,

            "height": 120

        })

        return detections