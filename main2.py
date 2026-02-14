from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from datetime import datetime
import json
import os

# ตั้งค่าขนาดหน้าจอ
Window.size = (400, 700)

# --- สีมาตรฐานสำหรับทั้งแอป ---
COLOR_BG = (0.1, 0.1, 0.1, 1)      # พื้นหลังหลัก
COLOR_HEADER = (0.05, 0.05, 0.05, 1) # ส่วนหัว
COLOR_NEON_BLUE = (0, 0.7, 1, 1)   # ฟ้า Neon
COLOR_TEXT_DIM = (0.6, 0.6, 0.6, 1) # ข้อความรอง
COLOR_CARD = (0.15, 0.15, 0.15, 1) # พื้นหลังรายการสินค้า

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
    
    def get_product_daily_trends(self):
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
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.size_hint = (0.7, 1)
        self.pos_hint = {'left': 0, 'top': 1}
        
        with self.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        header = Label(text='MENU', size_hint_y=None, height=80, font_size='22sp', bold=True, color=COLOR_NEON_BLUE)
        self.add_widget(header)
        
        menu_items = [('CAMERA', 'camera'), ('STOCK LIST', 'stock'), ('ANALYTICS', 'analytics')]
        for text, screen_name in menu_items:
            btn = Button(text=text, size_hint_y=None, height=60, background_normal='', background_color=(0,0,0,0), color=(1,1,1,1))
            btn.bind(on_press=lambda x, s=screen_name: self.go_to_screen(s))
            self.add_widget(btn)
        self.add_widget(Label())

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_screen(self, screen_name):
        self.screen_manager.current = screen_name
        self.parent.remove_widget(self)

class CameraScreen(Screen):
    def __init__(self, stock_data, yolo_detector=None, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        self.yolo_detector = yolo_detector
        self.menu_open = False
        
        layout = FloatLayout()
        with layout.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60, pos_hint={'top': 1})
        with header.canvas.before:
            Color(*COLOR_HEADER)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        hamburger_btn = Button(size_hint=(None, None), size=(45, 45), pos_hint={'center_y': 0.5, 'x': 0.05}, 
                              background_normal='/Users/nannam/Downloads/project2/hamburger.png')
        hamburger_btn.bind(on_press=self.toggle_menu)
        
        app_title = Label(text='STOCK COUNTER AI', font_size='18sp', bold=True, color=(1, 1, 1, 1))
        header.add_widget(hamburger_btn)
        header.add_widget(app_title)
        
        self.camera = Camera(play=True, resolution=(640, 480), size_hint=(0.9, 0.65), pos_hint={'center_x': 0.5, 'top': 0.88}, index=-1)
        
        capture_btn = Button(size_hint=(None, None), size=(85, 85), pos_hint={'center_x': 0.5, 'y': 0.12},
                            background_normal='/Users/nannam/Downloads/project2/camera.png')
        capture_btn.bind(on_press=self.capture_and_detect)
        
        switch_btn = Button(size_hint=(None, None), size=(50, 50), pos_hint={'right': 0.95, 'y': 0.14},
                           background_normal='/Users/nannam/Downloads/project2/arrow.png')
        switch_btn.bind(on_press=self.switch_camera)
        
        self.result_label = Label(text='Ready to scan', size_hint=(1, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.06}, 
                                 color=COLOR_NEON_BLUE, font_size='14sp', bold=True)
        
        layout.add_widget(header)
        layout.add_widget(self.camera)
        layout.add_widget(capture_btn)
        layout.add_widget(switch_btn)
        layout.add_widget(self.result_label)
        self.add_widget(layout)
        self.layout = layout

    def update_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def update_header(self, i, v): self.header_rect.pos, self.header_rect.size = i.pos, i.size
    def toggle_menu(self, instance):
        if not self.menu_open:
            menu = HamburgerMenu(screen_manager=self.manager)
            self.layout.add_widget(menu)
            self.menu_open = True
        else:
            for child in self.layout.children[:]:
                if isinstance(child, HamburgerMenu): self.layout.remove_widget(child)
            self.menu_open = False

    def switch_camera(self, instance):
        self.camera.index = 1 if self.camera.index == 0 else 0

    def capture_and_detect(self, instance):
        self.result_label.text = 'Processing...'; Clock.schedule_once(self._process_detection, 0.1)

    def _process_detection(self, dt):
        texture = self.camera.texture
        if texture:
            filename = 'temp_capture.png'
            texture.save(filename)
            results = self.yolo_detector.detect_from_image(filename) if self.yolo_detector else self._mock_detection()
            self.display_results(results)
            if os.path.exists(filename): os.remove(filename)

    def display_results(self, results):
        if not results:
            self.result_label.text = 'No items detected'; return
        total = sum(results.values())
        res_str = ", ".join([f"{k}: {v}" for k, v in results.items()])
        self.result_label.text = f"Detected {total} items - {res_str}"
        for name, count in results.items(): self.stock_data.add_record(name, count)

    def _mock_detection(self): return {'item': 1}

