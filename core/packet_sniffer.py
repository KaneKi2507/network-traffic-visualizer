from scapy.all import sniff, TCP
import psutil
from core.platform import IS_WINDOWS
from core.aggregator import add_traffic
import time

if IS_WINDOWS:
    from scapy.all import conf
    conf.use_pcap = True

# Cache port → app for stability
PORT_CACHE = {}
CACHE_TIMEOUT = 10  # seconds


def get_process_by_port(port):
    now = time.time()

    # Use cache first
    if port in PORT_CACHE:
        app, ts = PORT_CACHE[port]
        if now - ts < CACHE_TIMEOUT:
            return app

    candidates = []

    try:
        for c in psutil.net_connections(kind="inet"):
            if not c.pid or not c.laddr:
                continue

            if c.laddr.port == port or (c.raddr and c.raddr.port == port):
                try:
                    p = psutil.Process(c.pid)
                    name = p.name()

                    # Prefer browsers
                    if any(b in name.lower() for b in ["chrome", "firefox", "edge"]):
                        PORT_CACHE[port] = (name, now)
                        return name

                    candidates.append(name)
                except Exception:
                    pass
    except Exception:
        pass

    if candidates:
        PORT_CACHE[port] = (candidates[0], now)
        return candidates[0]

    return "System"


def on_packet(pkt):
    if TCP in pkt:
        size = len(pkt)

        sport = pkt[TCP].sport
        dport = pkt[TCP].dport

        app = get_process_by_port(sport)
        direction = "up"

        if app == "System":
            app = get_process_by_port(dport)
            direction = "down"

        add_traffic(app, size, direction)


def start_sniffing():
    sniff(prn=on_packet, store=False)
