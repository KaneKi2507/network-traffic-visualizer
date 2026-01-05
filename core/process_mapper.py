import psutil

def get_process_by_ports(src_port, dst_port):
    try:
        for conn in psutil.net_connections(kind="inet"):
            if not conn.laddr:
                continue

            if conn.laddr.port in (src_port, dst_port):
                if conn.pid:
                    return psutil.Process(conn.pid).name()
    except Exception:
        pass

    return "system"
