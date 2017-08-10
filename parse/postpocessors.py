import re


def test(input: str) -> str:
    pass


def cisco_iface_name_shorten(long_iface_name: str) -> str:
    result = re.search("^(..)[a-zA-Z-]+([/0-9.]*)", long_iface_name)
    if hasattr(result, 'group'):
        if result.group(2) != '' and result.group(1) != '':
            return result.group(1) + result.group(2)
    return long_iface_name


def cisco_route_type_expand(short_route_type: str) -> str:
    result = []
    route_types = [('C', 'connected'),
                   ('S', 'static'),
                   ('R', 'RIP'),
                   ('M', 'mobile'),
                   ('B', 'BGP'),
                   ('D', 'EIGRP'),
                   ('EX', 'EIGRP external'),
                   ('O', 'OSPF'),
                   ('IA', 'OSPF inter area'),
                   ('N1', 'OSPF NSSA external type 1'),
                   ('N2', 'OSPF NSSA external type 2'),
                   ('E1', 'OSPF external type 1'),
                   ('E2', 'OSPF external type 2'),
                   ('i', 'IS-IS'),
                   ('su', 'IS-IS summary'),
                   ('L1', 'IS-IS level-1'),
                   ('L2', 'IS-IS level-2'),
                   ('ia', 'IS-IS inter area'),
                   ('U', 'per-user static route'),
                   ('o', 'ODR'),
                   ('P', 'periodic downloaded static route'),
                   ('*', 'candidate default')
                   ]
    for rt in route_types:
        if short_route_type.find(rt[0]) > -1:
            result.append(rt[1])
    if len(result) > 0:
        return ' '.join(result)

    return short_route_type


def to_lowercase(input: str) -> str:
    return input.lower()


def to_uppercase(input: str) -> str:
    return input.upper()


def strip_whitespaces(input: str) -> str:
    return input.strip()
