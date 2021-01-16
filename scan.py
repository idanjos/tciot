from bluepy.btle import Scanner, DefaultDelegate
import miband4_console as mibandConnect
import pika
import time
import os
import sys

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
        elif isNewData:
            pass

if not os.geteuid() == 0:
    sys.exit("\nOnly root can run this script\n")

scanner = Scanner().withDelegate(ScanDelegate())
matchList = list()

with open("keys.txt") as search:
    for line in search:
        line = line.lower().rstrip()  # remove '\n' at end of line
        matchList.append(line.split(" "))

while True:
    try:
        print("Scanning nearby devices... please wait")
        scanner.scan(10)
        print("-------------")
        devices =  scanner.getDevices()
        print("Devices MAC Address: " + str([x.addr for x in devices]))
        for device in devices:
            key = next((x[1] for x in matchList if x[0] == str(device.addr)), None)
            mibandConnect.connect(device.addr, key)
    except:
        print("Error with BLE scan: Trying again in 10s")
        time.sleep(10)
        scanner = Scanner().withDelegate(ScanDelegate())
