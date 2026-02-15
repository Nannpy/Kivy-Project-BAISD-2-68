import cv2
import numpy as np
from collections import Counter

class YOLODetector:
    """Class สำหรับจัดการระบบตรวจจับวัตถุด้วยโมเดล YOLOv8"""

    def __init__(self, model_path='yolov8n.pt'):
        """เริ่มต้นโหลดโมเดล AI เมื่อเรียกใช้งาน Class"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path) # โหลดไฟล์ Weight ของโมเดล (.pt)
            self.enabled = True
            print(f"load model done: {model_path}")
        except ImportError:
            # กรณีที่ยังไม่ได้ติดตั้ง Library ultralytics
            print("Can't import ultralytics, plese type this first pip install ultralytics")
            self.enabled = False
        except Exception as e:
            # กรณีโหลดไฟล์โมเดลไม่สำเร็จ
            print(f"Can't load model: {e}")
            self.enabled = False
    
    def detect_from_image(self, image_path, confidence=0.5):
        """ฟังก์ชันตรวจจับวัตถุจากไฟล์รูปภาพ (ใช้ในหน้า Scan)"""
        if not self.enabled:
            return self._mock_detection()
        
        try:
            # ส่งรูปภาพให้โมเดลประมวลผลตามค่าความเชื่อมั่น (confidence) ที่กำหนด
            results = self.model(image_path, conf=confidence)
            
            # เก็บชื่อวัตถุที่ตรวจจับได้ลงใน List
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0]) # รหัสคลาสสินค้า
                    class_name = result.names[class_id] # แปลงรหัสเป็นชื่อสินค้า
                    detected_objects.append(class_name)
            
            # สรุปจำนวนวัตถุแต่ละชนิดโดยใช้ Counter
            object_counts = Counter(detected_objects)
            
            return dict(object_counts) # คืนค่าเป็น Dictionary เช่น {'Milk': 2, 'Bread': 1}
            
        except Exception as e:
            print(f"detection error: {e}")
            return self._mock_detection()
    
    def detect_from_camera(self, frame, confidence=0.5):
        """ฟังก์ชันตรวจจับวัตถุจากเฟรมวิดีโอแบบ Real-time"""
        if not self.enabled:
            return frame, self._mock_detection()
        
        try:
            # ประมวลผลภาพจากเฟรมกล้อง
            results = self.model(frame, conf=confidence)
            
            # วาดกรอบสี่เหลี่ยม (Bounding Box) และชื่อคลาสลงบนภาพ
            annotated_frame = results[0].plot()
            
            # วนลูปนับจำนวนวัตถุที่พบในเฟรม
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    detected_objects.append(class_name)
            
            object_counts = Counter(detected_objects)
            
            # คืนค่าทั้งภาพที่วาดกรอบแล้ว และจำนวนสินค้าที่นับได้
            return annotated_frame, dict(object_counts)
            
        except Exception as e:
            print(f"detection error: {e}")
            return frame, self._mock_detection()
import cv2
import numpy as np
from collections import Counter

class YOLODetector:
    """Class สำหรับจัดการระบบตรวจจับวัตถุด้วยโมเดล YOLOv8"""

    def __init__(self, model_path='yolov8n.pt'):
        """เริ่มต้นโหลดโมเดล AI เมื่อเรียกใช้งาน Class"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path) # โหลดไฟล์ Weight ของโมเดล (.pt)
            self.enabled = True
            print(f"load model done: {model_path}")
        except ImportError:
            # กรณีที่ยังไม่ได้ติดตั้ง Library ultralytics
            print("Can't import ultralytics, plese type this first pip install ultralytics")
            self.enabled = False
        except Exception as e:
            # กรณีโหลดไฟล์โมเดลไม่สำเร็จ
            print(f"Can't load model: {e}")
            self.enabled = False
    
    def detect_from_image(self, image_path, confidence=0.5):
        """ฟังก์ชันตรวจจับวัตถุจากไฟล์รูปภาพ (ใช้ในหน้า Scan)"""
        if not self.enabled:
            return self._mock_detection()
        
        try:
            # ส่งรูปภาพให้โมเดลประมวลผลตามค่าความเชื่อมั่น (confidence) ที่กำหนด
            results = self.model(image_path, conf=confidence)
            
            # เก็บชื่อวัตถุที่ตรวจจับได้ลงใน List
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0]) # รหัสคลาสสินค้า
                    class_name = result.names[class_id] # แปลงรหัสเป็นชื่อสินค้า
                    detected_objects.append(class_name)
            
            # สรุปจำนวนวัตถุแต่ละชนิดโดยใช้ Counter
            object_counts = Counter(detected_objects)
            
            return dict(object_counts) # คืนค่าเป็น Dictionary เช่น {'Milk': 2, 'Bread': 1}
            
        except Exception as e:
            print(f"detection error: {e}")
            return self._mock_detection()
    
    def detect_from_camera(self, frame, confidence=0.5):
        """ฟังก์ชันตรวจจับวัตถุจากเฟรมวิดีโอแบบ Real-time"""
        if not self.enabled:
            return frame, self._mock_detection()
        
        try:
            # ประมวลผลภาพจากเฟรมกล้อง
            results = self.model(frame, conf=confidence)
            
            # วาดกรอบสี่เหลี่ยม (Bounding Box) และชื่อคลาสลงบนภาพ
            annotated_frame = results[0].plot()
            
            # วนลูปนับจำนวนวัตถุที่พบในเฟรม
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    detected_objects.append(class_name)
            
            object_counts = Counter(detected_objects)
            
            # คืนค่าทั้งภาพที่วาดกรอบแล้ว และจำนวนสินค้าที่นับได้
            return annotated_frame, dict(object_counts)
            
        except Exception as e:
            print(f"detection error: {e}")
            return frame, self._mock_detection()
    
    def detect_custom_objects(self, image_path, custom_model_path, confidence=0.5):
        """ฟังก์ชันพิเศษสำหรับเลือกโหลดโมเดลอื่นๆ มาใช้ตรวจจับเฉพาะกิจ"""
        try:
            from ultralytics import YOLO
            custom_model = YOLO(custom_model_path)
            
            results = custom_model(image_path, conf=confidence)
            
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    detected_objects.append(class_name)
            
            object_counts = Counter(detected_objects)
            
            return dict(object_counts)
            
        except Exception as e:
            print(f"An error occurred when using the custom model: {e}")
            return self._mock_detection()
    
