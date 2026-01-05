from collections import defaultdict, deque
import time

_app_up_bytes = defaultdict(int)
_app_down_bytes = defaultdict(int)
_app_history = defaultdict(lambda: deque(maxlen=50))
_last_time = time.time()


def add_traffic(app, size, direction):
    if direction == "up":
        _app_up_bytes[app] += size
    else:
        _app_down_bytes[app] += size


def get_app_rates():
    global _last_time
    now = time.time()
    elapsed = max(now - _last_time, 0.1)

    rates = {}

    for app in set(_app_up_bytes) | set(_app_down_bytes):
        up_kbps = (_app_up_bytes[app] * 8) / elapsed / 1000
        down_kbps = (_app_down_bytes[app] * 8) / elapsed / 1000

        rates[app] = (down_kbps, up_kbps)
        _app_history[app].append(down_kbps + up_kbps)

    _app_up_bytes.clear()
    _app_down_bytes.clear()
    _last_time = now

    return rates


def get_app_history(app):
    return list(_app_history.get(app, []))
