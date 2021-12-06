import os
import sys
### For RESTCONF
import requests
import json
from netmiko import ConnectHandler
import yaml



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
    from genie import testbed
    testbed = testbed.load('testbed/routers.yml')
    device = testbed.devices[device]
    device.connect()
    output = device.parse('show version')
    return yaml.dump(output)

def get_routes(device):
    from genie import testbed
    testbed = testbed.load('testbed/routers.yml')
    device = testbed.devices[device]
    device.connect()
    output = device.parse('show ip route')
    return yaml.dump(output)