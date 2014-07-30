#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:19:24 2014

@author: vartiai6, lehmusvj
"""

import socket
import sys
import struct
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import base64

def sendImagesAsXML(files):
    """
    Reads each image file in a list and sends contents over network
    files : list of file names
    returns : nothing
    """
    for filename in files:
        img = cv2.imread(filename, cv2.IMREAD_COLOR)
        if img == None:
            raise IOError("could not read image "+filename)
        vek = np.reshape(img, img.shape[0]*img.shape[1]*img.shape[2])
        # work out base64

if __name__ == '__main__':

    # [filename]
    unsupervisedAnnotFile = sys.argv[1]
    f = open(unsupervisedAnnotFile, "r")
    fl = [line if len(line) > 0 for line in list(f)]

    # Create example XML

    request = ET.Element("request")
    imagesub = ET.SubElement(request,"image")

    widthsub = ET.SubElement(imagesub,"width")
    widthsub.text = "768"

    heightsub = ET.SubElement(imagesub,"height")
    heightsub.text = "576"

    rawdatasub = ET.SubElement(imagesub,"rawdata")
    rawdatasub.text = "TÄHÄN KUVADATA"

    XML = ET.ElementTree(request)
    #XML.write("try.xml")



    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    # Connect the socket to the port where the server is listening

    server_address = ('130.230.177.59', 10000)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    print server_address

    # send number of images to classify
    # <begin>
    #   <images>200</images>
    # </begin>

    begin= ET.Element("begin")
    imagessub = ET.SubElement(begin,"images")
    imagessub.text = str(len(fl))

    sock.sendall(ET.tostring(begin))

    # wait for ok from server, send images, read prediction in separate thread

    sendImagesAsXML(fl)



    try:
        
        # Send data
        message = ET.tostring(request)
        
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