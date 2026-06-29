from ultralytics import YOLO

from .image_utils import ImageUtils


class YoloModel:

    def __init__(
        self,
        model_path='yolov8n.pt',
        confidence_threshold=0.35,
        target_classes=None
    ):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.target_classes = {
            name.strip().lower()
            for name in (target_classes or [])
            if name.strip()
        }

    def detect(self, image_msg):
        frame = ImageUtils.to_bgr8(image_msg)

        predictions = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            verbose=False
        )

        detections = []
        for prediction in predictions:
            names = prediction.names or self.model.names
            if prediction.boxes is None:
                continue

            for box in prediction.boxes:
                class_id = int(box.cls[0].item())
                class_name = self._class_name(names, class_id)
                if (
                    self.target_classes
                    and class_name.lower() not in self.target_classes
                ):
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    'class_name': class_name,
                    'confidence': float(box.conf[0].item()),
                    'x': int(round(x1)),
                    'y': int(round(y1)),
                    'width': max(0, int(round(x2 - x1))),
                    'height': max(0, int(round(y2 - y1))),
                })

        return detections

    @staticmethod
    def _class_name(names, class_id):
        if isinstance(names, dict):
            return str(names.get(class_id, class_id))

        if 0 <= class_id < len(names):
            return str(names[class_id])

        return str(class_id)
