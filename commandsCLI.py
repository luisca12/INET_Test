from netmiko import ConnectHandler
from log import authLog

import traceback
import re
import os
import threading

shIntDes = "show interface description | inc CON|con"
shHostname = "show run | i hostname"
interface = ''

intPatt = r'[a-zA-Z]+\d+\/(?:\d+\/)*\d+'

shutDownInt = [
    f'interface {interface}',
    'shutdown'
]

def testINET(validIPs, username, netDevice):
    # This function is to take a show run

    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                try:
                    sshAccess.enable()
                    shHostnameOut = sshAccess.send_command(shHostname)
                    authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                    shHostnameOut = shHostnameOut.replace('hostname', '')
                    shHostnameOut = shHostnameOut.strip()
                    shHostnameOut = shHostnameOut + "#"
                
                    print(f"INFO: Taking a \"{shIntDes}\" for device: {validDeviceIP}")
                    shIntDesOut = sshAccess.send_command(shIntDes)
                    authLog.info(f"Automation successfully ran the command: {shIntDes}")
                    shIntDesOut1 = re.findall(intPatt, shIntDesOut)
                    authLog.info(f"The following interfaces were found under the command: {shIntDes}\n{shIntDesOut1}")

                    if shIntDesOut1:
                        for interface in shIntDesOut1:
                            interface = interface.strip()
                            print(f"INFO: Shutting down interface: {interface}, on device {validDeviceIP}")
                            authLog.info(f"Shutting down interface: {interface}, on device {validDeviceIP}")
                            shutDownInt[0] = f'interface {interface}'
                            shutDownIntOut = sshAccess.send_config_set(shutDownInt)
                            
                    with open(f"Outputs/{validDeviceIP}_Dot1x.txt", "a") as file:
                        file.write(f"User {username} connected to device IP {validDeviceIP}, configuration applied:\n\n")
                        file.write(f"{shHostnameOut}\n{dot1xConfigOut}\n")
                    
                except Exception as error:
                    print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                    authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
                    authLog.debug(traceback.format_exc(),"\n")
       
        except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.debug(traceback.format_exc(),"\n")
            with open(f"failedDevices.txt","a") as failedDevices:
                failedDevices.write(f"User {username} connected to {validDeviceIP} got an error.\n")
        
        finally:
            print(f"Outputs and files successfully created for device {validDeviceIP}.\n")
            print("For any erros or logs please check Logs -> authLog.txt\n")


def testINETThread(validIPs, username, netDevice):
    try:
        thread = threading.Thread(target=testINET, args=(validIPs, username, netDevice))
        thread.start()

    except Exception as error:
        print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
        authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
        authLog.debug(traceback.format_exc(),"\n")