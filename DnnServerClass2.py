# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:11:42 2014

@author: vartiai6
"""

import threading
from multiprocessing import Queue
import Queue as Kyy
import struct
import xml.etree.ElementTree as ET

import numpy as np
import base64
import cv2



import SocketServer


def showImage(mat):
    cv2.imshow('image',mat)
    cv2.waitKey()
    cv2.destroyAllWindows()

def classify(ims):
    """Once all images have been received, send them to classifier.
    input   : N x image_height x image_width matrix of images
    returns : N x n_classes matrix of probabilities"""
    pass

def putimage(XMLstring, queue):

    XML = ET.fromstring(XMLstring)

    imageElem = XML[0]
    width = int(imageElem[0].text)
    height = int(imageElem[1].text)
    rawdata = imageElem[2].text
    decoded = base64.b64decode(rawdata)
    decoded = np.fromstring(decoded,dtype=np.uint8)
    #print decoded[0:50]

    mat = np.reshape(decoded, (height, width, 3))

    queue.put(mat)

    print "image put to queue"
    #Resize image using openCV

    #targetsize = (192,144)
    #resized_image = cv2.resize(mat,targetsize)

    #cv2.imshow('image',resized_image)
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    ###







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
        print "Incoming connection from {}:".format(self.client_address[0])
        self.data = self.request.recv(1024).strip()
        XML = ET.fromstring(self.data)
        self.n_images = int(XML[0].text)
        self.threads = []
        self.queue = Queue()
        ####

        print "Receiving {0} images.".format(self.n_images)

        next_buffer = ""

        for i in range(self.n_images):

            if len(next_buffer) > 0:
                self.data = next_buffer[0:4]
                next_buffer = next_buffer[4:]
            # self.request is the TCP socket connected to the client

#            self.data = self.request.recv(4)

            else:
                self.data = self.request.recv(4).strip()


            # Check if message length has been received correctly
            if len(self.data) != 4:
                print "ERROR: Message length not received correctly"

            sc = struct.Struct('<L')
            unpacked_length = sc.unpack(self.data)

            #Necessary?
            unpacked_length = long(unpacked_length[0])

            #print "Message length received:%i" % unpacked_length


            rdata = next_buffer
            #HUONO VALINTA
            recvalue = 1024
            received = 0
            #loopnumber = int(np.ceil((float(unpacked_length)/float(recvalue))))
            #print "Loopnumber = {0}".format(loopnumber)


#            for i in range(loopnumber):
#                self.data = self.request.recv(recvalue)
#                self.data = self.data.strip()
#                rdata = rdata + self.data
#
#
#            while True:
#                self.data = self.request.recv(recvalue).strip()
#                if self.data == '':
#                    break
#                rdata = rdata + self.data

            #for i in range(loopnumber):

            while True:
                self.data = self.request.recv(recvalue).strip()
                rdata = rdata + self.data
                received = len(rdata)
                #print "received: {0}".format(received)
                if received >= unpacked_length:
                    break

            next_buffer = rdata[len(rdata)-(received-unpacked_length):]


#            print "next_buffer = {0}".format(next_buffer)


            rdata = rdata[0:len(rdata)-(received-unpacked_length)]



#            print "first 50 chars of received data:\n{0}".format(rdata[0:50])

#            print "last 50 chars of received data:\n{0}".format(rdata[-50:])
            

            #print "Length of received data: {0}".format(len(rdata))

            #print "first 50 chars of received data:\n{0}".format(rdata[0:50])

            #print "last 50 chars of received data:\n{0}".format(rdata[-50:])


            if (unpacked_length != len(rdata)):
                print "Package incomplete"

            t = threading.Thread(target=putimage, args=(rdata, self.queue))
            self.threads.append(t)
            t.start()
            print "sending image {0} to queue".format(i)

        print "All images processed."

        print "Length of queue: {0}".format(self.queue.qsize())
#        XML = ET.ElementTree(ET.fromstring(rdata))

        self.queue.close()
        self.queue.join_thread()
        # Close all threads.
        for t in self.threads:
            #print "attempting to join subprocess"
            t.join()

        #self.queue.close()

        self.mats = []
        while True:
            try:
                mat = self.queue.get()
                self.mats.append(mat)
            except Kyy.Empty:
                break
        self.ims = np.dstack(self.mats)
        print "resulting matrix shape: {0}".format(self.ims.shape)

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


