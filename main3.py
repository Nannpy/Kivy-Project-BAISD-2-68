from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from datetime import datetime
import json
import os
import csv
import random

# --- การตั้งค่าพื้นฐานของโปรแกรม ---
Window.size = (400, 700) # กำหนดขนาดหน้าจอจำลองสำหรับ Mobile

# --- การกำหนดชุดสี (Theme) ของแอปพลิเคชัน ---
COLOR_BG = (0.1, 0.1, 0.1, 1)      # สีพื้นหลังเทาเข้ม
COLOR_HEADER = (0.05, 0.05, 0.05, 1) # สีส่วนหัวดำสนิท
COLOR_NEON_BLUE = (0, 0.7, 1, 1)   # สีฟ้าเนออนสำหรับเน้นจุดสำคัญ
COLOR_TEXT_DIM = (0.6, 0.6, 0.6, 1) # สีข้อความสีจางสำหรับคำอธิบาย
COLOR_CARD = (0.15, 0.15, 0.15, 1) # สีพื้นหลังของรายการแต่ละชิ้น
COLOR_DANGER = (0.8, 0.2, 0.2, 1)  # สีแดงสำหรับปุ่มลบ
COLOR_SUCCESS = (0, 0.8, 0.4, 1)  # สีเขียวสำหรับปุ่มส่งออก/บันทึก

