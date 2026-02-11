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
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

# =========================
# THEME COLOR (GREEN AI)
# =========================
BACKGROUND = (0.93, 0.97, 0.95, 1)   # เขียวอมเทาอ่อน
HEADER_COLOR = (0.10, 0.55, 0.35, 1)

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
        summary = {}
        for record in self.data:
            name = record['product_name']
            count = record['count']
            if name in summary:
                summary[name] += count
            else:
                summary[name] = count
        return summary


class HamburgerMenu(BoxLayout):
    """เมนู hamburger"""
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.size_hint = (0.7, 1)
        self.pos_hint = {'right': 1, 'top': 1}

        with self.canvas.before:
            Color(0.88, 0.94, 0.90, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        header = Label(
            text='Menu',
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True,
            color=(0, 0, 0, 1)
        )
        self.add_widget(header)

        menu_items = [
            ('หน้าแรก', 'camera'),
            ('รายการสต็อก', 'stock'),
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

        self.add_widget(Label())

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_screen(self, screen_name):
        self.screen_manager.current = screen_name
        self.parent.remove_widget(self)


class CameraScreen(Screen):
    """หน้าจอกล้องสำหรับนับสต็อก"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        self.menu_open = False

        layout = FloatLayout()

        # ===== Background =====
        with layout.canvas.before:
            Color(*BACKGROUND)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # ===== Header =====
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=60,
            pos_hint={'top': 1}
        )

        with header.canvas.before:
            Color(*HEADER_COLOR)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)

        hamburger_btn = Button(
            text='☰',
            size_hint=(None, 1),
            width=60,
            background_color=HEADER_COLOR,
            font_size='30sp',
            color=(1, 1, 1, 1)
        )
        hamburger_btn.bind(on_press=self.toggle_menu)

        app_title = Label(
            text='Smart Inventory',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )

        header.add_widget(hamburger_btn)
        header.add_widget(app_title)

        camera_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, None),
            height=400,
            pos_hint={'center_x': 0.5, 'top': 0.85}
        )

        self.display_area = FloatLayout()
        with self.display_area.canvas:
            Color(0.88, 0.93, 0.90, 1)
            self.display_rect = Rectangle(pos=self.display_area.pos, size=self.display_area.size)
            Color(0.20, 0.75, 0.55, 1)
            self.display_border = Line(rectangle=(0, 0, 0, 0), width=2)

        self.display_area.bind(pos=self.update_display, size=self.update_display)
        camera_box.add_widget(self.display_area)

        self.result_label = Label(
            text='result : Product name , Product count',
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.1},
            color=(0, 0, 0, 1),
            font_size='14sp'
        )

        layout.add_widget(header)
        layout.add_widget(camera_box)
        layout.add_widget(self.result_label)

        self.add_widget(layout)
        self.layout = layout

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def update_display(self, instance, value):
        self.display_rect.pos = instance.pos
        self.display_rect.size = instance.size
        self.display_border.rectangle = (
            instance.x, instance.y,
            instance.width, instance.height
        )

    def toggle_menu(self, instance):
        if not self.menu_open:
            menu = HamburgerMenu(screen_manager=self.manager)
            self.layout.add_widget(menu)
            self.menu_open = True
        else:
            for child in self.layout.children[:]:
                if isinstance(child, HamburgerMenu):
                    self.layout.remove_widget(child)
            self.menu_open = False


class StockListScreen(Screen):
    """หน้าจอแสดงรายการสต็อก"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data

        layout = BoxLayout(orientation='vertical')

        with layout.canvas.before:
            Color(*BACKGROUND)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        header = BoxLayout(size_hint=(1, None), height=60)
        with header.canvas.before:
            Color(*HEADER_COLOR)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)

        back_btn = Button(text='←', size_hint=(None, 1), width=60)
        back_btn.bind(on_press=self.go_back)

        title = Label(text='รายการสต็อก', color=(1, 1, 1, 1))

        header.add_widget(back_btn)
        header.add_widget(title)

        scroll = ScrollView()
        self.stock_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.stock_list.bind(minimum_height=self.stock_list.setter('height'))

        scroll.add_widget(self.stock_list)

        layout.add_widget(header)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.bind(on_enter=self.load_stock_data)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def go_back(self, instance):
        self.manager.current = 'camera'

    def load_stock_data(self, *args):
        self.stock_list.clear_widgets()
        for record in reversed(self.stock_data.get_all_records()):
            label = Label(
                text=f"{record['product_name']} - {record['count']} ({record['timestamp']})",
                size_hint_y=None,
                height=40,
                color=(0, 0, 0, 1)
            )
            self.stock_list.add_widget(label)


class AnalyticsScreen(Screen):
    """หน้าจอแสดงกราฟวิเคราะห์"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data

        layout = BoxLayout(orientation='vertical')

        with layout.canvas.before:
            Color(*BACKGROUND)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        header = BoxLayout(size_hint=(1, None), height=60)
        with header.canvas.before:
            Color(*HEADER_COLOR)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header, size=self.update_header)

        back_btn = Button(text='←', size_hint=(None, 1), width=60)
        back_btn.bind(on_press=self.go_back)

        title = Label(text='Analytics', color=(1, 1, 1, 1))

        header.add_widget(back_btn)
        header.add_widget(title)

        self.chart_container = BoxLayout()

        layout.add_widget(header)
        layout.add_widget(self.chart_container)

        self.add_widget(layout)
        self.bind(on_enter=self.load_chart)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def go_back(self, instance):
        self.manager.current = 'camera'

    def load_chart(self, *args):
        self.chart_container.clear_widgets()
        summary = self.stock_data.get_summary()

        if not summary:
            self.chart_container.add_widget(Label(text='ยังไม่มีข้อมูล'))
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(summary.keys(), summary.values(), color='#2ECC71')
        ax.set_title('สรุปจำนวนสต็อกสินค้า')

        self.chart_container.add_widget(FigureCanvasKivyAgg(fig))


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
