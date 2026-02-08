from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

import cv2
from ultralytics import YOLO
from collections import Counter

MODEL_PATH = '/Users/nannam/Downloads/kivy_project/yolov8n.pt'   # <<< แก้ตรงนี้
CONF_THRESHOLD = 0.5

class VisionEngine:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def run_inference(self, image_path):
        results = self.model(image_path, conf=0.4)
        detections = results[0].boxes.cls.tolist()

        names = self.model.names
        labels = [names[int(i)] for i in detections]

        return dict(Counter(labels))


class SmartPOS(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # -------- Vision --------
        self.vision = VisionEngine('/Users/nannam/Downloads/kivy_project/yolov8n.pt')

        # -------- UI --------
        self.result_label = Label(
            text="Scan Result\n\nWaiting...",
            halign="center",
            valign="middle",
            font_size=22
        )
        self.result_label.bind(size=self.result_label.setter("text_size"))
        self.add_widget(self.result_label)

        btn_layout = BoxLayout(size_hint_y=0.2)

        self.scan_btn = Button(text="Scan Product")
        self.confirm_btn = Button(text="Confirm")
        self.cancel_btn = Button(text="Cancel")

        self.scan_btn.bind(on_press=self.scan_product)
        self.confirm_btn.bind(on_press=self.on_confirm)
        self.cancel_btn.bind(on_press=self.on_cancel)

        btn_layout.add_widget(self.scan_btn)
        btn_layout.add_widget(self.confirm_btn)
        btn_layout.add_widget(self.cancel_btn)

        self.add_widget(btn_layout)

        # -------- Auto Scan (Demo) --------  # Removed auto scan

    def scan_product(self, instance=None):
        # For demo, since no image, use dummy result
        result = {'apple': 1, 'banana': 2}  # Dummy detection result
        self.update_result_ui(result)

    def update_result_ui(self, result_dict):
        if not result_dict:
            self.result_label.text = "Scan Result\n\nNo product detected"
            return

        text = "Scan Result\n\n"
        for k, v in result_dict.items():
            text += f"{k} : {v}\n"

        self.result_label.text = text

    def on_confirm(self, instance):
        print("Confirmed")

    def on_cancel(self, instance):
        self.result_label.text = "Scan Result\n\nCancelled"


class SmartPOSApp(App):
    def build(self):
        return SmartPOS()


if __name__ == "__main__":
    SmartPOSApp().run()
