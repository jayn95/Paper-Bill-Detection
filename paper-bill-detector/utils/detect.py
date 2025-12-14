from ultralytics import YOLO
from PIL import Image

CONF_THRESHOLD = 0.5

class BillDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect(self, image: Image.Image):
        """
        Run YOLOv8 inference and return detected bill classes.
        Returns a list of class names (e.g., ['100', '50']).
        """
        results = self.model(image, conf=CONF_THRESHOLD)
        detected_classes = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                detected_classes.append(cls_name)

        return detected_classes
