import re


RE_TEMPLATE_HOST = "^(?P<host>\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})$"
RE_TEMPLATE_RANGE = "^(?P<net1>\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})-" \
                  "(?P<net2>\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})$"
RE_TEMPLATE_NET = "^(?P<net1>\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})/(?P<mask>\\d{1,2})$"


def _to_int(ip_or_mask: str) -> int:

    spl = ip_or_mask.split('.')

    if len(spl) == 1:
        if int(spl[0]) > 32:
            raise ValueError
        return int(spl[0])

    result = 0
    for s in spl:
        if int(s) > 255:
            raise ValueError
        result = (result << 8) + int(s)

    return result


def parse_line(net: str) -> set:

    re_host = re.compile(RE_TEMPLATE_HOST)
    re_range = re.compile(RE_TEMPLATE_RANGE)
    re_net = re.compile(RE_TEMPLATE_NET)

    match_host = re_host.match(net)
    match_range = re_range.match(net)
    match_net = re_net.match(net)

    if match_host is not None:

        return {_to_int(match_host.group('host'))}

    if match_range is not None:

        low = _to_int(match_range.group('net1'))
        high = _to_int(match_range.group('net2'))
        if low > high:
            raise ValueError

        return set(range(low, high + 1))

    if match_net is not None:

        net = _to_int(match_net.group('net1'))
        maskbitcount = _to_int(match_net.group('mask'))

        mask = 0xFFFFFFFF << (32 - maskbitcount)
        max_host = 0xFFFFFFFF >> maskbitcount
        net &= mask

        return set(range(net, net + max_host + 1))

    return set()


def parse_list(iplist: list) -> set:
    for s in iplist:
        yield parse_line(s)


def compose_set(iplist: list) -> set:
    result = set()
    for rng in parse_list(iplist):
        result |= rng
    return result


def dec_to_ip(host: int) -> str:
    mask = 0xFF
    result = []
    for _ in range(0, 4):
        result.append(str(host & mask))
        host >>= 8
    result.reverse()

    return '.'.join(result)


def check_line(text: str) -> bool:

    def _check_digit(ip: str) -> bool:

        result = True
        declist = ip.split(".")
        for dec in declist:
            d = int(dec)
            result &= d <= 255

        return result

    if text == "":
        return True

    re_host = re.compile(RE_TEMPLATE_HOST)
    re_range = re.compile(RE_TEMPLATE_RANGE)
    re_net = re.compile(RE_TEMPLATE_NET)

    match_host = re_host.match(text)
    match_range = re_range.match(text)
    match_net = re_net.match(text)

    if match_host is not None:
        return _check_digit(match_host.group('host'))

    if match_net is not None:
        return _check_digit(match_net.group('net1')) and (int(match_net.group('mask')) < 32)

    if match_range is not None:
        if _check_digit(match_range.group('net1')) and _check_digit(match_range.group('net2')):
            low = _to_int(match_range.group('net1'))
            high = _to_int(match_range.group('net2'))
            if low < high:
                return True

    return False


