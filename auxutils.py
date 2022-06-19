import socket
import logging
import pprint
import time
import json
import socket
import struct
import binascii
from datetime import datetime
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import figure
import numpy as np
from influxdb import InfluxDBClient


def getFormattedTime(dateTimeObj):
    f = '%Y-%m-%d %H:%M:%S'
    return dateTimeObj.strftime(f)

def ip_header(data):
    storeobj=struct.unpack("!BBHHHBBH4s4s", data)
    _version=storeobj[0]
    _tos=storeobj[1]
    _total_length =storeobj[2]
    _identification =storeobj[3]
    _fragment_Offset =storeobj[4]
    _ttl =storeobj[5]
    _protocol =storeobj[6]
    _header_checksum =storeobj[7]
    _source_address =socket.inet_ntoa(storeobj[8])
    _destination_address =socket.inet_ntoa(storeobj[9])

    data={'Version':_version,
    "Tos":_tos,
    "Total Length":_total_length,
    "Identification":_identification,
    "Fragment":_fragment_Offset,
    "TTL":_ttl,
    "Protocol":_protocol,
    "Header CheckSum":_header_checksum,
    "Source Address":_source_address,
    "Destination Address":_destination_address}
    return data

def eth_header(data):
    storeobj = data
    storeobj = struct.unpack("!6s6sH", storeobj)
    destination_mac = binascii.hexlify(storeobj[0])
    source_mac = binascii.hexlify(storeobj[1])
    eth_protocol = storeobj[2]
    data = {"Destination Mac": destination_mac,
    "Source Mac": source_mac,
    "Protocol": eth_protocol}
    return data

# UDP Header Extraction


def udp_header(data):
    storeobj = struct.unpack('!HHHH', data)
    source_port = storeobj[0]
    dest_port = storeobj[1]
    length = storeobj[2]
    checksum = storeobj[3]
    data = {"Source Port": source_port,
    "Destination Port": dest_port,
    "Length": length,
    "CheckSum": checksum}
    return data


def getAccel(data, l_range, name):
    struc_txt = ""
    for i in range(l_range):
        struc_txt = struc_txt + 'B'

    storeobj = struct.unpack(struc_txt, data)

    data = {}
    for i in range(l_range):
        data.update({name + str(i): (storeobj[i] / 16000) * 386.08858267716})

    return data

def getSingleReads(data):
    storeobj = struct.unpack("HHHH", data)

    data = {}
    names = ["temp", "humidity", "temp_case", "bat"]

    for i in range(4):
        data.update({names[i]: storeobj[i] / 100})

    return data

def getDebugReads(data):
    storeobj=struct.unpack("h", data)

    data= {}
    names = ["RSSI dB"]
    for i in range(1):
        data.update( {names[i] :storeobj[i]} )
    return data

def getUnix(data):
    print(data)
    storeobj = struct.unpack("BBBB", data)
    unix = ( (storeobj[0] << 24)
                   + (storeobj[1] << 16)
                   + (storeobj[2] << 8)
                   + (storeobj[3] ) )
    return {"unix" : unix }

def writePkt1(pkt1):

    # write header info
    tags = eth_header(pkt1[0][0:14])
    tags.update(ip_header(pkt1[0][14:34]))
    tags.update(udp_header(pkt1[0][34:42]))

    # Converting datetime object to string
    unix = getUnix(pkt1[0][1074:1078])
    tags.update(unix)
    #dateTimeObj = datetime.fromtimestamp(unix["unix"])

    # Get ax and ay measurements
    ax_fft = getAccel(pkt1[0][50:562], 512,"ax")
    ay_fft = getAccel(pkt1[0][562:1074], 512 ,"ay")

    # update all feilds
    fields = getSingleReads(pkt1[0][42:50])
    fields.update(ax_fft)
    fields.update(ay_fft)

    client = InfluxDBClient('34.69.157.244', 8086, 'root', 'root', 'sensors')

    json_body = [
        {
            "measurement": "packet1",
            "tags": tags,
            "time": unix["unix"]*1000,
            "fields": fields
        }
    ]
    client.write_points(json_body)
    result = client.query('SELECT * from packet1 ORDER by time DESC LIMIT 1;')
    print(unix["unix"]*1000)
    #print(result)

def writePkt2(pkt2):
    # write header info
    tags = eth_header(pkt2[0][0:14])
    tags.update(ip_header(pkt2[0][14:34]))
    tags.update(udp_header(pkt2[0][34:42]))

    # Get UNIX Time (Add some checks in here)
    unix = getUnix(pkt2[0][1068:1072])
    tags.update(unix)
    #dateTimeObj = datetime.fromtimestamp(unix["unix"])

    # Write az and sound
    az_fft = getAccel(pkt2[0][42:554], 512,"az")
    sound = getAccel(pkt2[0][554:1066], 512 ,"sound")

    # update fields
    fields = az_fft
    fields.update(sound)

    # add debug info to tags
    debug = getDebugReads(pkt2[0][1066:1068])
    tags= debug

    # Send packets
    client = InfluxDBClient('34.69.157.244', 8086, 'root', 'root', 'sensors')
    json_body = [
        {
            "measurement": "packet2",
            "tags": tags,
            "time": unix["unix"]*1000,
            "fields": fields
        }
    ]
    client.write_points(json_body)
    result = client.query('SELECT * from packet2 ORDER by time DESC LIMIT 1;')
    print(unix["unix"]*1000)
    #print(json_body)