# --- ส่วนจัดการข้อมูล (Data Management) ---
class StockData:
    """Class สำหรับจัดการการอ่าน/เขียนไฟล์ JSON และประมวลผลสถิติ"""
    def __init__(self):
        self.filename = 'stock_data.json'
        self.data = self.load_data()
    
    def load_data(self):
        """โหลดข้อมูลจาก JSON หากไม่มีไฟล์จะคืนค่าเป็น List ว่าง"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self):
        """บันทึกข้อมูลปัจจุบันลงในไฟล์ JSON"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_record(self, product_name, count):
        """เพิ่มบันทึกสต็อกใหม่พร้อมประทับเวลา"""
        record = {'product_name': product_name, 'count': count, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        self.data.append(record)
        self.save_data()
    
    def update_record(self, index, new_name, new_count):
        """แก้ไขข้อมูลในรายการเดิมตาม Index ที่กำหนด"""
        try:
            self.data[index]['product_name'] = new_name
            self.data[index]['count'] = int(new_count)
            self.save_data()
            return True
        except: return False

    def delete_record(self, index):
        """ลบรายการข้อมูลออกจากระบบ"""
        try:
            self.data.pop(index)
            self.save_data()
            return True
        except: return False

    def export_to_csv(self):
        """ส่งออกข้อมูลประวัติสต็อกทั้งหมดเป็นไฟล์ CSV เพื่อใช้ใน Excel"""
        if not self.data: return None
        fn = f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        try:
            with open(fn, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['Product', 'Count', 'Time'])
                for r in self.data:
                    w.writerow([r['product_name'], r['count'], r['timestamp']])
            return fn
        except: return None

    def get_all_records(self): return self.data

    def get_product_daily_trends(self):
        """รวมยอดการตรวจนับรายวันแยกตามประเภทสินค้าสำหรับวาดกราฟ"""
        trends = {}
        for r in self.data:
            d, n, c = r['timestamp'].split(' ')[0], r['product_name'], r['count']
            if n not in trends: trends[n] = {}
            trends[n][d] = trends[n].get(d, 0) + c
        return {n: dict(sorted(t.items())) for n, t in trends.items()}

# --- ส่วนเมนูหลัก (Navigation) ---
class HamburgerMenu(BoxLayout):
    """แถบเมนูด้านข้างที่เลื่อนออกมาเพื่อสลับหน้าจอ"""
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'; self.size_hint = (0.7, 1); self.pos_hint = {'left': 0, 'top': 1}
        # วาดพื้นหลังเมนู
        with self.canvas.before:
            Color(0.08, 0.08, 0.08, 1); self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        # หัวข้อเมนู
        self.add_widget(Label(text='MENU', size_hint_y=None, height=80, font_size='22sp', bold=True, color=COLOR_NEON_BLUE))
        # รายการปุ่มในเมนู
        for text, sn in [('CAMERA', 'camera'), ('STOCK LIST', 'stock'), ('ANALYTICS', 'analytics')]:
            btn = Button(text=text, size_hint_y=None, height=60, background_normal='', background_color=(0,0,0,0))
            btn.bind(on_press=lambda x, s=sn: self.go_to_screen(s))
            self.add_widget(btn)
        self.add_widget(Label()) # ตัวดันให้ปุ่มอยู่ด้านบน
    
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size
    def go_to_screen(self, sn):
        self.screen_manager.current = sn
        self.parent.remove_widget(self) # ปิดเมนูหลังจากเลือกหน้า

# --- หน้าจอตรวจจับ (Camera Screen) ---
class CameraScreen(Screen):
    """หน้าจอหลักสำหรับเปิดกล้องและใช้ AI ตรวจนับสต็อก"""
    def __init__(self, stock_data, yolo_detector=None, **kwargs):
        super().__init__(**kwargs)
        self.stock_data, self.yolo_detector, self.menu_open = stock_data, yolo_detector, False
        layout = FloatLayout()
        # พื้นหลัง
        with layout.canvas.before: Color(*COLOR_BG); self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # ส่วนหัว (Header)
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60, pos_hint={'top': 1})
        with header.canvas.before: Color(*COLOR_HEADER); self.h_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_h, size=self.update_h)
        
        # ปุ่ม Hamburger
        h_btn = Button(size_hint=(None, None), size=(65, 65), pos_hint={'center_y': 0.5, 'x': 0.05}, background_normal='/Users/nannam/Downloads/project2/hammenu.png')
        h_btn.bind(on_press=self.toggle_menu)
        header.add_widget(h_btn); header.add_widget(Label(text='STOCK AI SCANNER', font_size='18sp', bold=True))
        
        # วิดเจ็ตกล้อง
        self.camera = Camera(play=True, resolution=(640, 480), size_hint=(0.9, 0.6), pos_hint={'center_x': 0.5, 'top': 0.88}, index=-1)
        # ปุ่มชัตเตอร์ (ถ่ายรูป)
        c_btn = Button(size_hint=(None, None), size=(135, 135), pos_hint={'center_x': 0.5, 'y': 0.15}, background_normal='/Users/nannam/Downloads/project2/camera2.png')
        c_btn.bind(on_press=self.start_detect)
        # ปุ่มสลับกล้อง
        s_btn = Button(size_hint=(None, None), size=(100, 100), pos_hint={'right': 0.95, 'y': 0.15}, background_normal='/Users/nannam/Downloads/project2/swcam.png')
        s_btn.bind(on_press=self.switch_camera)
        
        self.res_lbl = Label(text='Ready to scan', size_hint=(1, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.08}, color=COLOR_NEON_BLUE, bold=True)

        layout.add_widget(header); layout.add_widget(self.camera); layout.add_widget(c_btn); layout.add_widget(s_btn); layout.add_widget(self.res_lbl)
        self.add_widget(layout); self.layout = layout

    def update_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def update_h(self, i, v): self.h_rect.pos, self.h_rect.size = i.pos, i.size
    def toggle_menu(self, *args):
        if not self.menu_open: self.menu = HamburgerMenu(self.manager); self.layout.add_widget(self.menu); self.menu_open = True
        else: self.layout.remove_widget(self.menu); self.menu_open = False
    def switch_camera(self, *args): self.camera.index = 1 if self.camera.index == 0 else 0
    
    def _mock_detection(self):
        """จำลองการตรวจจับกรณีไม่ใช้ AI จริงเพื่อทดสอบระบบ"""
        products = ['person', 'bottle', 'cup', 'snack', 'milk']
        res = {}
        for _ in range(random.randint(1, 2)):
            p = random.choice(products)
            res[p] = (random.randint(1, 5), 0.92) 
        return res

    def start_detect(self, *args):
        """เรียกใช้ฟังก์ชันตรวจจับผ่าน Clock เพื่อไม่ให้ UI ค้าง"""
        self.res_lbl.text = 'Analyzing...'; Clock.schedule_once(self._review, 0.1)

    def _review(self, dt):
        """ประมวลผลรูปภาพและเปิดหน้าต่าง Review ยืนยันจำนวน"""
        if self.camera.texture:
            self.camera.texture.save('temp.png')
            # ตรวจจับด้วย YOLO ถ้าโมเดลพร้อม ถ้าไม่พร้อมให้ใช้ตัวสุ่ม (Mock)
            res = self.yolo_detector.detect_from_image('temp.png') if self.yolo_detector else self._mock_detection()
            self.show_review_popup(res)
            if os.path.exists('temp.png'): os.remove('temp.png')

    def show_review_popup(self, results):
        """Popup สำหรับแสดงผลการนับ และให้ผู้ใช้กด +/- เพื่อแก้ไขจำนวนก่อนบันทึกจริง"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        self.temp_res = {}
        for n, data in results.items():
            count, conf = data if isinstance(data, tuple) else (data, 0.9)
            self.temp_res[n] = count
            row = BoxLayout(size_hint_y=None, height=45, spacing=10)
            row.add_widget(Label(text=f"{n} ({int(conf*100)}%)", halign='left'))
            # ปุ่มลบจำนวน (-)
            b_min = Button(text='-', size_hint_x=None, width=40); b_min.bind(on_press=lambda x, name=n: self.adj(name, -1, lbl))
            lbl = Label(text=str(count), size_hint_x=None, width=40, bold=True)
            # ปุ่มเพิ่มจำนวน (+)
            b_pls = Button(text='+', size_hint_x=None, width=40); b_pls.bind(on_press=lambda x, name=n: self.adj(name, 1, lbl))
            row.add_widget(b_min); row.add_widget(lbl); row.add_widget(b_pls); grid.add_widget(row)
        
        scroll = ScrollView(); scroll.add_widget(grid); content.add_widget(scroll)
        btn = Button(text='SAVE TO STOCK', size_hint_y=None, height=50, background_color=COLOR_SUCCESS, bold=True)
        btn.bind(on_press=lambda x: self.final_save(p)); content.add_widget(btn)
        p = Popup(title="Review AI Detection", content=content, size_hint=(0.9, 0.6)); p.open()

    def adj(self, n, v, l): 
        """ฟังก์ชันปรับจำนวนสินค้าในหน้า Review"""
        self.temp_res[n] = max(0, self.temp_res[n] + v)
        l.text = str(self.temp_res[n])

    def final_save(self, p):
        """บันทึกยอดที่ยืนยันแล้วลงฐานข้อมูล"""
        for n, c in self.temp_res.items(): 
            if c > 0: self.stock_data.add_record(n, c)
        p.dismiss(); self.res_lbl.text = "Stock Updated!"; Popup(title="Status", content=Label(text="Saved Successfully!"), size_hint=(0.6, 0.2)).open()

# --- หน้าจอประวัติสต็อก (Stock List Screen) ---
class StockListScreen(Screen):
    """หน้าจอแสดงรายการประวัติทั้งหมด พร้อมระบบค้นหาและกรองตามวันที่"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data = stock_data
        with self.canvas.before: 
            Color(*COLOR_BG); self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)
        
        layout = BoxLayout(orientation='vertical')
        
        # ส่วนหัวและระบบตัวกรอง (Header)
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=160, spacing=5)
        with header.canvas.before: 
            Color(*COLOR_HEADER); self.h_rect = Rectangle(pos=(0, 0), size=(Window.width, 160))
        header.bind(pos=self._upd_h, size=self._upd_h)
        
        top = BoxLayout(size_hint_y=None, height=60)
        back = Button(text='   BACK', size_hint_x=None, width=80, background_color=(0,0,0,0), color=COLOR_NEON_BLUE, bold=True)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
        top.add_widget(back); top.add_widget(Label(text='STOCK HISTORY', bold=True)); top.add_widget(Label(size_hint_x=None, width=80))
        header.add_widget(top)
        
        # ช่องค้นหาชื่อสินค้า (Search)
        filter_layout = BoxLayout(orientation='vertical', padding=[10, 0, 10, 10], spacing=8)
        self.search = TextInput(hint_text='Search product name...', multiline=False, size_hint_y=None, height=40,
                               background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1), 
                               hint_text_color=(0.5, 0.5, 0.5, 1))
        self.search.bind(text=self.refresh)
        filter_layout.add_widget(self.search)
        
        # ช่องกรองวันที่และปุ่ม CLEAR
        date_row = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=40)
        self.date_filter = TextInput(hint_text='YYYY-MM-DD', multiline=False, size_hint_x=0.7,
                                    background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1),
                                    hint_text_color=(0.5, 0.5, 0.5, 1))
        self.date_filter.bind(text=self.refresh)
        
        clear_btn = Button(text='CLEAR', size_hint_x=0.3, background_normal='', 
                          background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1), bold=True)
        clear_btn.bind(on_press=self.clear_all_filters)
        
        date_row.add_widget(self.date_filter); date_row.add_widget(clear_btn)
        filter_layout.add_widget(date_row); header.add_widget(filter_layout)
        
        # ส่วนแสดงรายการแบบเลื่อนได้ (Scrollable List)
        self.list_view = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=15)
        self.list_view.bind(minimum_height=self.list_view.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.list_view)
        
        layout.add_widget(header); layout.add_widget(scroll)
        self.add_widget(layout); self.bind(on_enter=self.refresh)

    def _upd_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def _upd_h(self, i, v): self.h_rect.pos, self.h_rect.size = i.pos, i.size

    def clear_all_filters(self, *args):
        """ล้างค่าตัวกรองทั้งหมดเพื่อแสดงข้อมูลครบทุกรายการ"""
        self.search.text = ""
        self.date_filter.text = ""
        self.refresh()

    def refresh(self, *args):
        """โหลดรายการใหม่เมื่อมีการพิมพ์ในช่องค้นหา หรือเข้าหน้าจอ"""
        self.list_view.clear_widgets()
        recs = self.stock_data.get_all_records()
        q_name = self.search.text.lower()
        q_date = self.date_filter.text.strip()
        
        for i, r in enumerate(reversed(recs)):
            # ตรองข้อมูลตามชื่อและวันที่
            if q_name in r['product_name'].lower() and q_date in r['timestamp']:
                idx = len(recs) - 1 - i
                box = BoxLayout(orientation='horizontal', size_hint_y=None, height=75, spacing=5)
                # ปุ่มข้อมูลกดเพื่อ Edit
                info = Button(text=f"{r['product_name']} : {r['count']}\n{r['timestamp']}", background_color=COLOR_CARD, halign='left', padding=[15,0])
                info.bind(on_press=lambda x, idx=idx: self.open_edit(idx))
                # ปุ่มลบข้อมูล (DEL)
                del_b = Button(text='DEL', size_hint_x=None, width=60, background_color=COLOR_DANGER)
                del_b.bind(on_press=lambda x, idx=idx: self.confirm_del(idx))
                box.add_widget(info); box.add_widget(del_b); self.list_view.add_widget(box)

    def open_edit(self, idx):
        """หน้าต่างแก้ไขข้อมูลรายการประวัติ"""
        r = self.stock_data.get_all_records()[idx]
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ni = TextInput(text=r['product_name']); ci = TextInput(text=str(r['count']))
        content.add_widget(Label(text="Name:")); content.add_widget(ni)
        content.add_widget(Label(text="Count:")); content.add_widget(ci)
        b = Button(text='UPDATE', background_color=COLOR_SUCCESS)
        b.bind(on_press=lambda x: self.do_upd(idx, ni.text, ci.text, p))
        content.add_widget(b); p = Popup(title="Edit Record", content=content, size_hint=(0.8, 0.5)); p.open()
        
    def do_upd(self, idx, n, c, p): self.stock_data.update_record(idx, n, c); p.dismiss(); self.refresh()

    def confirm_del(self, idx):
        """Popup ยืนยันก่อนทำการลบประวัติ"""
        c = BoxLayout(orientation='vertical', padding=10); c.add_widget(Label(text="Delete this record?"))
        bs = BoxLayout(size_hint_y=None, height=50, spacing=10)
        y = Button(text="YES", background_color=COLOR_DANGER); y.bind(on_press=lambda x: self.do_del(idx, p))
        n = Button(text="NO"); n.bind(on_press=lambda x: p.dismiss()); bs.add_widget(y); bs.add_widget(n); c.add_widget(bs)
        p = Popup(title="Confirm", content=c, size_hint=(0.7, 0.3)); p.open()

    def do_del(self, idx, p): self.stock_data.delete_record(idx); p.dismiss(); self.refresh()

