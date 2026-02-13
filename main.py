from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from datetime import datetime
import json
import os

# ตั้งค่าขนาดหน้าจอ
Window.size = (400, 700)

class StockData:
    """จัดการข้อมูลสต็อก"""
    def __init__(self):
        self.filename = 'stock_data.json'
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_record(self, product_name, count):
        record = {
            'product_name': product_name,
            'count': count,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.data.append(record)
        self.save_data()
    
    def get_all_records(self):
        return self.data
    
    def get_summary(self):
        """สรุปข้อมูลสำหรับกราฟ"""
        summary = {}
        for record in self.data:
            name = record['product_name']
            count = record['count']
            if name in summary:
                summary[name] += count
            else:
                summary[name] = count
        return summary
    
    def get_daily_summary(self):
        """สรุปข้อมูลจำนวนรวมรายวัน (แกน X: วัน, แกน Y: จำนวน)"""
        daily_summary = {}
        for record in self.data:
            # ดึงเฉพาะวันที่ (YYYY-MM-DD)
            date = record['timestamp'].split(' ')[0]
            count = record['count']
            daily_summary[date] = daily_summary.get(date, 0) + count
        # เรียงลำดับวันที่
        return dict(sorted(daily_summary.items()))
    
    def get_product_daily_trends(self):
        """สรุปข้อมูลแยกตามสินค้าและวันที่ {product: {date: total_count}}"""
        trends = {}
        for record in self.data:
            date = record['timestamp'].split(' ')[0]
            name = record['product_name']
            count = record['count']
            
            if name not in trends:
                trends[name] = {}
            trends[name][date] = trends[name].get(date, 0) + count
            
        for name in trends:
            trends[name] = dict(sorted(trends[name].items()))
        return trends


class HamburgerMenu(BoxLayout):
    """เมนู hamburger"""
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.size_hint = (0.7, 1)
        self.pos_hint = {'left': 0, 'top': 1}
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # หัวข้อเมนู
        header = Label(
            text='Menu',
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True,
            color=(0, 0, 0, 1)
        )
        self.add_widget(header)
        
        # ปุ่มเมนู
        menu_items = [
            ('Home', 'camera'),
            ('Stock', 'stock'),
            ('Analytics', 'analytics')
        ]
        
        for text, screen_name in menu_items:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=50,
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1),
                font_size='16sp'
            )
            btn.bind(on_press=lambda x, s=screen_name: self.go_to_screen(s))
            self.add_widget(btn)
        
        # เว้นที่ว่าง
        self.add_widget(Label())
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_to_screen(self, screen_name):
        self.screen_manager.current = screen_name
        self.parent.remove_widget(self)


