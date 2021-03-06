import socket
import threading
import struct
import xml.etree.ElementTree as ET
import sys

import numpy as np
import base64
import cv2

from NnforgeWrapper import Nnforge
from AutoNetWrapper import AutoNet

IMAGE_WIDTH = 768
IMAGE_HEIGHT = 288



class DummyClassifier(object):
    def __init__(self):
        pass

    def predict_proba(self, X):
        return np.random.random((X.shape[0], 4))

def handleimage(rawdata):
    """convert raw image data to numpy array."""
    XML = ET.fromstring(rawdata)

    imageElem = XML[0]
    imagenameElem = XML[1]
    filename = imagenameElem.text
    width = int(imageElem[0].text)
    height = int(imageElem[1].text)
    rawdata = imageElem[2].text
    decoded = base64.b64decode(rawdata)
    decoded = np.fromstring(decoded,dtype=np.uint8)

    mat = np.reshape(decoded, (height, width, 3))
    resized = cv2.resize(mat, (IMAGE_WIDTH, IMAGE_HEIGHT))
    return resized, filename


def handle(connection, clf):
    """read raw image data, convert it to numpy array, send to classifier,
    return classification result, close connection"""

    # first, read n_images
    data = connection.recv(512).strip()
    XML = ET.fromstring(data)
    n_images = int(XML[0].text)

    print "Receiving {0} images.".format(n_images)

    reply = 'k'
    connection.sendall(reply)

    X = []
    filenames = []
    # next_buffer holds the left-over data
    next_buffer = ""

    for i in range(n_images):

        # first 4 bytes designate message length
        if len(next_buffer) > 0:
            data = next_buffer[0:4]
            next_buffer = next_buffer[4:]
            # if parts of message length got spilled to next packet
            if len(data) < 4:
                # for some reason, the '\r' character gets skipped so we need to take that into account
                rem = connection.recv(4-len(data)-1)
                data = data+"\r"+rem

        else:
            data = connection.recv(4).strip()

        # Check if message length has been received correctly
        if len(data) != 4:
            print "ERROR: Message length not received correctly (length = {0})".format(len(data))
            connection.close()
            return

        sc = struct.Struct('<L')
        unpacked_length = sc.unpack(data)

        unpacked_length = long(unpacked_length[0])


        rdata = next_buffer
        recvalue = 1024
        received = 0
        while True:
            data = connection.recv(recvalue).strip()
            rdata = rdata + data
            received = len(rdata)
            #print "received: {0}".format(received)
            if received >= unpacked_length:
                break

        # store left-over data for next image (if any)
        next_buffer = rdata[unpacked_length:]
        #print "stored next_buffer:", repr(next_buffer)
        #sys.stdout.flush()

        rdata = rdata[0:unpacked_length]

        if (unpacked_length != len(rdata)):
            print "ERROR: Package incomplete"
            connection.close()
            return

        mat, filename = handleimage(rdata)
        mat = np.expand_dims(mat, axis=0)
        X.append(mat)
        filenames.append(filename)


    imagemat = np.vstack(X)
    # returns (n_images, 4) matrix
    p = clf.predict_proba(imagemat)
    print p.shape
    print p
    # send number of images in reply
    begin= ET.Element("begin")
    imagessub = ET.SubElement(begin,"images")
    imagessub.text = str(n_images)

    connection.sendall(ET.tostring(begin))
    connection.recv(1) # wait ack from client

    for i in range(n_images):
        vekstring = p[i].tostring()
        encoded = base64.b64encode(vekstring)

        response = ET.Element("response")
        imagesub = ET.SubElement(response,"image_name")
        imagesub.text = filenames[i]

        probsub = ET.SubElement(response,"prob_vector_b64")
        probsub.text = encoded

        # simulate network lag
        #time.sleep(np.random.exponential(3.0))

        messagelength = len(ET.tostring(response))
        sendlength = struct.Struct('<L')

        packedlength = sendlength.pack(messagelength)

        connection.sendall(packedlength)

        connection.sendall(ET.tostring(response))

    connection.close()

if __name__ == '__main__':
    
#    assert sys.argv[1] == "pylearn" or sys.argv[1] == "nnforge"
    HOST = ""
    PORT = 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    clf = []
    clfLock = threading.Lock()
    if sys.argv[1] == "nnforge":
        clf = Nnforge(lock=clfLock, isColor=False)
    else:
        clf = AutoNet(lock=clfLock)
    while True:
        s.listen(1)
        conn, addr = s.accept()

        print "Incoming connection from", addr
        t = threading.Thread(target=handle, args=(conn,clf))
        # threads responsibility is to handle the connection and close it
        t.start()

