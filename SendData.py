# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:19:24 2014

@author: vartiai6
"""

import socket
import sys
import struct
import xml.etree.ElementTree as ET



# Create example XML

request = ET.Element("request")
imagesub = ET.SubElement(request,"image")

widthsub = ET.SubElement(imagesub,"width")
widthsub.text = "768"

heightsub = ET.SubElement(imagesub,"height")
heightsub.text = "576"

XML = ET.ElementTree(request)
#XML.write("try.xml")



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# Connect the socket to the port where the server is listening

server_address = ('130.230.177.59', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

print server_address

try:
    
    # Send data
    message = ET.tostring(request)
    
    print [elem.encode("hex") for elem in message]
    
    messagelength = len(message)
    print messagelength
    sendlength = struct.Struct('<L')
    
    #YLIVUOTO???
    
    packedlength = sendlength.pack(messagelength)
    
    
    print "Sending length of message: %i" % messagelength
    sock.sendall(packedlength)
    print "Sending the message"
    sock.sendall(message)
    print "Message sent"

#    
#    amount_received = 0
#    amount_expected = len(message)
#    
#    while amount_received < amount_expected:
#        data = sock.recv(16)
#        amount_received += len(data)
#        print >>sys.stderr, 'received "%s"' % data

finally:
    print >>sys.stderr, 'Closing socket'
    sock.close()