class StockListScreen(Screen):
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        layout = BoxLayout(orientation='vertical')
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60)
        with header.canvas.before:
            Color(*COLOR_HEADER)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        back_btn = Button(text='< BACK', size_hint_x=None, width=80, background_color=(0,0,0,0), color=COLOR_NEON_BLUE, bold=True)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='STOCK HISTORY', font_size='18sp', bold=True))
        header.add_widget(Label(size_hint_x=None, width=80))
        
        self.stock_list = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=15)
        self.stock_list.bind(minimum_height=self.stock_list.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.stock_list)
        
        layout.add_widget(header); layout.add_widget(scroll)
        self.add_widget(layout); self.bind(on_enter=self.load_stock_data)

    def update_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def update_header(self, i, v): self.header_rect.pos, self.header_rect.size = i.pos, i.size
    
    def load_stock_data(self, *args):
        self.stock_list.clear_widgets()
        records = self.stock_data.get_all_records()
        for record in reversed(records):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=75, padding=[15, 10])
            with item.canvas.before:
                Color(*COLOR_CARD)
                item.rect = Rectangle(pos=item.pos, size=item.size)
            item.bind(pos=lambda i,v,it=item: setattr(it.rect, 'pos', i.pos), size=lambda i,v,it=item: setattr(it.rect, 'size', i.size))
            item.add_widget(Label(text=f"{record['product_name']} : {record['count']}", bold=True, halign='left', valign='middle', size_hint_x=1, text_size=(350, None)))
            item.add_widget(Label(text=record['timestamp'], color=COLOR_TEXT_DIM, font_size='12sp', halign='left', valign='middle', size_hint_x=1, text_size=(350, None)))
            self.stock_list.add_widget(item)

