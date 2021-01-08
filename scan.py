from bluepy.btle import Scanner, DefaultDelegate
import miband4_console as mibandConnect
import pika

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
        elif isNewData:
            pass

scanner = Scanner().withDelegate(ScanDelegate())
matchList = list()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

with open("keys.txt") as search:
    for line in search:
        line = line.lower().rstrip()  # remove '\n' at end of line
        matchList.append(line.split(" "))

while True:
    scanner.scan(10)
    print("-------------")
    devices =  scanner.getDevices()
    print([x.addr for x in devices])
    for device in devices:
        key = next((x[1] for x in matchList if x[0] == str(device.addr)), None)
        mibandConnect.connect(device.addr, key)

