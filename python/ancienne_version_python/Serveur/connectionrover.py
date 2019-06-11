from threading import BoundedSemaphore
import selectors
import socket
import types
import sys


class ConnectionRover:
    
    def __init__(self, sem):
        self.sem = sem
        self.sel = selectors.DefaultSelector()
        self.header = False
        self.rcvData = b''
        self.msgIn = {'roverID': 0, 'msgType': 0, 'dataSize': 0}
        self.msgSize = 0
        self.msgOut = []
        self.rover_id = 0
        self.roverIP = {'192.168.1.1': 1,
                        '127.0.0.1': 2,
                        '192.168.1.3': 3,
                        '192.168.43.208': 4,
                        '192.168.1.5': 5}


    def matlab_to_rover(self, message):
        self.msgOut = message

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            self.rcvData += sock.recv(2048)
            self.msgSize = len(self.rcvData)
            if self.msgSize >= 9 * 3 and self.header == False:
                self.msgIn['roverID'] = self.rcvData[0:9].decode('utf-8')
                self.msgIn['msgType'] = self.rcvData[9:18].decode('utf-8')
                self.msgIn['dataSize'] = self.rcvData[18:27].decode('utf-8')
                self.rover_id = int(self.msgIn['roverID'])
                with open('header.txt', 'w') as fHead:
                    fHead.write(self.msgIn['roverID'])
                self.rcvData = self.rcvData[9 * 3:]
                self.header = True
                self.msgSize = len(self.rcvData)
            elif self.header == True and self.msgSize > int(self.msgIn['dataSize']):
                if int(self.msgIn['msgType']) == 0:
                    with open('receivedTXT' + str(self.rover_id) + '.txt', 'wb') as fTxt:
                        self.sem[self.rover_id].acquire()
                        print('vou escrever')
                        fTxt.write(self.rcvData[0:int(self.msgIn['dataSize'])])
                        self.sem[self.rover_id].release()
                if int(self.msgIn['msgType']) == 1:
                    with open('receivedIMG'+ str(self.rover_id) +'.jpg', 'wb') as fImg:
                        self.sem[self.rover_id].acquire()
                        fImg.write(self.rcvData[0:int(self.msgIn['dataSize'])])
                        self.sem[self.rover_id].release()
                self.rcvData = self.rcvData[int(self.msgIn['dataSize']):]
                self.msgSize = len(self.rcvData)
                self.header = False

        if mask & selectors.EVENT_WRITE:
            if self.msgOut:
                if self.roverIP[data.addr[0]] == self.msgOut[1]:
                    sock.sendall(self.msgOut[0].encode('utf-8'))
                    self.msgOut = []

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def start_server(self):
        #host = '192.168.43.6'
        host = '127.0.0.1'
        port = 65431

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print('listening on', (host, port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        while True:
            events = self.sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask)
                    

