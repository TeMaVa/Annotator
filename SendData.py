#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:19:24 2014

@author: vartiai6, lehmusvj
"""

import socket
import sys
import struct
import threading
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import base64

lock = threading.Lock()

def sendImageAsXML(filename, socket):
    """
    Read image file and send contents over network
    filename : filename of image
    socket   : where to send data
    returns  : nothing
    """

    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    if img == None:
        raise IOError("could not read image "+filename)

    height = img.shape[0]
    width = img.shape[1]
    vek = np.reshape(img, img.shape[0]*img.shape[1]*img.shape[2])
    vekstring = vek.tostring()
    encoded = base64.b64encode(vekstring)


    request = ET.Element("request")
    imagesub = ET.SubElement(request,"image_data")

    widthsub = ET.SubElement(imagesub,"width")
    widthsub.text = str(width)

    heightsub = ET.SubElement(imagesub,"height")
    heightsub.text = str(height)

    rawdatasub = ET.SubElement(imagesub,"rawdata")
    rawdatasub.text = encoded

    imagenamesub = ET.SubElement(request,"image_name")
    imagenamesub.text = filename

    messagelength = len(ET.tostring(request))
    #print messagelength
    sendlength = struct.Struct('<L')

    packedlength = sendlength.pack(messagelength)

    #print "Sending length of message: %i" % messagelength
    sock.sendall(packedlength)

    sock.sendall(ET.tostring(request))

def handlereply(sock, outputH, pipe, N_images, image_n):
    """this function waits for the reply from the server,
    writes result to output file
    and then closes the connection."""
    # wait for reply
    data = sock.recv(1024).strip()
    #print "received reply: {0}".format(data)

    XML = ET.fromstring(data)

    imagenameElem = XML[0]
    probElem = XML[1]
    filename = imagenameElem.text
    rawdata = probElem.text
    decoded = base64.b64decode(rawdata)
    vek = np.fromstring(decoded)
    veks = ",".join([str(elem) for elem in vek])
    #print "received vector:", vek
    with lock:
        outputH.write(filename+","+veks+"\n")
        pipe.write("{0}/{1} classified\n".format(image_n, N_images))


    sock.close()

if __name__ == '__main__':

    server_address = ("localhost", 10000)
    #server_address = ('130.230.177.59', 10000)


    # [(filename, class_label)]
    annotFile = sys.argv[1]
    f = open(annotFile, "r")
    fl = filter(lambda line: len(line) > 0, [line.split(",")[0] for line in list(f)])
    N_images = len(fl)
    image_n = 0

    fo = open(sys.argv[2], "w");

    fifoname = "/tmp/DNNFIFO"
    pipe = open(fifoname, "w")

    # send each image as a new connection, read the response
    for filename in fl:
        image_n = image_n + 1
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        # send number of images to classify
        begin= ET.Element("begin")
        imagessub = ET.SubElement(begin,"images")
        imagessub.text = str(1)

        #print "sending n_images {0} of length {1}".format(ET.tostring(begin), len(ET.tostring(begin)))
        sock.sendall(ET.tostring(begin))

        #print "sending", filename
        # send the image
        sendImageAsXML(filename, sock)

        t = threading.Thread(target=handlereply, args=(sock,fo,pipe,N_images,image_n))
        t.start()
