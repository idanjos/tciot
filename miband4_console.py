#!/usr/bin/env python3

# This script demonstrates the usage, capability and features of the library.

import argparse
import subprocess
import time
from datetime import datetime

from bluepy.btle import BTLEDisconnectError
from miband import miband
import pika
import logging

channel = None
connection = None

def connect(mac_addr, auth_key = None):
    global channel
    global connection
    MAC_ADDR = mac_addr
    AUTH_KEY = str(auth_key)
    # Validate MAC address
    if 1 < len(MAC_ADDR) != 17:
        print("Error:")
        print("  Your MAC length is not 17, please check the format")
        print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
        return False
    
    # Validate Auth Key
    if auth_key != None:
        if 1 < len(AUTH_KEY) != 32:
            print("Error:")
            print("  Your AUTH KEY length is not 32, please check the format")
            return False

    # Convert Auth Key from hex to byte format
    if auth_key != None:
        AUTH_KEY = bytes.fromhex(AUTH_KEY)
    
    try:
        band = None
        if (AUTH_KEY):
            band = miband(MAC_ADDR, AUTH_KEY, debug=True)
            success = band.initialize()
            if success:
                try:
                    logging.getLogger("pika").propagate = False
                    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                    channel = connection.channel()
                except: 
                    pass
                get_activity_logs(band)
        else:
            band = miband(MAC_ADDR, debug=True)
            get_activity_logs(band)
    except Exception as ex:
        print("Error in device: %s", MAC_ADDR)
        print(ex)
        if type(band) is miband:
            band.disconnectDevice()
        return False

    if type(band) is miband:
        band.disconnectDevice()
    
    if connection != None:
        connection.close()

    return True
        
def activity_log_callback(timestamp,c,i,s,h,m):
    global channel
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body='{"id": 2, "size": 50, "raw":"{}: category: {}; intensity {}; steps {}; heart rate {}; mac {}"}'.format( timestamp.strftime('%d.%m - %H:%M'), c, i ,s ,h,m))
    print("{}: category: {}; intensity {}; steps {}; heart rate {}; mac {};\n".format( timestamp.strftime('%d.%m - %H:%M'), c, i ,s ,h,m))

def activity_log_callback_print(timestamp,c,i,s,h,m):
    print("{}: category: {}; intensity {}; steps {}; heart rate {}; mac {};\n".format( timestamp.strftime('%d.%m - %H:%M'), c, i ,s ,h,m))

#Needs auth    
def get_activity_logs(band):
    global channel
    temp = datetime.now()
    if channel != None:
        band.get_activity_betwn_intervals(datetime(temp.year,temp.month,temp.day),datetime.now(),activity_log_callback)
    else:
        band.get_activity_betwn_intervals(datetime(temp.year,temp.month,temp.day),datetime.now(),activity_log_callback_print)

    while band.waitForNotifications(5):
        pass