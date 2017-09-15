from pysnmp.hlapi import *
from confproc import fileProc

def getsnmpdata(community, host, oid, port=161):
    if oid['type'] == 'single':
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community, mpModel=1),
                   UdpTransportTarget((host, port)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid['OID'])))
        )

        if errorIndication:
            raise IOError(errorIndication)
        elif errorStatus:
            raise IOError('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            ls = []
            for varBind in varBinds:
                ls.append([x.prettyPrint() for x in varBind])
            return ls

    if oid['type'] == 'multiple':

        errorIndication, errorStatus, errorIndex, varBindTable = nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid['OID'])))

        if errorIndication:
            raise IOError(errorIndication)
        else:
            if errorStatus:
                raise IOError('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex) - 1] or '?'
                    )
                )
            else:
                ls = []
                for varBindTableRow in varBindTable:
                    ls.append([(name.prettyPrint(), val.prettyPrint()) for name, val in varBindTableRow])


def getoid(queryname):
    pass

oid = {'OID': '1.3.6.1.2.1.1.1.0', 'type': 'single'}
oid = {'OID': '1.3.6.1.4.1.9.9.23', 'type': 'multiple'}

snmpqueries = fileProc.yaml_load(file="..\\snmpQueries.json")
print(getsnmpdata('NTM', '10.171.18.203', oid))
print(getsnmpdata('NTM', '10.171.2.5', oid))
print(getsnmpdata('public', '10.171.254.105', oid))