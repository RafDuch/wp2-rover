from threading import BoundedSemaphore
import time
import socket
from connectionrover import ConnectionRover

class ConnectionMatlab:


    def __init__(self, sem, connection_rover):
        self.sem = sem
        self.connection_rover = connection_rover


    def permission_to_access_files(self, rover):
        self.sem[rover].acquire()


    def finished_access(self, rover):
        self.sem[rover].release()


    def start_server(self):
        host = '127.0.0.1'
        port = 13001
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        print('listening on', (host, port))

        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()

            try:
                print('connection from', client_address)

                while True:
                    data = connection.recv(64)
                    if data:
                        print("Data: %s" % data)

                        data = data.decode("utf-8")
                        data = data.split(' ')

                        if len(data) != 3:
                            print(data)
                            print('ERROR: Conneciton  Matlab')
                            break

                        type_connection = data[0]
                        instruction = data[1]
                        rover_id = int(data[2])

                        print('rover id: ', rover_id)

                        if type_connection == 'read':
                            if instruction == 'acquire':
                                self.permission_to_access_files(rover_id)
                                connection.send(str('ok').encode("utf-8"))
                                print("acquire")
                            elif instruction == 'release':
                                self.finished_access(rover_id)
                                print("release")
                        elif type_connection == 'send':
                            self.connection_rover.matlab_to_rover([instruction, rover_id])

                    else:
                        print("end connection")
                        break
            finally:
                connection.close()