class CameraScreen(Screen):
    """หน้าจอกล้องสำหรับนับสต็อก"""
    def __init__(self, stock_data, yolo_detector=None, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        self.yolo_detector = yolo_detector
        self.menu_open = False
        
        layout = FloatLayout()
        
        # พื้นหลัง
        with layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=60,
            pos_hint={'top': 1}
        )
        
        with header.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        # ปุ่ม hamburger
        # hamburger_btn = Button(
        #     text='☰',
        #     size_hint=(None, 1),
        #     width=60,
        #     background_color=(0.2, 0.6, 1, 1),
        #     font_size='30sp',
        #     color=(1, 1, 1, 1)
        # )
        # hamburger_btn.bind(on_press=self.toggle_menu)
        
        # ปุ่ม hamburger รูปภาพ
        hamburger_btn = Button(
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'center_y': 0.5, 'x': 0.05},
            background_normal='/Users/nannam/Downloads/project2/hamburger.png',  # ใส่พาธรูปไอคอนเมนูของคุณ
            background_down='menu_icon_pressed.png' # (Optional) รูปตอนกด
        )
        hamburger_btn.bind(on_press=self.toggle_menu)
        
        app_title = Label(
            text='Stock Counter AI',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        header.add_widget(hamburger_btn)
        header.add_widget(app_title)
        
        # กล่องสำหรับแสดงกล้อง
        camera_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, None),
            height=600,
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        
        # สร้างกล้อง
        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint=(1, 1),
            index=-1
        )
        
        camera_box.add_widget(self.camera)
        
        # ปุ่มถ่ายรูป
        # capture_btn = Button(
        #     size_hint=(None, None),
        #     size=(80, 80),
        #     pos_hint={'center_x': 0.5, 'y': 0.28},
        #     background_normal='',
        #     background_color=(0.2, 0.6, 1, 1)
        # )
        # capture_btn.bind(on_press=self.capture_and_detect)
        
        # สร้างปุ่มถ่ายรูป
        capture_btn = Button(
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            background_normal='/Users/nannam/Downloads/project2/camera.png', # รูปปุ่มชัตเตอร์
            background_down='/Users/nannam/Downloads/project2/camera.png',
            border=(0, 0, 0, 0) # ลบขอบปุ่ม Kivy แบบเดิมออก
        )
        capture_btn.bind(on_press=self.capture_and_detect)
        
        # วาดวงกลมปุ่ม
        with capture_btn.canvas.before:
            from kivy.graphics import Ellipse
            Color(1, 1, 1, 1)
            
        camera_icon = Label(
            text='📷',
            font_size='40sp',
            pos_hint={'center_x': 0.5, 'y': 0.28}
        )
        
        # ปุ่มสลับกล้อง (สำหรับมือถือ)
        # switch_btn = Button(
        #     text='🔄',
        #     size_hint=(None, None),
        #     size=(50, 50),
        #     pos_hint={'right': 0.95, 'y': 0.28},
        #     background_color=(0.3, 0.3, 0.3, 0.7),
        #     font_size='25sp'
        # )
        # switch_btn.bind(on_press=self.switch_camera)
        
        # สร้างปุ่มถ่ายรูป
        switch_btn = Button(
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'right': 0.95, 'y': 0.28},
            background_normal='/Users/nannam/Downloads/project2/arrow.png', # รูปปุ่มชัตเตอร์
            background_down='/Users/nannam/Downloads/project2/arrow.png',
            border=(0, 0, 0, 0) # ลบขอบปุ่ม Kivy แบบเดิมออก
        )
        switch_btn.bind(on_press=self.switch_camera)
        
        # ผลลัพธ์
        self.result_label = Label(
            text='Press the camera button to count the stock.',
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.1},
            color=(0, 0, 0, 1),
            font_size='14sp'
        )
        
        # สถานะ YOLO
        self.status_label = Label(
            text='',
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'y': 0.05},
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp'
        )
        
        layout.add_widget(header)
        layout.add_widget(camera_box)
        layout.add_widget(capture_btn)
        layout.add_widget(camera_icon)
        layout.add_widget(switch_btn)
        layout.add_widget(self.result_label)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
        self.layout = layout
        
        # ตรวจสอบ YOLO
        self.check_yolo_status()
    
    def check_yolo_status(self):
        """ตรวจสอบสถานะ YOLO"""
        if self.yolo_detector and self.yolo_detector.enabled:
            self.status_label.text = 'Model ready for detection'
            self.status_label.color = (0, 0.7, 0, 1)
        else:
            self.status_label.text = 'Model not ready'
            self.status_label.color = (0.8, 0.5, 0, 1)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def toggle_menu(self, instance):
        if not self.menu_open:
            menu = HamburgerMenu(screen_manager=self.manager)
            self.layout.add_widget(menu)
            self.menu_open = True
        else:
            # ลบเมนูถ้ามีอยู่
            for child in self.layout.children[:]:
                if isinstance(child, HamburgerMenu):
                    self.layout.remove_widget(child)
            self.menu_open = False
    
    def switch_camera(self, instance):
        """สลับกล้องหน้า-หลัง"""
        try:
            current_index = self.camera.index
            self.camera.index = 1 if current_index == 0 else 0
            print(f"สลับไปกล้อง: {self.camera.index}")
        except Exception as e:
            print(f"ไม่สามารถสลับกล้องได้: {e}")
    
    def capture_and_detect(self, instance):
        """ถ่ายรูปและตรวจจับด้วย YOLO"""
        self.result_label.text = 'Processing...'
        self.result_label.color = (0, 0.5, 1, 1)
        
        # ใช้ Clock เพื่อให้ UI อัพเดท
        Clock.schedule_once(self._process_detection, 0.1)
    
    def _process_detection(self, dt):
        """ประมวลผลการตรวจจับ"""
        try:
            # จับภาพจากกล้อง
            image_path = self.save_camera_image()
            
            if image_path:
                # ใช้ YOLO ตรวจจับ
                if self.yolo_detector:
                    results = self.yolo_detector.detect_from_image(image_path)
                else:
                    # โหมดทดสอบ
                    results = self._mock_detection()
                
                # แสดงผลลัพธ์
                self.display_results(results)
                
                # ลบไฟล์ชั่วคราว
                if os.path.exists(image_path):
                    os.remove(image_path)
            else:
                self.result_label.text = 'ไม่สามารถจับภาพได้'
                self.result_label.color = (1, 0, 0, 1)
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            self.result_label.text = f'เกิดข้อผิดพลาด: {str(e)}'
            self.result_label.color = (1, 0, 0, 1)
    
    def save_camera_image(self):
        """บันทึกภาพจากกล้อง"""
        try:
            texture = self.camera.texture
            if texture is None:
                return None
            
            # บันทึกเป็นไฟล์ชั่วคราว
            filename = 'temp_capture.png'
            texture.save(filename)
            return filename
            
        except Exception as e:
            print(f"ไม่สามารถบันทึกภาพได้: {e}")
            return None
    
    def display_results(self, results):
        """แสดงผลลัพธ์การตรวจจับ"""
        if not results:
            self.result_label.text = 'Product not found'
            self.result_label.color = (0.7, 0.7, 0.7, 1)
            return
        
        # สร้างข้อความผลลัพธ์
        result_text = []
        total_items = 0
        
        for product_name, count in results.items():
            result_text.append(f"{product_name}: {count}")
            total_items += count
            
            # บันทึกลงฐานข้อมูล
            self.stock_data.add_record(product_name, count)
        
        # แสดงผล
        self.result_label.text = f"detected {total_items} items - " + ", ".join(result_text)
        self.result_label.color = (0, 0.7, 0, 1)
    
    def _mock_detection(self):
        """จำลองผลลัพธ์สำหรับทดสอบ"""
        import random
        products = ['ขนมปัง', 'นม', 'น้ำอัดลม', 'ขนมขบเคี้ยว']
        
        # สุ่ม 1-3 ประเภทสินค้า
        num_products = random.randint(1, 3)
        results = {}
        
        for _ in range(num_products):
            product = random.choice(products)
            if product not in results:
                results[product] = random.randint(1, 5)
        
        return results


