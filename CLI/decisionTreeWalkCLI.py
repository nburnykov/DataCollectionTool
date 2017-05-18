import datetime
import re

from CLI.deviceConnection import DeviceConnection
from CLI.portScan import PortScan
from confproc.queryCLI import QueryCLI
from confproc.yamlDecoder import yamlload


class DecisionTreeWalkCLI:
    def __init__(self, hostdata, treedict, querydict, savedqueryresult={}):
        self.hostdata = hostdata
        self.querydict = querydict
        self.__processlog__ = []
        self.__savedqueryresult__ = savedqueryresult
        self.__pathlist__ = []
        self.__portsopen__ = False
        self.__connected__ = False
        self.__treeconfigerror__ = False
        self.__targetclasslist__ = []
        self.__currentclass__ = 'None'
        self.__test_string__ = ''

        # TODO implement host ping

        if self.__savedqueryresult__ == {}:     # if not - test mode

            ps = PortScan(self.hostdata)
            if ps.issshopen() or ps.istelnetopen():
                self.__portsopen__ = True
                self.__devconn__ = DeviceConnection(self.hostdata, ps.connectiontype)

                if not self.__devconn__.isconnected():
                    self.__processlogadd__("Cannot connect to host: {}".format(hostdata['ip']))
                    return

            if not hasattr(self, '__devconn__'):
                self.__processlogadd__("Telnet and SSH ports are closed. Exit")
                return

            self.__connected__ = True

        self.__decisiontreewalk__('clMainClass', treedict)

    def __decisiontreewalk__(self, currentclass, treedict):

        if currentclass not in treedict:
            self.__processlogadd__("Target class {} is not found".format(currentclass))
            self.__treeconfigerror__ = True
            return

        dt = treedict[currentclass]
        self.__pathlist__.append((dt['folder'], dt['genericscript']))
        self.__test_string__ += dt['folder'] + " "
        self.__targetclasslist__.append(currentclass)
        self.__currentclass__ = currentclass

        if 'query' in dt:

            q = dt['query']

            if q not in self.__savedqueryresult__:
                self.__processlogadd__("{} result is not found in cache, performing CLI command:".format(q))
                self.__processlogadd__("      Host: {}".format(hostdata['ip']))

                qd = QueryCLI(self.querydict)
                qd.findattributebyname(q)
                if not qd.isattributepresented():
                    self.__processlogadd__("Cannot find \"{}\" in queries list, please check queriesCLI.yaml".format(q))
                    self.__treeconfigerror__ = True
                    return

                qlist = qd.getattribute()
                output = ''
                for s in qlist:
                    output += self.__devconn__.runcommand(s)

                # TODO handle write to file exceptions
                with open(q + '.txt', 'w') as data_file:
                    data_file.write(output)

                self.__savedqueryresult__[q] = output

            if 'parse' not in dt:
                self.__processlogadd__("\"query\" section exists but \"parse\" is not presented, "
                                       "use current folder \"{}\" and script \"{}\"".format(dt['folder'],
                                                                                            dt['genericscript']))
                self.__treeconfigerror__ = True
                return

            pq = dt['parse']

            targetClassList = []

            self.__processlogadd__(
                "Content of the current query {} in cache:\n{}\n".format(q, self.__savedqueryresult__[q]))

            for pqi in pq:

                regexp = re.compile(pqi['expression'], re.IGNORECASE)
                self.__processlogadd__("Expression \"" + pqi['expression'] + "\":")
                if len(regexp.findall(self.__savedqueryresult__[q])) > 0:
                    targetClassList.append(pqi['targetClass'])
                    self.__processlogadd__("      Found, proceed to next class: {}\n".format(pqi['targetClass']))
                else:
                    self.__processlogadd__("      Not found\n")

            if len(targetClassList) == 0:
                self.__processlogadd__("Expressions aren't found, using current folder \"{}\" and script \"{}\""
                                       .format(dt['folder'], dt['genericscript']))
                return

            for targetClass in targetClassList:
                self.__decisiontreewalk__(targetClass, dt)

        else:
            self.__processlogadd__("Query section is not presented, stopping recursive search, "
                                   "using current folder \"{}\" and script \"{}\""
                                   .format(dt['folder'], dt['genericscript']))

    def __processlogadd__(self, msg, cclass=''):
        if cclass == '':
            cclass = self.__currentclass__
        self.__processlog__.append((str(datetime.datetime.now().time()), cclass, msg))
        return

    def getpathlist(self):
        return self.__pathlist__

    def getlog(self):
        return self.__processlog__

    def isportsopen(self):
        return self.__portsopen__

    def isdeviceconnected(self):
        return self.__connected__

    def istreeconfigerror(self):
        return self.__treeconfigerror__

    def gettargetclasslist(self):
        return self.__targetclasslist__

    def getteststring(self):
        return str(self.__test_string__).strip(' ')



# hostdata = {'ip': '10.171.18.201',
#             'username': 'cisco',
#             'password': 'cisco'}
#
#
# td = yamlload("..\\decisionTreeCLI.yaml")
# qd = yamlload("..\\queriesCLI.yaml")
#
# dcw = DecisionTreeWalkCLI(hostdata, treedict=td, querydict=qd)
# #[print("[{}] {}".format(st2, st3)) for st1, st2, st3 in dcw.getlog()]
# print(dcw.getteststring())