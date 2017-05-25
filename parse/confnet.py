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
        result = (result << 8) + int(s)
    print(bin(result))
    return result


def parseline(net: str) -> set:

    rehost = re.compile(REHOSTTEMPLATE)
    rerange = re.compile(RERANGETEMPLATE)
    renet = re.compile(RENETTEMPLATE)

    matchhost = rehost.match(net)
    matchrange = rerange.match(net)
    matchnet = renet.match(net)

    if matchhost is not None:

        return {_toint(matchhost.group('host'))}

    if matchrange is not None:

        low = _toint(matchrange.group('net1'))
        high = _toint(matchrange.group('net2'))
        if low > high:
            raise ValueError

        return set(range(low, high + 1))

    if matchnet is not None:

        net = _toint(matchnet.group('net1'))
        maskbitcount = _toint(matchnet.group('mask'))

        mask = 0xFFFFFFFF << (32 - maskbitcount)
        maxhost = 0xFFFFFFFF >> maskbitcount
        net |= mask

        return set(range(net, net + maxhost + 1))

    return set()


def parselist():
    pass



