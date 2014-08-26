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
import itertools

lock = threading.Lock()

def sendImagesAsXML(filenames, socket):
    """
    Read image files and send contents over network
    filenames : filename of image
    socket    : where to send data
    returns   : nothing
    """


    for filename in filenames:
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

        #print "Length of message length: %i" % len(packedlength)
        sock.sendall(packedlength)

        sock.sendall(ET.tostring(request))

def handlereply(sock, outputH, pipe, N_images, image_n):
    """This function waits for the reply from the server,
    writes results to output file, and then closes the connection.
    sock     = socket to server
    outputH  = prediction file handle (read by Visualizer)
    pipe     = named pipe to Visualizer (used to update status)
    N_images = how many images there are in total
    image_n  = first image of this packet"""

    # receive n_images
    data = sock.recv(512).strip()
    print "received data:", data
    XML = ET.fromstring(data)
    n_images = int(XML[0].text)

    print "Receiving a reply of {0} images.".format(n_images)

    reply = 'k'
    sock.sendall(reply)

    vektors = []
    filenames = []
    # next_buffer holds the left-over data
    next_buffer = ""

    for i in range(n_images):

        # first 4 bytes designate message length
        if len(next_buffer) > 0:
            data = next_buffer[0:4]
            next_buffer = next_buffer[4:]

        else:
            data = sock.recv(4).strip()

        # Check if message length has been received correctly
        if len(data) != 4:
            print "ERROR: Message length not received correctly"
            sock.close()
            return

        sc = struct.Struct('<L')
        unpacked_length = sc.unpack(data)

        unpacked_length = long(unpacked_length[0])

        #print "Message length received:%i" % unpacked_length

        rdata = next_buffer
        recvalue = 1024
        received = 0
        while True:
            data = sock.recv(recvalue).strip()
            rdata = rdata + data
            received = len(rdata)
            #print "received: {0}".format(received)
            if received >= unpacked_length:
                break

        # store left-over data for next image (if any)
        next_buffer = rdata[len(rdata)-(received-unpacked_length):]

        rdata = rdata[0:len(rdata)-(received-unpacked_length)]

        if (unpacked_length != len(rdata)):
            print "ERROR: Package incomplete"
            sock.close()
            return

        XML = ET.fromstring(rdata)
        imagenameElem = XML[0]
        probElem = XML[1]
        filename = imagenameElem.text
        filenames.append(filename)
        rawdata = probElem.text
        decoded = base64.b64decode(rawdata)
        vek = np.fromstring(decoded)
        veks = ",".join([str(elem) for elem in vek])
        vektors.append(veks)

    # write prediction values to .csv, and report classification
    # status to Visualizer
    with lock:
        for i in range(len(filenames)):
            outputH.write(filenames[i]+","+vektors[i]+"\n")
            pipe.write("{0}/{1} classified\n".format(image_n, N_images))
        pipe.flush()


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

    # divide input images into how many groups
    N_PACKETS = int(sys.argv[3])
    keyfunc = lambda x: x % N_PACKETS
    indexList = sorted(range(len(fl)), key=keyfunc)
    indexGroups = []
    for k, g in itertools.groupby(indexList, keyfunc):
        indexGroups.append(list(g))
    filename_arr = np.array(fl)

    # send each group individually
    for group in indexGroups:
        #print "group:", group
        images = filename_arr[group]
        image_n = image_n + len(images)
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        # send number of images to classify
        begin= ET.Element("begin")
        imagessub = ET.SubElement(begin,"images")
        imagessub.text = str(len(images))

        #print "sending n_images {0} of length {1}".format(ET.tostring(begin), len(ET.tostring(begin)))
        sock.sendall(ET.tostring(begin))
        sock.recv(1) # number of images received

        #print "sending", filename
        # send the image
        sendImagesAsXML(images, sock)

        t = threading.Thread(target=handlereply, args=(sock,fo,pipe,N_images,image_n))
        t.start()

