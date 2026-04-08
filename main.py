from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import platform
import json
import os
from datetime import datetime, timedelta

# 设置窗口大小（手机尺寸）
Window.size = (375, 812)

# 主题色配置
THEMES = {
    'default': {'primary': '#3b82f6', 'bg': '#FAFAFA', 'card': '#ffffff'},
    'sky': {'primary': '#87CEEB', 'bg': '#F0F8FF', 'card': '#ffffff'},
    'mint': {'primary': '#98FB98', 'bg': '#F0FFF0', 'card': '#ffffff'},
    'pink': {'primary': '#FFB6C1', 'bg': '#FFF0F5', 'card': '#ffffff'},
    'yellow': {'primary': '#FFD700', 'bg': '#FFFACD', 'card': '#ffffff'},
    'purple': {'primary': '#DDA0DD', 'bg': '#F8F0FF', 'card': '#ffffff'},
    'beige': {'primary': '#D2B48C', 'bg': '#F5F5DC', 'card': '#ffffff'},
    'gray': {'primary': '#A9A9A9', 'bg': '#F5F5F5', 'card': '#ffffff'},
    'cyan': {'primary': '#AFEEEE', 'bg': '#F0FFFF', 'card': '#ffffff'},
}


class TimerCard(BoxLayout):
    """计时卡片组件"""
    timer_id = StringProperty('')
    timer_name = StringProperty('计时器')
    note = StringProperty('')
    elapsed = NumericProperty(0)  # 已运行秒数
    target = NumericProperty(0)   # 目标秒数（0表示正计时）
    is_running = BooleanProperty(False)
    is_paused = BooleanProperty(False)
    
    def __init__(self, timer_id, **kwargs):
        super().__init__(**kwargs)
        self.timer_id = timer_id
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(16)
        self.spacing = dp(8)
        
        # 卡片背景
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(rgba=(1, 1, 1, 1))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        self._build_ui()
        Clock.schedule_interval(self._update_timer, 1)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _build_ui(self):
        # 标题行
        header = BoxLayout(size_hint_y=None, height=dp(30))
        
        self.name_label = Button(
            text=self.timer_name,
            size_hint_x=0.8,
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(14)
        )
        self.name_label.bind(on_press=self._show_rename_popup)
        
        menu_btn = Button(
            text='⋮',
            size_hint_x=0.2,
            background_normal='',
            background_color=(1, 1, 1, 0),
            color=(0.4, 0.4, 0.4, 1),
            font_size=dp(20)
        )
        menu_btn.bind(on_press=self._show_menu)
        
        header.add_widget(self.name_label)
        header.add_widget(menu_btn)
        self.add_widget(header)
        
        # 时间显示
        self.time_label = Label(
            text='00:00:00',
            font_size=dp(36),
            font_name='RobotoMono',
            color=(0.12, 0.12, 0.12, 1),
            size_hint_y=None,
            height=dp(60)
        )
        self.add_widget(self.time_label)
        
        # 备注输入
        self.note_input = TextInput(
            hint_text='添加备注...',
            text=self.note,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0.97, 0.97, 0.97, 1),
            padding=[dp(12), dp(10)],
            font_size=dp(13)
        )
        self.note_input.bind(text=self._on_note_change)
        self.add_widget(self.note_input)
        
        # 控制按钮
        controls = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        self.start_btn = Button(
            text='开始',
            background_normal='',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14),
            bold=True
        )
        self.start_btn.bind(on_press=self._toggle_timer)
        
        self.reset_btn = Button(
            text='重置',
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.3, 0.3, 0.3, 1),
            font_size=dp(14)
        )
        self.reset_btn.bind(on_press=self._reset_timer)
        
        controls.add_widget(self.start_btn)
        controls.add_widget(self.reset_btn)
        self.add_widget(controls)
    
    def _update_timer(self, dt):
        if self.is_running and not self.is_paused:
            self.elapsed += 1
            self._update_display()
            
            # 检查倒计时结束
            if self.target > 0 and self.elapsed >= self.target:
                self._on_countdown_finish()
    
    def _update_display(self):
        hours = self.elapsed // 3600
        minutes = (self.elapsed % 3600) // 60
        seconds = self.elapsed % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.text = time_str
        
        # 更新颜色
        if self.is_running:
            if self.target > 0 and self.elapsed > self.target:
                self.time_label.color = (0.93, 0.27, 0.27, 1)  # 红色 - 超时
            else:
                self.time_label.color = (0.13, 0.77, 0.37, 1)  # 绿色 - 运行中
        elif self.is_paused:
            self.time_label.color = (0.96, 0.59, 0.04, 1)  # 橙色 - 暂停
        else:
            self.time_label.color = (0.12, 0.12, 0.12, 1)  # 黑色 - 初始
    
    def _toggle_timer(self, *args):
        if not self.is_running:
            # 首次开始，选择时长
            self._show_duration_popup()
        elif self.is_paused:
            # 继续
            self.is_paused = False
            self.start_btn.text = '暂停'
            self.start_btn.background_color = (0.96, 0.59, 0.04, 1)
        else:
            # 暂停
            self.is_paused = True
            self.start_btn.text = '继续'
            self.start_btn.background_color = (0.23, 0.51, 0.96, 1)
        self._update_display()
    
    def _show_duration_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # 预设选项
        presets = [
            ('1小时', 3600),
            ('2小时', 7200),
            ('3小时', 10800),
            ('不限时', 0)
        ]
        
        for name, seconds in presets:
            btn = Button(
                text=name,
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.95, 0.95, 0.95, 1)
            )
            btn.bind(on_press=lambda x, s=seconds: self._start_with_duration(s))
            content.add_widget(btn)
        
        # 自定义输入
        custom_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.custom_hours = TextInput(hint_text='时', multiline=False, input_filter='int')
        self.custom_mins = TextInput(hint_text='分', multiline=False, input_filter='int')
        self.custom_secs = TextInput(hint_text='秒', multiline=False, input_filter='int')
        custom_box.add_widget(self.custom_hours)
        custom_box.add_widget(self.custom_mins)
        custom_box.add_widget(self.custom_secs)
        content.add_widget(custom_box)
        
        # 自定义确认按钮
        custom_btn = Button(
            text='自定义时长',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        custom_btn.bind(on_press=self._start_custom_duration)
        content.add_widget(custom_btn)
        
        self.duration_popup = Popup(
            title='选择时长',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=True
        )
        self.duration_popup.open()
    
    def _start_with_duration(self, seconds):
        self.target = seconds
        self.is_running = True
        self.is_paused = False
        self.start_btn.text = '暂停'
        self.start_btn.background_color = (0.96, 0.59, 0.04, 1)
        self.duration_popup.dismiss()
        self._update_display()
    
    def _start_custom_duration(self, *args):
        try:
            hours = int(self.custom_hours.text or 0)
            mins = int(self.custom_mins.text or 0)
            secs = int(self.custom_secs.text or 0)
            total = hours * 3600 + mins * 60 + secs
            self._start_with_duration(total)
        except:
            pass
    
    def _reset_timer(self, *args):
        self.is_running = False
        self.is_paused = False
        self.elapsed = 0
        self.target = 0
        self.start_btn.text = '开始'
        self.start_btn.background_color = (0.23, 0.51, 0.96, 1)
        self._update_display()
    
    def _on_countdown_finish(self):
        # 倒计时结束提醒
        self.is_running = False
        self.start_btn.text = '开始'
        self.start_btn.background_color = (0.23, 0.51, 0.96, 1)
        
        # 震动提醒（如果支持）
        if platform == 'android':
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            @run_on_ui_thread
            def vibrate():
                Context = autoclass('android.content.Context')
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                if vibrator.hasVibrator():
                    vibrator.vibrate(2000)  # 震动2秒
            
            vibrate()
    
    def _show_rename_popup(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        text_input = TextInput(
            text=self.timer_name,
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(text_input)
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        confirm_btn = Button(
            text='确定',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1)
        )
        
        def do_rename(*args):
            self.timer_name = text_input.text or '计时器'
            self.name_label.text = self.timer_name
            popup.dismiss()
        
        confirm_btn.bind(on_press=do_rename)
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(confirm_btn)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='重命名',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def _show_menu(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        rename_btn = Button(
            text='重命名',
            size_hint_y=None,
            height=dp(50)
        )
        rename_btn.bind(on_press=lambda x: (self._show_rename_popup(), popup.dismiss()))
        
        delete_btn = Button(
            text='删除',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.93, 0.27, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        delete_btn.bind(on_press=lambda x: self._confirm_delete(popup))
        
        content.add_widget(rename_btn)
        content.add_widget(delete_btn)
        
        popup = Popup(
            title='菜单',
            content=content,
            size_hint=(0.6, 0.35)
        )
        popup.open()
    
    def _confirm_delete(self, menu_popup):
        menu_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text='确定要删除这个计时器吗？'))
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        confirm_btn = Button(
            text='删除',
            background_color=(0.93, 0.27, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        confirm_btn.bind(on_press=lambda x: self._do_delete(popup))
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(confirm_btn)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, 0.35)
        )
        popup.open()
    
    def _do_delete(self, popup):
        popup.dismiss()
        if self.parent:
            self.parent.remove_widget(self)
    
    def _on_note_change(self, instance, value):
        self.note = value
    
    def get_state(self):
        return {
            'id': self.timer_id,
            'name': self.timer_name,
            'note': self.note,
            'elapsed': self.elapsed,
            'target': self.target,
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }
    
    def set_state(self, state):
        self.timer_name = state.get('name', '计时器')
        self.name_label.text = self.timer_name
        self.note = state.get('note', '')
        self.note_input.text = self.note
        self.elapsed = state.get('elapsed', 0)
        self.target = state.get('target', 0)
        self.is_running = state.get('is_running', False)
        self.is_paused = state.get('is_paused', False)
        
        if self.is_running:
            if self.is_paused:
                self.start_btn.text = '继续'
                self.start_btn.background_color = (0.23, 0.51, 0.96, 1)
            else:
                self.start_btn.text = '暂停'
                self.start_btn.background_color = (0.96, 0.59, 0.04, 1)
        
        self._update_display()


class TimerApp(App):
    """主应用类"""
    
    def build(self):
        self.title = '极简计时器'
        self.timers = []
        self.timer_counter = 0
        
        # 数据存储
        self.store = JsonStore('timer_data.json')
        
        # 主布局
        root = BoxLayout(orientation='vertical')
        
        # 顶部栏
        header = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        
        title = Label(
            text='极简计时器',
            font_size=dp(20),
            bold=True,
            size_hint_x=0.6,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        
        settings_btn = Button(
            text='⚙',
            size_hint_x=0.2,
            background_normal='',
            background_color=(1, 1, 1, 0),
            font_size=dp(24)
        )
        settings_btn.bind(on_press=self._show_settings)
        
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))  # 占位
        header.add_widget(settings_btn)
        root.add_widget(header)
        
        # 批量操作栏
        batch_bar = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(8)],
            spacing=dp(8)
        )
        
        batch_actions = [
            ('全部开始', self._batch_start),
            ('全部暂停', self._batch_pause),
            ('全部重置', self._batch_reset),
            ('全部删除', self._batch_delete)
        ]
        
        for text, callback in batch_actions:
            btn = Button(
                text=text,
                font_size=dp(12),
                background_normal='',
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=callback)
            batch_bar.add_widget(btn)
        
        root.add_widget(batch_bar)
        
        # 计时器列表
        scroll = ScrollView()
        self.timer_grid = GridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None
        )
        self.timer_grid.bind(minimum_height=self.timer_grid.setter('height'))
        scroll.add_widget(self.timer_grid)
        root.add_widget(scroll)
        
        # 添加按钮
        add_btn = Button(
            text='+ 增加计时',
            size_hint_y=None,
            height=dp(56),
            background_normal='',
            background_color=(0.23, 0.51, 0.96, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True
        )
        add_btn.bind(on_press=self._add_timer)
        root.add_widget(add_btn)
        
        # 加载保存的数据
        self._load_data()
        
        # 如果没有计时器，默认添加2个
        if len(self.timers) == 0:
            self._add_timer()
            self._add_timer()
        
        # 自动保存
        Clock.schedule_interval(self._auto_save, 5)
        
        return root
    
    def _add_timer(self, *args):
        self.timer_counter += 1
        timer = TimerCard(timer_id=f'timer_{self.timer_counter}')
        self.timers.append(timer)
        self.timer_grid.add_widget(timer)
    
    def _batch_start(self, *args):
        for timer in self.timers:
            if not timer.is_running:
                timer._start_with_duration(0)  # 默认正计时
    
    def _batch_pause(self, *args):
        for timer in self.timers:
            if timer.is_running and not timer.is_paused:
                timer._toggle_timer()
    
    def _batch_reset(self, *args):
        for timer in self.timers:
            timer._reset_timer()
    
    def _batch_delete(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text='确定要删除所有计时器吗？'))
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        confirm_btn = Button(
            text='全部删除',
            background_color=(0.93, 0.27, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        confirm_btn.bind(on_press=lambda x: self._do_batch_delete(popup))
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(confirm_btn)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, 0.35)
        )
        popup.open()
    
    def _do_batch_delete(self, popup):
        popup.dismiss()
        for timer in self.timers[:]:
            self.timer_grid.remove_widget(timer)
        self.timers.clear()
        self.timer_counter = 0
    
    def _show_settings(self, *args):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        content.add_widget(Label(
            text='选择主题色',
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))
        
        # 主题色选择
        theme_grid = GridLayout(cols=4, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        theme_names = {
            'default': '默认蓝',
            'sky': '浅天蓝',
            'mint': '薄荷绿',
            'pink': '浅樱粉',
            'yellow': '浅鹅黄',
            'purple': '淡紫',
            'beige': '米白',
            'gray': '浅烟灰',
            'cyan': '浅青'
        }
        
        for theme_id, theme_data in THEMES.items():
            btn = Button(
                background_normal='',
                background_color=self._hex_to_rgb(theme_data['primary'])
            )
            btn.bind(on_press=lambda x, t=theme_id: self._apply_theme(t, popup))
            theme_grid.add_widget(btn)
        
        content.add_widget(theme_grid)
        
        popup = Popup(
            title='设置',
            content=content,
            size_hint=(0.9, 0.6)
        )
        popup.open()
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)) + (1,)
    
    def _apply_theme(self, theme_id, popup):
        # 应用主题色（简化实现）
        popup.dismiss()
    
    def _auto_save(self, dt):
        self._save_data()
    
    def _save_data(self):
        data = {
            'timers': [t.get_state() for t in self.timers],
            'counter': self.timer_counter
        }
        with open('timer_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    
    def _load_data(self):
        try:
            with open('timer_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.timer_counter = data.get('counter', 0)
            for timer_data in data.get('timers', []):
                timer = TimerCard(timer_id=timer_data['id'])
                timer.set_state(timer_data)
                self.timers.append(timer)
                self.timer_grid.add_widget(timer)
        except:
            pass
    
    def on_stop(self):
        self._save_data()


if __name__ == '__main__':
    TimerApp().run()