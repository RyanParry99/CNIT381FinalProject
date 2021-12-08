import os
import sys
import requests
import json
from netmiko import ConnectHandler
import yaml
import robot


def get_ints(ip):
    router = {'device_type': 'cisco_ios', 'host': ip, 'username': 'cisco','password': 'cisco','port': 22, 'secret': 'cisco', 'verbose': True}
    connection = ConnectHandler(**router)
    connection.enable()
    output = connection.send_command('sh ip int br')
    return output

def get_run(ip):
    router = {'device_type': 'cisco_ios', 'host': ip, 'username': 'cisco','password': 'cisco','port': 22, 'secret': 'cisco', 'verbose': True}
    connection = ConnectHandler(**router)
    connection.enable()
    output = connection.send_command('sh run')
    return output

def get_eigrp(ip):
    router = {'device_type': 'cisco_ios', 'host': ip, 'username': 'cisco','password': 'cisco','port': 22, 'secret': 'cisco', 'verbose': True}
    connection = ConnectHandler(**router)
    connection.enable()
    output = connection.send_command('sh eigrp protocols')
    return output

def get_version(device):
    robot.run('robot_platform.robot')
    json_file_path = "platform_R1_platform_pts.json"

    with open(json_file_path, 'r') as j:
        output = json.loads(j.read())
    return json.dumps(output)


def get_routes(device):
    from genie import testbed
    testbed = testbed.load('testbed/routers.yml')
    device = testbed.devices[device]
    device.connect()
    output = device.parse('show ip route')
    return yaml.dump(output)

def netconfshow(ip):
    from ncclient import manager
    import xml.dom.minidom
    import xmltodict

    m = manager.connect (
        host=ip,
        port=830,
        username="cisco",
        password="cisco",
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
    output=""
    netconf_reply=m.get(getLoop)
    loopDetails=xmltodict.parse(netconf_reply.xml)["rpc-reply"]["data"]
    loopConfig=loopDetails["interfaces"]["interface"]
    loopInfo=loopDetails["interfaces-state"]["interface"]
    output+="\nInterface Details: "
    output+=" IPv4 Address: {}".format(loopConfig["ipv4"]["address"]["ip"])
    output+=" Type: {}".format(loopConfig["type"]["#text"])
    output+=" MAC Address: {}".format(loopInfo["phys-address"])
    output+=" Packets Input: {}".format(loopInfo["statistics"]["in-unicast-pkts"])
    output+=" Packets Output: {}".format(loopInfo["statistics"]["out-unicast-pkts"])
    output+=" Admin Status: {}".format(loopInfo["admin-status"])
    output+=" Operational Status: {}".format(loopInfo["oper-status"])
    return output


def disaster_recovery():
    import yaml
    from genie.libs.parser.iosxe.show_interface import ShowIpInterfaceBrief
    from genie import testbed
    import time
    import paramiko

    testbed = testbed.load('testbed/routers.yml')

    client=paramiko.SSHClient()
    r1={'hostname':'192.168.56.102','port':'22','username':'cisco','password':'cisco'}
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    r2 = testbed.devices['R2'] #connect to R2 with genie
    r2.connect()

    out = r2.parse("show interface GigabitEthernet2") #use genie to get device info
    start = yaml.dump(out['GigabitEthernet2']['ipv4']).find("ip:") #specifically grab the start of the ip line
    end = yaml.dump(out['GigabitEthernet2']['ipv4']).find("pre") #grab the end of the IP line
    oldIP = yaml.dump(out['GigabitEthernet2']['ipv4'])[start+4:end-3] #format the IP

    #print("\n\n ---------Waiting 60 Seconds---------\n\n")
    time.sleep(10) #wait for the IP to possibly change

    out = r2.parse("show interface GigabitEthernet2") #use genie to get device info
    start = yaml.dump(out['GigabitEthernet2']['ipv4']).find("ip:") #specifically grab the start of the ip line
    end = yaml.dump(out['GigabitEthernet2']['ipv4']).find("pre") #grab the end of the IP line
    currentIP = yaml.dump(out['GigabitEthernet2']['ipv4'])[start+4:end-3] #format the IP

    if currentIP != oldIP: #if r2's IP changed, R1's crypto map needs to change
        print("Current IP does not match former IP")
        client.connect(**r1,look_for_keys=True,allow_agent=False) #connect to R1 with paramiko
        shell=client.invoke_shell()
        time.sleep(1)
        shell.send('configure t\n')
        time.sleep(1)
        shell.send('crypto map Crypt 10 ipsec-isakmp\n') #update the crypto map to set a peer to the current ip
        time.sleep(1)
        shell.send('no set peer ' + oldIP + '\n')
        time.sleep(1)
        shell.send('set peer ' + currentIP + '\n')
        time.sleep(1)
        shell.send('end\n')
        time.sleep(1)
        client.close()
        oldIP = currentIP #update IPs for future comparisons
        return("Crypto Map updated")
    else:
        return("IP address has not changed")
