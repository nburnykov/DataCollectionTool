# TODO move to decision tree class


def find_attr_by_name(query_dict: dict, attr: str):

    _attr_presented = False
    _attr = ''
    for query in query_dict:
        if query['ID'] == attr:
            _attr_presented = True
            _attr = query['CLI']

            if type(_attr) is str:
                _attr = [_attr]

            return _attr_presented, _attr

    return _attr_presented, _attr
