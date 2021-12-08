## Project Overview
Hello and welcome to this project. In this project we are looking at implementing a Chatbot that utilizes Cisco WebEx and Python in order to monitor and configure network devices. 

## Project Setup

### Install Packages
There are several libraries that require installation for this project
``` 
pip3 install ansible
pip3 install ansible-runner
pip3 install genie
pip3 install xmltodict
pip3 install robot
pip3 install netmiko
```

### Bot Creation
This bot is implemented using Cisco WebEx as our interface with the network. To do this we registered a bot with WebEx and copied out its ID information. The bot interfaces with the WebEx API using these pieces of information to allow it to send messages using the WebEx platform.

### Python Script
We then started creating the bot using Python. The first important piece was entering the information the script will use when connecting into WebEx’s infrastructure. This information includes the bot’s email as well as the ID token for WebEx. This section also includes adding in the URL for the webhook. To start the webhook enter the command ```ngrok http 5000``` into a terminal line and copy the URL with https and ngrok.io. These values can be combined into one bot object for convenience.

This diagram gives a visual representation of this connected relationship between the code that is running the bot and the WebEx infrastructure it is using as a platform 
![Command Processing diagram](https://user-images.githubusercontent.com/93947961/145149447-934b86a0-2670-4dfd-8a5f-ea44b7b6f401.PNG)

## Bot Commands
The bot is equipped with a variety of skills that can be accessed using commands in WebEx. These skills cover a variety of monitoring commands and can even do some areas of configuration. There is also one disaster monitoring function that is always operational and watches for IP address changes that would cause the VPN connection to be dropped.

### Show Interfaces
```show interfaces <hostname> ```  
This skill is built on NetConf and can be used to display the current configuration of the devices interfaces. The command requires that the hostname of the device is specified. This skill gives many important details about the interface including its addressing, its status, as well as the number of packets entering and leaving the interface. Having easy access to this information is vital to troubleshooting network problems.

### Show Run
```show run <hostname> ```  
This skill is built on NetMiko and can be used to display the current running configuration of a device. The command requires that the hostname of the device is specified. This is a very important skill to have as being able to retrieve the running configuration is necessary for network troubleshooting. 

### Show Version
```show version <hostname> ```  
This skill is built on Genie while also utilizing the Robots Framework. This one is designed to display the current version information on the device. The command requires that the hostname of the device is specified. Because this skill uses the Robots Framework it functions quite a bit different than the rest of the skills. It uses a Robots script to query a device for its version information and saves it to a file. This file is then read by the python script and then sent out to the user. The Robots Framework is quite powerful and is able to pull large sets of information. This results in a heavily detailed output. 

### Show IP Route
```show ip route <hostname> ```  
This skill is built on Genie and can be used to display the routing table on a target device. The command requires that the hostname of the device is specified. This skill provides yet another important show command. The routing table is one of the most important parts of a router and it is therefore necessary for troubleshooting. Being able to quickly access this information can give a network engineer large amounts of information about how the network is function as well as the operations of routing protocols such as EIGRP or OSPF.

### Show EIGRP
```show eigrp <hostname>```  
This skill is built on NetMiko and can be used to display the current configuration of EIGRP on a device. The command requires that the hostname of the device is specified. This skill is designed around displaying the configuration and running information for EIGRP on a device. Most importantly this skill plays an important part of verifying the operations of the next skill.

### Config EIGRP
```config eigrp```  
This skill is built using Ansible and can be used to configure EIGRP on both devices in the network simultaneously. This is a useful skill to have as it greatly simplifies configuring the network. This skill is again unique as it runs an ansible playbook that is in an external YAML file. This skill also uses the ansible_runner library to run the playbook and have it return its status. 

All of these skills are called from the main python script which acts as a core for the many commands. These commands call functions from other scripts that runs and returns the required information to the python bot. This diagram visualizes this process and shows which scripts call each other. 
![Code Branching diagram](https://user-images.githubusercontent.com/93947961/145151072-76c10fde-2c86-49c5-8c3a-239893156dc6.PNG)

## Disaster Recovery
The router interfaces hosting the site-to-site VPN are prone to change as the company's ISP has not given them a static IP. This frequent change is problem causing as their VPN needs to be reconfigured each time. This is a time-consuming process and would be much more fitting on an automated process. To implement this the bot is equipped with a disaster monitoring and recover feature. Using a combination of Genie with Robots and NetMiko the bot is able to automatically detect when an address is changed and change the peer address used in on the other end of the VPN. This can save the company a significant amount of time and keep the network more reliable.

This diagram visualizes the process that the bot uses to monitor the IPs used in the VPN. The bot first records the current address being used in the VPN. It then waits 60 seconds and compares that stored address with the address that is now on the interface. If the two addresses match, then the address has not changed and the bot waits again. If the addresses are different then the bot updates the peer information in the VPN to repair the tunnel and then records the new address starting the process over again.
![Disaster Monitoring Process](https://user-images.githubusercontent.com/93947961/145150644-2a291cec-aa35-4f66-a1f5-cc75291d057f.PNG)
