from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')


from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from threading import Thread

import psutil

from core.packet_sniffer import start_sniffing
from core.aggregator import get_app_rates, get_app_history
from ui.widgets import TrafficGraph, AppDashboard


class NetworkApp(App):
    def build(self):
        self.current_app = None

        Builder.load_file("ui/dashboard.kv")

        Thread(target=start_sniffing, daemon=True).start()
        Clock.schedule_interval(self.update_ui, 0.5)

        return Builder.load_file("ui/dashboard.kv")

    def update_ui(self, dt):
        rates = get_app_rates()

        main = self.root.get_screen("main")
        total = (
            sum(down + up for down, up in rates.values())
            if rates else 0.1
        )
        main.ids.traffic_graph.update_graph(total)
        main.ids.app_dashboard.update_apps(rates)

        if self.current_app:
            graph = self.root.get_screen("app_graph").ids.app_graph
            graph.set_data(get_app_history(self.current_app))

    def show_app_graph(self, app_name):
        self.current_app = app_name
        self.root.current = "app_graph"

    def show_app_info(self, app_name):
        screen = self.root.get_screen("app_info")
        screen.ids.info_label.text = self._collect_app_info(app_name)
        self.root.current = "app_info"

    def go_back(self):
        self.current_app = None
        self.root.current = "main"

    def _collect_app_info(self, app_name):
        pids = []
        cpu = 0.0
        mem = 0
        conns = 0

        for p in psutil.process_iter(["pid", "name"]):
            try:
                if p.info["name"] == app_name:
                    pids.append(str(p.pid))
                    cpu += p.cpu_percent(interval=0.1)
                    mem += p.memory_info().rss
                    conns += len(p.connections(kind="inet"))
            except Exception:
                pass

        if not pids:
            return f"[b]{app_name}[/b]\n\nNot running."

        return (
            f"[b]Application Information[/b]\n\n"
            f"Name        : {app_name}\n"
            f"PID(s)      : {', '.join(pids)}\n"
            f"Status      : Running\n"
            f"CPU Usage   : {cpu:.2f} %\n"
            f"Memory      : {mem / (1024*1024):.2f} MB\n"
            f"Connections : {conns}\n"
        )


if __name__ == "__main__":
    NetworkApp().run()
