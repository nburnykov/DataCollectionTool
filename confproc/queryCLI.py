class QueryCLI:
    def __init__(self, querydict):
        self.querydict = querydict
        self.attributepresented = False
        self.attribute = ''

    def isattributepresented(self):
        return self.attributepresented

    def findattributebyname(self, attribute):

        self.attributepresented = False
        self.attribute = ''
        for query in self.querydict:
            if query['ID'] == attribute:
                self.attributepresented = True
                self.attribute = query['CLI']

        return

    def getattribute(self):

        if type(self.attribute) is str:
            return [self.attribute]
        else:
            return self.attribute

