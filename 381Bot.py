import threading
import time
import json
import requests
import os

import subprocess
import ansible_runner

# To build the table at the en
from tabulate import tabulate

### teams Bot ###
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

import botSkills as skills

# Create  thread list
threads = list()
# Exit flag for threads
exit_flag = False


# Bot Details
bot_email = 'RParry-445Bot@webex.bot'
teams_token = 'MDQzYWZlMWMtZWJiMS00NDA1LTlmMjItNzg4NGYyNWExMzQ5NjU0YWEyNGMtNTk2_P0A1_9c947ef3-ba2a-406e-9976-6a57f8f739b7'
bot_url = "https://d092-97-91-82-207.ngrok.io"
bot_app_name = 'CNIT-381 Network Auto Chat Bot'

# Create a Bot Object
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},],
)
subprocess.run('./disasterMonitor.py', shell=True)


# Create a function to respond to messages that lack any specific command
# The greeting will be friendly and suggest how folks can get started.
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a friendly CSR1100v assistant .  ".format(
        sender.firstName
    )
    response.markdown += "\n\nSee what I can do by asking for **/help**."
    return response

def get_int_ips(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = ""
    if (incoming_msg.text.find('R1')!=-1):
        intf_list = skills.netconfshow ('192.168.56.102')
    elif (incoming_msg.text.find('R2')!=-1):
        intf_list = skills.netconfshow('192.168.56.106')

    if len(intf_list) == 0:
        response.markdown = "The requested information cannot be found"
    else:
        response.markdown = "Here is the list of interfaces with IPs I know. \n\n"
        response.markdown += intf_list
    return response

def get_run_conf(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = ""
    if (incoming_msg.text.find('R1')!=-1):
        intf_list = skills.get_run('192.168.56.102')
    elif (incoming_msg.text.find('R2')!=-1):
        intf_list = skills.get_run('192.168.56.106')

    if len(intf_list) == 0:
        response.markdown = "The requested information cannot be found"
    else:
        response.markdown = "Here is the running config. \n\n"
        response.markdown += intf_list
    return response

def get_eigrp_proto(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = ""
    if (incoming_msg.text.find('R1')!=-1):
        intf_list = skills.get_eigrp('192.168.56.102')
    elif (incoming_msg.text.find('R2')!=-1):
        intf_list = skills.get_eigrp('192.168.56.106')

    if len(intf_list) == 0:
        response.markdown = "The requested information cannot be found"
    else:
        response.markdown = "Here is the EIGRP protocol configuration \n\n"
        response.markdown += intf_list
    return response

def get_version_info(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = ""
    if (incoming_msg.text.find('R1')!=-1):
        intf_list = skills.get_version('R1')
    elif (incoming_msg.text.find('R2')!=-1):
        intf_list = skills.get_version('R2')

    if len(intf_list) == 0:
        response.markdown = "The requested information cannot be found"
    else:
        response.markdown = "Here is the version information \n\n"
        response.markdown += str(intf_list)
    return response

def get_ip_route(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = ""
    if (incoming_msg.text.find('R1')!=-1):
        intf_list = skills.get_routes('R1')
    elif (incoming_msg.text.find('R2')!=-1):
        intf_list = skills.get_routes('R2')

    if len(intf_list) == 0:
        response.markdown = "The requested information cannot be found"
    else:
        response.markdown = "Here is the version information \n\n"
        response.markdown += str(intf_list)
    return response

def config_EIGRP(incoming_msg):
    r = "a"
    r = ansible_runner.run(private_data_dir='/home/devasc/labs/devnet-src/sample-app/final', playbook='eigrp.yaml')
    if(r=="a"):
        return "EIGRP configuration failed!"
    return "EIGRP configured correctly"

def disRecov(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    response =  skills.disaster_recovery()
    return response

# Set the bot greeting.
bot.set_greeting(greeting)

# Add Bot's Commmands
bot.add_command("show interfaces", "List all interfaces and their IP addresses", get_int_ips)
bot.add_command("show run", "Displays the full running config for a device", get_run_conf)
bot.add_command("show eigrp", "Displays the EIGRP protocol configuration for a device", get_eigrp_proto)
bot.add_command("show version", "Displays the version information for a device", get_version_info)
bot.add_command("show ip route", "Displays the version information for a device", get_ip_route)
bot.add_command("config eigrp", "Configures eigrp on the target device", config_EIGRP)
bot.add_command("disaster recovery", "Recovers the VPN connection after a IP address change", disRecov)


# Every bot includes a default "/echo" command.  You can remove it, or any
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
