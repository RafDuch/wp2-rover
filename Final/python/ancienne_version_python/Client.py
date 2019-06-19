import types
import socket
import sys
import selectors
import time
from _thread import start_new_thread
import MainRover
import subprocess

class Client:

    def __init__(self, main_rover):
        self.sel = selectors.DefaultSelector()
        self.msgOut = {}
        self.msgOutBox = []
        self.ip_server = '192.168.43.160'
        self.port = 65431
        self.msg = ''
        self.msgSent = True
        self.msgKeys = ['roverID','msgType','dataSize','data']
        self.main_rover = main_rover


    def fill_box(self):
        while True:
            #subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", "img.jpg"])
            f1 = open('img.jpg', 'rb')
            f2 = open('data.txt', 'rb')
            data1 = f1.read()
            data2 = f2.read()
            dataSize1 = str(len(data1))
            dataSize2 = str(len(data2))
            while len(dataSize1) < 9:
                dataSize1 = '0' + dataSize1
            while len(dataSize2) < 9:
                dataSize2 = '0' + dataSize2
            self.msgOutBox = [
                {'roverID': b'000000004', 'msgType': b'000000001', 'dataSize': dataSize1.encode('utf-8'), 'data': data1},
                {'roverID': b'000000004', 'msgType': b'000000000', 'dataSize': dataSize2.encode('utf-8'), 'data': data2}]
            f1.close()
            f2.close()
            with open('test.txt','wb') as f3:
                f3.write(data1)
            time.sleep(2)


    def connect(self, serverIP, serverPort):
        server_addr = (serverIP, serverPort)
        print('Connecting to', server_addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        s.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(s, events, self.msgOutBox)
        print('Connected', server_addr)

    
    def start_connection(self):
        start_new_thread(self.fill_box, ())
        self.connect(self.ip_server, self.port)
        while True:
            events = self.sel.select(timeout=None)
            for key, mask in events:
                s = key.fileobj
                if len(self.msgOut) == 0 and len(self.msgOutBox) > 0:
                    self.msgOut = self.msgOutBox.pop()
                    i = 0
                    self.msgSent = True
                if mask & selectors.EVENT_READ:
                    instruction = s.recv(2048).decode("utf-8")
                    self.main_rover.sendInstruction(instruction)

                if mask & selectors.EVENT_WRITE:
                    if len(self.msgOut) > 0:
                        if self.msgSent == True:
                            self.msg = self.msgOut[self.msgKeys[i]]
                            i += 1
                        try:      
                            sent = s.send(self.msg)
                            self.msg = self.msg[sent:]
                            if len(self.msg) == 0:
                                self.msgSent = True
                            else:
                                self.msgSent = False
                        except socket.error:
                            print('Disconnected')
                            connected = False
                            s = socket.socket()
                            while not connected:
                                try:
                                    self.connect(self.ip_server, self.port)
                                    connected = True
                                    time.sleep(5)
                                except socket.error:
                                    time.sleep(1)
                        if i == 4 and self.msgSent == True:
                            self.msgOut = {}
                            i = 0
