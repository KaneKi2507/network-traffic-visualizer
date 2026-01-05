from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from kivy.metrics import dp

import psutil


# =========================
#   TRAFFIC GRAPH
# =========================
class TrafficGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.max_points = 50
        self.y_max = 10.0

    def update_graph(self, value):
        if value > self.y_max:
            self.y_max = value * 1.3

        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)

        self._draw()

    def set_data(self, data):
        self.data = data
        self.y_max = max(data) * 1.3 if data else 10.0
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 0)
            if len(self.data) > 1:
                points = []
                for i, v in enumerate(self.data):
                    x = self.x + i * (self.width / self.max_points)
                    y = self.y + (v / self.y_max) * self.height
                    points.extend([x, y])
                Line(points=points, width=dp(2))


# =========================
#   APP ROW (RIGHT CLICK)
# =========================
class AppRow(Label):
    def __init__(self, app_name, **kwargs):
        super().__init__(**kwargs)

        self.app_name = app_name
        self.size_hint_y = None
        self.height = dp(28)
        self.halign = "left"
        self.valign = "middle"
        self.padding = (dp(10), 0)

        self.bind(size=self._update_text)
        self.dropdown = self._create_dropdown()

    def _update_text(self, *_):
        self.text_size = self.size

    def _create_dropdown(self):
        dropdown = DropDown(auto_width=False, width=dp(160))

        def add_item(text, callback):
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(30),
                font_size="13sp"
            )
            btn.bind(on_release=lambda *_: (callback(), dropdown.dismiss()))
            dropdown.add_widget(btn)

        add_item("Information", self.show_info)
        add_item("Show Graph", self.show_graph)
        add_item("Close App", self.close_app)

        return dropdown

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == "right":
            self.dropdown.open(self)
            return True
        return super().on_touch_down(touch)

    def show_info(self):
        from kivy.app import App
        App.get_running_app().show_app_info(self.app_name)

    def show_graph(self):
        from kivy.app import App
        App.get_running_app().show_app_graph(self.app_name)

    def close_app(self):
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] == self.app_name:
                    proc.terminate()
            except Exception:
                pass


# =========================
#   APP DASHBOARD
# =========================
class AppDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.rows = {}

    def update_apps(self, rates):
        for app, (down, up) in rates.items():
            if app not in self.rows:
                row = AppRow(app)
                self.rows[app] = row
                self.add_widget(row)

            self.rows[app].text = (
                f"{app}  |  ⬇ {down:.2f} kbps  |  ⬆ {up:.2f} kbps"
            )

