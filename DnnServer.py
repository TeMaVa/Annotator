import socket
import threading
import struct
import xml.etree.ElementTree as ET

import numpy as np
import base64

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
    return mat, filename

def predict_proba(image):
    # TODO: call the classifier here
    return np.random.random((1,4))


def handle(connection):
    """read raw image data, convert it to numpy array, send to classifier,
    return classification result, close connection"""

    # first, read n_images
    data = connection.recv(1024).strip()
    XML = ET.fromstring(data)
    n_images = int(XML[0].text)

    print "Receiving {0} images.".format(n_images)

    # next_buffer holds the left-over data
    next_buffer = ""

    for i in range(n_images):

        # first 4 bytes designate message length
        if len(next_buffer) > 0:
            data = next_buffer[0:4]
            next_buffer = next_buffer[4:]

        else:
            data = connection.recv(4).strip()


        # Check if message length has been received correctly
        if len(data) != 4:
            print "ERROR: Message length not received correctly"
            connection.close()
            return

        sc = struct.Struct('<L')
        unpacked_length = sc.unpack(data)

        unpacked_length = long(unpacked_length[0])

        #print "Message length received:%i" % unpacked_length

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
        next_buffer = rdata[len(rdata)-(received-unpacked_length):]

        rdata = rdata[0:len(rdata)-(received-unpacked_length)]

        if (unpacked_length != len(rdata)):
            print "ERROR: Package incomplete"
            connection.close()
            return

        mat, filename = handleimage(rdata)
        p = predict_proba(mat)

        vekstring = p.tostring()
        encoded = base64.b64encode(vekstring)

        response = ET.Element("response")
        imagesub = ET.SubElement(request,"image_name")
        imagesub.text = filename

        probsub = ET.SubElement(request,"prob_vector_b64")
        probsub.text = encoded

        connection.sendall(ET.tostring(response))
        connection.close()

if __name__ == '__main__':
    HOST = ""
    PORT = 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    while True:
        s.listen(1)
        conn, addr = s.accept()
        print "Incoming connection from", addr
        t = threading.Thread(target=handle, args=(conn,))
        # threads responsibility is to handle the connection and close it
        t.start()

