import socket


def istcpportopen(ip: str, port: int, timeout: int = 5) -> bool:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    result = sock.connect_ex((ip, port))
    return result == 0

