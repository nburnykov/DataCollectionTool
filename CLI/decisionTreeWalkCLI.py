import re
import datetime
from CLI.portScan import PortScan
from CLI.deviceConnection import DeviceConnection


class DecisionTreeWalkCLI:
    def __init__(self, hostdata, treedict, querydict):
        self.hostdata = hostdata
        self.__treedict__ = treedict
        self.querydict = querydict
        self.__processlog__ = []
        self.__currentclass__ = ''
        self.__savedqueryresult__ = {}
        self.__pathlist__ = []

        ps = PortScan(self.hostdata)
        if ps.issshopen() or ps.istelnetopen():
            self.__devconn__ = DeviceConnection(self.hostdata, ps.connectiontype)

            if not self.__devconn__.isconnected():
                self.__processlogadd__("Cannot connect to host: {}".format(hostdata['ip']))
                return

        if not hasattr(self, '__devconn__'):
            self.__processlogadd__("Telnet and SSH ports are closed. Exit")
            return

        self.__currentclass__ = 'clMainClass'
        self.__decisiontreewalk__()

    def __processlogadd__(self, msg):
        return self.__processlog__.append((str(datetime.datetime.now().time()), self.__currentclass__, msg))

    def __decisiontreewalk__(self):

        if self.__currentclass__ not in self.__treedict__:
            self.__processlogadd__("Target class {} is not found".format(self.__currentclass__))
            return

        dt = self.__treedict__[self.__currentclass__]
        self.__pathlist__.append((dt['folder'], dt['genericscript']))

        if 'query' in dt:

            q = dt['query']

            if q not in self.__savedqueryresult__:
                self.__processlogadd__("{} result is not found in cache, performing CLI command:".format(q))
                self.__processlogadd__("      Host: {}".format(hostdata['ip']))

                # TODO parse cli queries
                if q not in self.querydict:
                    self.__processlogadd__("Cannot find \"{}\" in queries list, check cliQueries.yaml")
                    return

                qlist = str(q).split(';')
                output = ''
                for s in qlist:
                    output += self.__devconn__.runcommand(s)



                with open(q+'.txt', 'w') as data_file:
                    data_file.write(output)



                        # TODO perform parsed CLI queries and save data to dict and files

            if 'parse' not in dt:
                self.__processlogadd__("\"query\" section exists but \"parse\" is not presented, "
                                       "use current folder \"{}\" and script \"{}\"".format(dt['folder'],
                                                                                            dt['genericscript']))
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
                self.__processlogadd__("Expressions aren't found, use current folder \"{}\" and script \"{}\""
                                       .format(dt['folder'], dt['genericscript']))
                return

            for targetClass in targetClassList:
                self.__decisiontreewalk__(dt, targetClass, self.hostdata)

        else:
            self.__processlogadd__("Query section is not presented, use current folder \"{}\" and script \"{}\""
                                   .format(dt['folder'], dt['genericscript']))


hostdata = {'ip': '10.171.18.201',
            'username': 'cisco',
            'password': 'cisco'}
