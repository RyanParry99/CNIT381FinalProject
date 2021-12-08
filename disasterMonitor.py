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

while True:
    print("\n\n ---------Waiting 60 Seconds---------\n\n") 
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