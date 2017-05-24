import re

REHOSTTEMPLATE = "^(?P<host>\\d{,3}\\.\\d{,3}\\.\\d{,3}\\.\\d{,3})$"
RERANGETEMPLATE = "^(?P<net1>\\d{,3}\\.\\d{,3}\\.\\d{,3}\\.\\d{,3})-" \
                  "(?P<net2>\\d{,3}\\.\\d{,3}\\.\\d{,3}\\.\\d{,3})$"
RENETTEMPLATE = "^(?P<net1>\\d{,3}\\.\\d{,3}\\.\\d{,3}\\.\\d{,3})/(?P<mask>\\d{1,2})$"


def _toint(ip_or_mask: str) -> int:

    spl = ip_or_mask.split('.')

    if len(spl) == 1:
        if int(spl[0]) > 24:
            raise ValueError
        return int(spl[0])

    result = 0
    for s in spl:
        if int(s) > 255:
            raise ValueError
        result = result << 8
        result += int(s)

    return result


def parse(nets: list) -> list:

    result = []

    rehost = re.compile(REHOSTTEMPLATE)
    rerange = re.compile(RERANGETEMPLATE)
    renet = re.compile(RENETTEMPLATE)
    for n in nets:
        matchhost = rehost.match(n)
        matchrange = rerange.match(n)
        matchnet = renet.match(n)

        if matchhost is not None:
            result.append(_toint(matchhost.group('host')))

        # TODO spawn set of IP addresses
        if matchrange is not None:

            low = _toint(matchrange.group('net1'))
            high = _toint(matchrange.group('net2'))
            if low > high:
                raise ValueError

            ipset = set(range(low, high + 1))

        if matchnet is not None:
            result.append((matchnet.group('net1'), matchnet.group('mask')))

    return result


