import re
import datetime
from CLI.portScan import PortScan

savedqueryresult = {}
pathlist = []
processlog=[]
hostobj = {'ip': '10.171.2.5', 'community': 'NTM'}


def decisionTreeWalkCLI(dtree, currentclass, hostdata):

    def dtProcessLog(msg):
        return processlog.append((str(datetime.datetime.now().time()), currentclass, msg))

    if currentclass not in dtree:
        dtProcessLog(currentclass + " is not found")
        return

    dt = dtree[currentclass]
    pathlist.append((dt['folder'], dt['genericscript']))

    if 'query' in dt:

        q = dt['query']

        if q not in savedqueryresult:
            dtProcessLog("{} result is not found in cache, try to perform CLI command:".format(q))
            dtProcessLog("      Host: {}".format(hostdata['ip']))
            ps = PortScan(hostdata)
            if ps.issshopen():
                pass
            elif ps.istelnetopen():
                pass
            else:
                dtProcessLog("Telnet and SSH ports are closed. Exit")
                return
            try:

                queryoid = next(
                    query for query in snmpqueries['snmpQuery'] if query['ID'] == q)['OID']
                queryres = snmpquery.getsnmpdata(hostdata['community'], hostdata['ip'], queryoid)
                savedqueryresult[q] = queryres[1]
            except IOError:
                dtProcessLog("Host {} is not found".format(hostdata['ip']))
                return
            except KeyError:
                dtProcessLog("Key {} is not found".format(q))
                return
            dtProcessLog("      Success")

        if 'parse' not in dt:
            dtProcessLog("\"query\" section exists but \"parse\" is not presented, "
                         "use current folder \"{}\" and script \"{}\"".format(dt['folder'], dt['genericscript']))
            return

        pq = dt['parse']

        targetClassList = []

        dtProcessLog("Content of the current query {} in cache:\n{}\n".format(q, savedqueryresult[q]))

        for pqi in pq:

            regexp = re.compile(pqi['expression'], re.IGNORECASE)
            dtProcessLog("Expression \"" + pqi['expression']+"\":")
            if len(regexp.findall(savedqueryresult[q])) > 0:
                targetClassList.append(pqi['targetClass'])
                dtProcessLog("      Found, proceed to next class: {}\n".format(pqi['targetClass']))
            else:
                dtProcessLog("      Not found\n")

        if len(targetClassList) == 0:
            dtProcessLog("Expressions aren't found, use current folder \"{}\" and script \"{}\""
                         .format(dt['folder'], dt['genericscript']))
            return

        for targetClass in targetClassList:
            decisionTreeWalkCLI(dt, targetClass, hostobj)

    else:
        dtProcessLog("Query section is not presented, use current folder \"{}\" and script \"{}\""
                     .format(dt['folder'], dt['genericscript']))



