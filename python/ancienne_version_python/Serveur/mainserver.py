import threading


from connectionrover import ConnectionRover
from connectionmatlab import ConnectionMatlab

sem = {}
nb_rovers = 5

for i in range(nb_rovers):
    sem[i] = threading.BoundedSemaphore(1)

conn_rover = ConnectionRover(sem)

conn_matlab = ConnectionMatlab(sem, conn_rover)


threading.Thread(target=conn_matlab.start_server).start()


conn_rover.start_server()
