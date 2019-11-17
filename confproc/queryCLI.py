# TODO refactor logic


class QueryCLI:
    def __init__(self, querydict):
        self.querydict = querydict
        self.attr_presented = False
        self.attr = ''

    def is_attr_presented(self):
        return self.attr_presented

    def find_attr_by_name(self, attr):

        self.attr_presented = False
        self.attr = ''
        for query in self.querydict:
            if query['ID'] == attr:
                self.attr_presented = True
                self.attr = query['CLI']

        return self.attr_presented, self.attr

    def get_attribute(self):

        if type(self.attr) is str:
            return [self.attr]
        else:
            return self.attr

