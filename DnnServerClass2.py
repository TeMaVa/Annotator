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

from xml.dom.minidom import parse,parseString

import numpy as np
import base64
import cv2


import SocketServer




def ImageInitialize(XMLstring):
    
#    minidom = parseString(XMLstring)
#    height = int(minidom.getElementsByTagName('height')[0].childNodes[0].data)
#    width = int(minidom.getElementsByTagName('width')[0].childNodes[0].data)
#    #rawdata?
#    rawdata = np.random.random(((height, width, 3)))
    
    XML = ET.fromstring(XMLstring)  
            
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
    cv2.waitKey()
    cv2.destroyAllWindows()
    ###            
    
    
    targetsize = [576,768]
    



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
        print "Connection from {}:".format(self.client_address[0])
        self.data = self.request.recv(1024).strip()
        XML = ET.fromstring(self.data)
        n_images = int(XML[0].text)
        ####
        
        for i in range(n_images):        
        
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(4).strip()
            
            # Check if message length has been received correctly
            if len(self.data) != 4:
                print "ERROR: Message length not received correctly"
                
            sc = struct.Struct('<L')
            unpacked_length = sc.unpack(self.data)
            
            #Necessary?
            unpacked_length = long(unpacked_length[0])
            
            print "Message length received:%i" % unpacked_length
            
    
            rdata = ""
            #HUONO VALINTA
            recvalue = 1024
            loopnumber = int(np.ceil((float(unpacked_length)/float(recvalue))))
            print loopnumber
             
            for i in range(loopnumber):
                self.data = self.request.recv(recvalue).strip()
                rdata = rdata + self.data
    
            print len(rdata)
            
            if (unpacked_length != len(rdata)):
                print "Package incomplete"
            
            ImageInitialize(rdata)
            
#        XML = ET.ElementTree(ET.fromstring(rdata))

        
#        XML.write("received.xml")
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

    