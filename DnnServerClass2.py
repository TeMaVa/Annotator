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

import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        
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
        while unpacked_length > sys.getsizeof(rdata):
            self.data = self.request.recv(1024).strip()
            print self.data
            rdata = rdata.join(self.data)
            print rdata
            
        
        if (unpacked_length != sys.getsizeof(rdata)):
            print "Package incomplete"
        
        
        XML = ET.fromstring(rdata)
        print XML
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
    print "serve"
    server.serve_forever()

    