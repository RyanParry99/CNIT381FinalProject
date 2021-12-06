from ncclient import manager
import xml.dom.minidom
import xmltodict

m = manager.connect (
    host="192.168.56.102",
    port=830,
    username="cisco",
    password="cisco123!",
    hostkey_verify=False
)

getLoop="""
<filter>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Loopback0</name>
        </interface>
    </interfaces>
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Loopback0</name>
        </interface>
    </interfaces-state>
</filter>            
"""

netconf_reply=m.get(getLoop)
loopDetails=xmltodict.parse(netconf_reply.xml)["rpc-reply"]["data"]
loopConfig=loopDetails["interfaces"]["interface"]
loopInfo=loopDetails["interfaces-state"]["interface"]
print("\nInterface Details: ")
print(" IPv4 Address: {}".format(loopConfig["ipv4"]["address"]["ip"]))
print(" Type: {}".format(loopConfig["type"]["#text"]))
print(" MAC Address: {}".format(loopInfo["phys-address"]))
print(" Packets Input: {}".format(loopInfo["statistics"]["in-unicast-pkts"]))
print(" Packets Output: {}".format(loopInfo["statistics"]["out-unicast-pkts"]))
print(" Admin Status: {}".format(loopInfo["admin-status"]))
print(" Operational Status: {}".format(loopInfo["oper-status"]))

#Yes, you could print this information with Paramiko/Netmiko. It would be a little more advanced though because you would have to run a command, then parse it for your information
