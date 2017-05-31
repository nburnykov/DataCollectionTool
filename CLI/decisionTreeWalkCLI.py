import datetime
import re

from confproc.queryCLI import QueryCLI
from devproc.deviceConnection import DeviceConnection


class DecisionTreeWalkCLI:
    def __init__(self, hostdata: dict, connection: DeviceConnection, treedict: dict, querydict: dict) -> None:
        self.hostdata = hostdata
        self.querydict = querydict
        self.__processlog = []
        self._savedqueryresult = {}
        self._pathlist = []
        self._treeconfigerror = False
        self._targetclasslist = []
        self._currentclass = 'None'
        self._test_string = ''
        self._devconn = connection

        self._decisiontreewalk('clMainClass', treedict)

    def _decisiontreewalk(self, currentclass, treedict):

        if currentclass not in treedict:
            self._processlogadd("Target class {} is not found".format(currentclass))
            self._treeconfigerror = True
            return

        dt = treedict[currentclass]
        self._pathlist.append((dt['folder'], dt['genericscript']))
        self._test_string += dt['folder'] + " "
        self._targetclasslist.append(currentclass)
        self._currentclass = currentclass

        if 'query' in dt:

            q = dt['query']

            if q not in self._savedqueryresult:
                self._processlogadd("{} result is not found in cache, performing CLI command:".format(q))
                self._processlogadd("      Host: {}".format(self.hostdata['ip']))

                qd = QueryCLI(self.querydict)
                qd.findattributebyname(q)
                if not qd.isattributepresented():
                    self._processlogadd("Cannot find \"{}\" in queries list, please check queriesCLI.yaml".format(q))
                    self._treeconfigerror = True
                    return

                qlist = qd.getattribute()
                output = ''
                for s in qlist:
                    output += self._devconn.runcommand(s)

                # TODO handle write to file exceptions
                with open(q + '.txt', 'w') as data_file:
                    data_file.write(output)

                self._savedqueryresult[q] = output

            if 'parse' not in dt:
                self._processlogadd("\"query\" section exists but \"parse\" is not presented, "
                                       "use current folder \"{}\" and script \"{}\"".format(dt['folder'],
                                                                                            dt['genericscript']))
                self._treeconfigerror = True
                return

            pq = dt['parse']

            targetClassList = []

            self._processlogadd(
                "Content of the current query {0} in cache:\n===\n{1}\n===\n".format(q, self._savedqueryresult[q]))

            for pqi in pq:

                expr = pqi['expression']
                if type(expr) is str:
                    expr = [expr]
                isexprfound = False

                for e in expr:

                    regexp = re.compile(e, re.IGNORECASE)
                    self._processlogadd("Expression \"" + e + "\":")
                    if len(regexp.findall(self._savedqueryresult[q])) > 0:
                        isexprfound = True

                if isexprfound:
                    targetClassList.append(pqi['targetClass'])
                    self._processlogadd("      Found, proceed to next class: {}\n".format(pqi['targetClass']))
                else:
                    self._processlogadd("      Not found\n")

            if len(targetClassList) == 0:
                self._processlogadd("Expressions aren't found, using current folder \"{}\" and script \"{}\""
                                    .format(dt['folder'], dt['genericscript']))
                return

            for targetClass in targetClassList:
                self._decisiontreewalk(targetClass, dt)

        else:
            self._processlogadd("Query section is not presented, stopping recursive search, "
                                   "using current folder \"{}\" and script \"{}\""
                                .format(dt['folder'], dt['genericscript']))

    def _processlogadd(self, msg, cclass=''):
        if cclass == '':
            cclass = self._currentclass
        self.__processlog.append((str(datetime.datetime.now().time()), cclass, msg))
        return

    def getpathlist(self):
        return self._pathlist

    def getlog(self):
        return self.__processlog

    def istreeconfigerror(self):
        return self._treeconfigerror

    def gettargetclasslist(self):
        return self._targetclasslist

    def getteststring(self):
        return str(self._test_string).strip(' ')