class StockListScreen(Screen):
    """หน้าจอแสดงรายการสต็อก"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=60
        )
        
        with header.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        back_btn = Button(
            text='←',
            size_hint=(None, 1),
            width=60,
            background_color=(0.2, 0.6, 1, 1),
            font_size='30sp',
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title = Label(
            text='Stock List',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # รายการสต็อก
        scroll = ScrollView(size_hint=(1, 1))
        self.stock_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.stock_list.bind(minimum_height=self.stock_list.setter('height'))
        
        scroll.add_widget(self.stock_list)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        # โหลดข้อมูล
        self.bind(on_enter=self.load_stock_data)
    
    def update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def go_back(self, instance):
        self.manager.current = 'camera'
    
    def load_stock_data(self, *args):
        """โหลดและแสดงข้อมูลสต็อก"""
        self.stock_list.clear_widgets()
        
        records = self.stock_data.get_all_records()
        
        if not records:
            label = Label(
                text='ยังไม่มีข้อมูลสต็อก',
                size_hint_y=None,
                height=50,
                color=(0.5, 0.5, 0.5, 1)
            )
            self.stock_list.add_widget(label)
        else:
            for record in reversed(records):  # แสดงข้อมูลล่าสุดก่อน
                item = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=80,
                    padding=10
                )
                
                with item.canvas.before:
                    Color(0.95, 0.95, 0.95, 1)
                    item.rect = Rectangle(pos=item.pos, size=item.size)
                
                item.bind(pos=lambda i, v, r=item: setattr(r.rect, 'pos', i.pos),
                         size=lambda i, v, r=item: setattr(r.rect, 'size', i.size))
                
                name_label = Label(
                    text=f"{record['product_name']} : {record['count']}",
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=30,
                    halign='left',
                    valign='middle'
                )
                name_label.bind(size=name_label.setter('text_size'))
                
                time_label = Label(
                    text=record['timestamp'],
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=20,
                    font_size='12sp',
                    halign='left',
                    valign='middle'
                )
                time_label.bind(size=time_label.setter('text_size'))
                
                item.add_widget(name_label)
                item.add_widget(time_label)
                
                self.stock_list.add_widget(item)

class AnalyticsScreen(Screen):
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        self.selected_product = None # เก็บชื่อสินค้าที่กำลังดู
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Main Layout
        self.main_layout = BoxLayout(orientation='vertical')
        
        # --- Header ---
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        with header.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        back_btn = Button(text='< Back', size_hint_x=None, width=80, background_color=(0,0,0,0), color=(0.2, 0.6, 1, 1), bold=True)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
        
        header.add_widget(back_btn)
        header.add_widget(Label(text='PRODUCT ANALYSIS', font_size='18sp', bold=True))
        header.add_widget(Label(size_hint_x=None, width=80))
        self.main_layout.add_widget(header)

        # --- Product Selector (Scrollable Buttons) ---
        self.selector_area = ScrollView(size_hint_y=None, height=60, do_scroll_x=True, do_scroll_y=False)
        self.product_list = BoxLayout(orientation='horizontal', size_hint_x=None, padding=10, spacing=10)
        self.product_list.bind(minimum_width=self.product_list.setter('width'))
        self.selector_area.add_widget(self.product_list)
        self.main_layout.add_widget(self.selector_area)

        # --- Chart Display Area ---
        self.chart_container = FloatLayout()
        self.main_layout.add_widget(self.chart_container)
        
        self.add_widget(self.main_layout)
        self.bind(on_enter=self.update_product_menu)

    def _update_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def update_header(self, i, v): self.header_rect.pos, self.header_rect.size = i.pos, i.size

    def update_product_menu(self, *args):
        """สร้างปุ่มเลือกสินค้าจากข้อมูลที่มีอยู่จริง"""
        self.product_list.clear_widgets()
        trends = self.stock_data.get_product_daily_trends()
        
        if not trends:
            self.chart_container.clear_widgets()
            self.chart_container.add_widget(Label(text='No data available', color=(0.5, 0.5, 0.5, 1)))
            return

        for product_name in trends.keys():
            btn = Button(
                text=product_name,
                size_hint=(None, 1),
                width=120,
                background_normal='',
                background_color=(0.2, 0.2, 0.2, 1) if product_name != self.selected_product else (0, 0.6, 1, 1)
            )
            btn.bind(on_press=lambda x, p=product_name: self.show_graph_for(p))
            self.product_list.add_widget(btn)
        
        # ถ้ายังไม่มีการเลือก ให้เลือกตัวแรกให้อัตโนมัติ
        if not self.selected_product and trends:
            self.show_graph_for(list(trends.keys())[0])

    def show_graph_for(self, product_name):
        """วาดกราฟเฉพาะสินค้าที่เลือก"""
        self.selected_product = product_name
        self.update_product_menu() # เพื่ออัปเดตสีปุ่มที่ถูกเลือก
        
        self.chart_container.clear_widgets()
        trends = self.stock_data.get_product_daily_trends()
        product_data = trends.get(product_name, {})
        
        if product_data:
            chart = self.create_single_line_chart(product_name, product_data)
            self.chart_container.add_widget(chart)

    def create_single_line_chart(self, name, data):
        dates = list(data.keys())
        counts = list(data.values())
        max_val = max(counts) if counts else 10
        
        container = BoxLayout(orientation='vertical', padding=[60, 20, 40, 60])
        plot_area = FloatLayout()
        
        from kivy.graphics import Line, Color as KColor, Ellipse

        def draw_plot(instance, value):
            plot_area.canvas.clear()
            w, h = instance.size
            x, y = instance.pos
            
            with plot_area.canvas:
                # วาด Grid และแกน Y
                KColor(0.2, 0.2, 0.2, 1)
                for i in range(6):
                    py = y + (h * (i/5) * 0.8)
                    Line(points=[x, py, x + w, py], width=1)
                
                # วาดเส้นกราฟ
                KColor(0, 0.8, 1, 1)
                x_step = w / (len(dates) - 1) if len(dates) > 1 else w
                points = []
                for i, count in enumerate(counts):
                    px = x + (i * x_step)
                    py = y + ((count / max_val) * h * 0.8)
                    points.extend([px, py])
                    Ellipse(pos=(px-5, py-5), size=(10, 10))
                
                if len(points) >= 4:
                    Line(points=points, width=3, joint='round')

        plot_area.bind(pos=draw_plot, size=draw_plot)
        
        # ใส่ตัวเลขแกน Y
        for i in range(6):
            val = int((max_val / 5) * i)
            plot_area.add_widget(Label(text=str(val), size_hint=(None, None), size=(40, 20),
                                      pos_hint={'x': -0.15, 'y': (i/5) * 0.8}, font_size='12sp'))

        # ใส่ชื่อสินค้าและวันที่
        container.add_widget(Label(text=f"Trend for: {name}", size_hint_y=None, height=40, bold=True, color=(0, 0.8, 1, 1)))
        container.add_widget(plot_area)
        
        x_labels = FloatLayout(size_hint_y=None, height=30)
        x_labels.add_widget(Label(text=dates[0], pos_hint={'x': 0, 'y': 0}, size_hint=(None, 1), font_size='10sp'))
        x_labels.add_widget(Label(text=dates[-1], pos_hint={'right': 1, 'y': 0}, size_hint=(None, 1), font_size='10sp'))
        container.add_widget(x_labels)

        return container

class StockCountApp(App):
    def build(self):
        # สร้างระบบจัดการข้อมูล
        self.stock_data = StockData()
        
        # โหลด YOLO detector
        print("กำลังโหลด YOLO detector...")
        try:
            from yolo_detector import YOLODetector
            # ใช้โมเดล YOLOv8n (เล็กและเร็ว)
            self.yolo_detector = YOLODetector('yolov8n.pt')
            print("โหลด YOLO สำเร็จ!")
        except Exception as e:
            print(f"ไม่สามารถโหลด YOLO: {e}")
            print("จะใช้โหมดทดสอบแทน")
            self.yolo_detector = None
        
        # สร้าง Screen Manager
        sm = ScreenManager()
        
        # เพิ่มหน้าจอต่างๆ
        sm.add_widget(CameraScreen(
            name='camera',
            stock_data=self.stock_data,
            yolo_detector=self.yolo_detector
        ))
        sm.add_widget(StockListScreen(name='stock', stock_data=self.stock_data))
        sm.add_widget(AnalyticsScreen(name='analytics', stock_data=self.stock_data))
        
        return sm


if __name__ == '__main__':
    StockCountApp().run()