# --- หน้าจอวิเคราะห์สถิติ (Analytics Screen) ---
class AnalyticsScreen(Screen):
    """หน้าจอแสดงกราฟสถิติรายวันแยกตามประเภทสินค้า"""
    def __init__(self, stock_data, **kwargs):
        super().__init__(**kwargs)
        self.stock_data, self.sel_p = stock_data, None
        
        with self.canvas.before: 
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)
        
        layout = BoxLayout(orientation='vertical')
        
        # ส่วนหัว (Header) พร้อมปุ่ม BACK และ EXPORT
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        with header.canvas.before: 
            Color(*COLOR_HEADER)
            self.h_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.h_rect, 'pos', i.pos), 
                    size=lambda i, v: setattr(self.h_rect, 'size', i.size))
        
        back_btn = Button(text='   BACK', size_hint_x=None, width=80, 
                          background_color=(0,0,0,0), color=COLOR_NEON_BLUE, bold=True)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
        
        title_label = Label(text='ANALYTICS', bold=True)
        
        # ปุ่มส่งออกข้อมูล (Export)
        ex = Button(text='EXPORT', size_hint_x=None, width=80, 
                    background_color=(0,0,0,0), color=COLOR_SUCCESS, bold=True)
        ex.bind(on_press=self.do_ex)

        spacer_right = Label(size_hint_x=None, width=40) 
        
        header.add_widget(back_btn); header.add_widget(title_label); header.add_widget(ex); header.add_widget(spacer_right)
        layout.add_widget(header)

        # เมนูเลือกประเภทสินค้า (Horizontal Scroll)
        self.sm = ScrollView(size_hint_y=None, height=60, do_scroll_x=True, do_scroll_y=False)
        self.pb = BoxLayout(orientation='horizontal', size_hint_x=None, padding=10, spacing=10)
        self.pb.bind(minimum_width=self.pb.setter('width'))
        self.sm.add_widget(self.pb)
        layout.add_widget(self.sm)

        # พื้นที่สำหรับวาดกราฟเส้น
        self.cc = FloatLayout() 
        layout.add_widget(self.cc)
        self.add_widget(layout)
        self.bind(on_enter=self.upd_menu)

    def _upd_bg(self, i, v): self.bg_rect.pos, self.bg_rect.size = i.pos, i.size
    def do_ex(self, b): 
        """ฟังก์ชันส่งออกข้อมูลสต็อกทั้งหมดเป็น CSV"""
        f = self.stock_data.export_to_csv()
        if f: b.text = "SAVED!"; Clock.schedule_once(lambda d: setattr(b, 'text', 'EXPORT'), 2)

    def upd_menu(self, *args):
        """สร้างปุ่มสินค้าที่มีอยู่ในระบบเพื่อใช้เลือกดูกราฟ"""
        self.pb.clear_widgets(); tr = self.stock_data.get_product_daily_trends()
        if not tr: return
        for n in tr.keys():
            b = Button(text=n, size_hint=(None, 1), width=110, background_normal='', 
                      background_color=(0.2,0.2,0.2,1) if n != self.sel_p else COLOR_NEON_BLUE)
            b.bind(on_press=lambda x, name=n: self.draw(name)); self.pb.add_widget(b)
        if not self.sel_p and tr: self.draw(list(tr.keys())[0])

    def draw(self, n):
        """ล้างพื้นกราฟเดิมและวาดข้อมูลของสินค้าที่เลือก"""
        self.sel_p = n; self.upd_menu(); self.cc.clear_widgets()
        d = self.stock_data.get_product_daily_trends().get(n, {})
        if d: self.cc.add_widget(self.create_chart(n, d))

    def create_chart(self, n, d):
        """Logic การวาดกราฟเส้นด้วย Kivy Canvas (Line Drawing)"""
        dates, counts = list(d.keys()), list(d.values())
        mv = max(counts) if counts else 10 # สเกลสูงสุดของแกน Y
        root = BoxLayout(orientation='vertical', padding=[60, 20, 40, 60])
        plot = FloatLayout()
        
        def _dr(inst, val):
            # ล้าง Widget ตัวเลข (Label) ของกราฟเก่าออกก่อนวาดใหม่
            to_remove = [c for c in plot.children if hasattr(c, 'is_v') or hasattr(c, 'is_y')]
            for child in to_remove:
                plot.remove_widget(child)

            w, h, x, y = inst.width, inst.height, inst.x, inst.y
            
            plot.canvas.clear()
            with plot.canvas:
                # วาดเส้น Grid แกน Y
                Color(0.2, 0.2, 0.2, 1)
                for i in range(6): 
                    py = y + (h * (i/5) * 0.8)
                    Line(points=[x, py, x + w, py], width=1)
            
            # วาด Label บอกตัวเลขแกน Y
            for i in range(6):
                py = y + (h * (i/5) * 0.8)
                val_y = int((mv / 5) * i)
                y_lbl = Label(text=str(val_y), size_hint=(None, None), size=(40, 20),
                             pos=(x - 50, py - 10), font_size='11sp', color=COLOR_TEXT_DIM)
                y_lbl.is_y = True
                plot.add_widget(y_lbl)

            # วาดเส้นกราฟ
            with plot.canvas:
                Color(*COLOR_NEON_BLUE)
                x_s = w / (len(dates) - 1) if len(dates) > 1 else w
                pts = []
                for i, v in enumerate(counts):
                    px, py = x + (i * x_s), y + ((v / mv) * h * 0.8)
                    pts.extend([px, py])
                
                # ลากเส้นเชื่อมระหว่างจุดข้อมูล
                if len(pts) >= 4:
                    Line(points=pts, width=3, joint='round')
                
                # วาดจุดข้อมูล (Dot)
                Color(1, 1, 1, 1)
                for i in range(0, len(pts), 2):
                    Ellipse(pos=(pts[i]-5, pts[i+1]-5), size=(10, 10))
            
            # วาด Label ตัวเลขบอกค่าที่อยู่เหนือแต่ละจุด
            for i, v in enumerate(counts):
                px = x + (i * x_s)
                py = y + ((v / mv) * h * 0.8)
                val_lbl = Label(text=str(v), size_hint=(None, None), size=(30, 20), 
                               pos=(px-15, py+10), font_size='12sp', bold=True)
                val_lbl.is_v = True
                plot.add_widget(val_lbl)

        # ผูกฟังก์ชันวาดกราฟเข้ากับการเปลี่ยนแปลงขนาด (Resize) ของ FloatLayout
        plot.bind(pos=_dr, size=_dr)

        root.add_widget(Label(text=f"Stock Trend : {n}", size_hint_y=None, height=40, bold=True, color=COLOR_NEON_BLUE))
        root.add_widget(plot)
        
        # แสดงวันที่เริ่มต้นและวันที่ล่าสุดที่แกน X
        xl = FloatLayout(size_hint_y=None, height=30)
        xl.add_widget(Label(text=dates[0], pos_hint={'x': 0, 'y': 0}, size_hint=(None, 1), font_size='10sp', color=COLOR_TEXT_DIM))
        xl.add_widget(Label(text=dates[-1], pos_hint={'right': 1, 'y': 0}, size_hint=(None, 1), font_size='10sp', color=COLOR_TEXT_DIM))
        root.add_widget(xl)
        
        return root

# --- ส่วนหลักที่ใช้รันโปรแกรม (Main Entry) ---
class StockCountApp(App):
    def build(self):
        self.stock_data = StockData()
        # พยายามโหลด YOLO Detector ถ้ามีการติดตั้งไฟล์ไว้
        try:
            from yolo_detector import YOLODetector
            self.yolo_detector = YOLODetector('yolov8n.pt')
        except: self.yolo_detector = None
        
        # จัดการหน้าจอด้วย ScreenManager
        sm = ScreenManager()
        sm.add_widget(CameraScreen(name='camera', stock_data=self.stock_data, yolo_detector=self.yolo_detector))
        sm.add_widget(StockListScreen(name='stock', stock_data=self.stock_data))
        sm.add_widget(AnalyticsScreen(name='analytics', stock_data=self.stock_data))
        return sm

if __name__ == '__main__': 
    StockCountApp().run()