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

import SocketServer


import numpy


def ImageInitialize(XMLstring):
    
    minidom = parseString(XMLstring)
    height = int(minidom.getElementsByTagName('height')[0].childNodes[0].data)
    width = int(minidom.getElementsByTagName('width')[0].childNodes[0].data)
    #rawdata?
    rawdata = numpy.random.random(((height, width, 3)))
    
    targetsize = [576,768]
    



class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        
        #RECEIVE IMAGE NUMBER

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
        
                
        
        rdata = ""
#                
        
        #HUONO VALINTA
            
        while unpacked_length > len(rdata):
            self.data = self.request.recv(1024).strip()
            print self.data
            rdata = rdata + self.data
            print rdata
             
        
        if (unpacked_length != len(rdata)):
            print "Package incomplete"
        
        
        XML = ET.ElementTree(ET.fromstring(rdata))
        
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

    