class AnalyticsScreen(Screen):
    """หน้าจอแสดงกราฟแนวโน้มแบบ Single Line ตามที่คุณชอบ"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        self.selected_product = None
        with self.canvas.before:
            Color(*COLOR_BG); self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        layout = BoxLayout(orientation='vertical')
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        with header.canvas.before:
            Color(*COLOR_HEADER); self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)
        
        back_btn = Button(text='< BACK', size_hint_x=None, width=80, background_color=(0,0,0,0), color=COLOR_NEON_BLUE, bold=True)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
        header.add_widget(back_btn); header.add_widget(Label(text='ANALYTICS', font_size='18sp', bold=True)); header.add_widget(Label(size_hint_x=None, width=80))
        layout.add_widget(header)

        self.selector_area = ScrollView(size_hint_y=None, height=60, do_scroll_x=True, do_scroll_y=False)
        self.product_list = BoxLayout(orientation='horizontal', size_hint_x=None, padding=10, spacing=10)
        self.product_list.bind(minimum_width=self.product_list.setter('width'))
        self.selector_area.add_widget(self.product_list)
        layout.add_widget(self.selector_area)

        self.chart_container = FloatLayout()
        layout.add_widget(self.chart_container)
        self.add_widget(layout); self.bind(on_enter=self.update_product_menu)

    def update_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def update_header(self, i, v): self.header_rect.pos, self.header_rect.size = i.pos, i.size

    def update_product_menu(self, *args):
        self.product_list.clear_widgets()
        trends = self.stock_data.get_product_daily_trends()
        if not trends: return
        for name in trends.keys():
            btn = Button(text=name, size_hint=(None, 1), width=100, background_normal='', 
                        background_color=(0.2, 0.2, 0.2, 1) if name != self.selected_product else COLOR_NEON_BLUE)
            btn.bind(on_press=lambda x, p=name: self.show_graph_for(p))
            self.product_list.add_widget(btn)
        if not self.selected_product and trends: self.show_graph_for(list(trends.keys())[0])

    def show_graph_for(self, name):
        self.selected_product = name; self.update_product_menu(); self.chart_container.clear_widgets()
        data = self.stock_data.get_product_daily_trends().get(name, {})
        if data: self.chart_container.add_widget(self.create_single_line_chart(name, data))

    def create_single_line_chart(self, name, data):
        dates, counts = list(data.keys()), list(data.values())
        max_val = max(counts) if counts else 10
        container = BoxLayout(orientation='vertical', padding=[60, 20, 40, 60])
        plot_area = FloatLayout()
        
        def draw_plot(instance, value):
            plot_area.canvas.clear()
            for child in [c for c in plot_area.children if hasattr(c, 'is_val')]: plot_area.remove_widget(child)
            w, h, x, y = instance.width, instance.height, instance.x, instance.y
            with plot_area.canvas:
                Color(0.2, 0.2, 0.2, 1)
                for i in range(6): 
                    py = y + (h * (i/5) * 0.8)
                    Line(points=[x, py, x + w, py], width=1)
                Color(*COLOR_NEON_BLUE)
                x_step = w / (len(dates) - 1) if len(dates) > 1 else w
                points = []
                for i, count in enumerate(counts):
                    px, py = x + (i * x_step), y + ((count / max_val) * h * 0.8)
                    points.extend([px, py]); Ellipse(pos=(px-5, py-5), size=(10, 10))
                    val_lbl = Label(text=str(count), size_hint=(None, None), size=(30, 20), pos=(px - 15, py + 10), font_size='12sp', bold=True)
                    val_lbl.is_val = True; plot_area.add_widget(val_lbl)
                if len(points) >= 4: Line(points=points, width=3, joint='round')

        plot_area.bind(pos=draw_plot, size=draw_plot)
        for i in range(6):
            val = int((max_val / 5) * i)
            plot_area.add_widget(Label(text=str(val), size_hint=(None, None), size=(40, 20), pos_hint={'x': -0.15, 'y': (i/5) * 0.8}, font_size='12sp', color=COLOR_TEXT_DIM))
        container.add_widget(Label(text=f"Trend: {name}", size_hint_y=None, height=40, bold=True, color=COLOR_NEON_BLUE))
        container.add_widget(plot_area)
        x_lbls = FloatLayout(size_hint_y=None, height=30)
        x_lbls.add_widget(Label(text=dates[0], pos_hint={'x': 0, 'y': 0}, size_hint=(None, 1), font_size='10sp', color=COLOR_TEXT_DIM))
        x_lbls.add_widget(Label(text=dates[-1], pos_hint={'right': 1, 'y': 0}, size_hint=(None, 1), font_size='10sp', color=COLOR_TEXT_DIM))
        container.add_widget(x_lbls)
        return container

class StockCountApp(App):
    def build(self):
        self.stock_data = StockData()
        sm = ScreenManager()
        sm.add_widget(CameraScreen(name='camera', stock_data=self.stock_data))
        sm.add_widget(StockListScreen(name='stock', stock_data=self.stock_data))
        sm.add_widget(AnalyticsScreen(name='analytics', stock_data=self.stock_data))
        return sm

if __name__ == '__main__':
    StockCountApp().run()