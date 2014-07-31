# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:11:42 2014

@author: vartiai6
"""

import socket
import sys
import time
from multiprocessing import Process
import threading
import struct
import xml.etree.ElementTree as ET
import numpy as np
import base64
import cv2

import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        
        #receive number of images
        # first packet:
        # <begin>
        #   <images>n_images</images>
        # </begin>
        ####
        XML = ET.fromstring(packet)
        n_images = int(XML[0].text)
        ####

        self.data = self.request.recv(4).strip()
        imagenumber = int(self.data)        
        
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4).strip()
        print "Connection from {}:".format(self.client_address[0])
        
        
        
        # Check if message length has been received correctly
        if len(self.data) != 4:
            print "ERROR: Message length not received correctly"
            
        sc = struct.Struct('<L')
        unpacked_length = sc.unpack(self.data)
        
        #Necessary?
        unpacked_length = long(unpacked_length[0])
        
        print "Message length received:%i" % unpacked_length
        
        # rawdata luetaan np.array:ksi seuraavasti
        # kuvia tulee n_images kappaletta, joten kannattaa hoitaa silmukassa
        # XML = request-paketti
        ###
        imageElem = XML[0]
        width = int(imageElem[0].text)
        height = int(imageElem[1].text)
        rawdata = imageElem[2].text
        decoded = base64.b64decode(rawdata)
        l = len(decoded)
        arr = np.uint8(map(lambda lst: "".join(lst), map(list,zip(decoded[0:l:3], decoded[1:l:3], decoded[2:l:3]))))
        mat = np.reshape(arr, (height, width, 3))
        cv2.imshow('image',mat)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        ###

        rdata = ""
#                
        
        while unpacked_length > len(rdata):
            self.data = self.request.recv(1024).strip()
            print self.data
            rdata = rdata + self.data
            print rdata
             
        
        if (unpacked_length != len(rdata)):
            print "Package incomplete"
        
        
        XML = ET.fromstring(rdata)
        
        
        #XML.getroot.write("received.xml")
        #self.data = self.request.recv(4).strip()
        

    
    def handle_error(self):       
        print "EXCEPTION"

if __name__ == "__main__":
    
    
    HOST, PORT = "", 10000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "Server on"
    
    server.handle_request()

    