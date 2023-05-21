# importamos las librerías necesarias y establecemos conexión
import sim  # librería para conectar con CoppeliaSim


def connect(port):
    # Establece la conexión a VREP
    # port debe coincidir con el puerto de conexión en VREP
    # retorna el número de cliente o -1 si no puede establecer conexión
    sim.simxFinish(-1)  # just in case, close all opened connections
    clientID = sim.simxStart('127.0.0.1', port, True, True, 2000, 5)  # Conectarse
    if clientID == 0:
        print("conectado a", port)
    else:
        print("no se pudo conectar")
    return clientID


def get_drone_pos(clientID, dron_handle):
    _, dron_pos = sim.simxGetObjectPosition(clientID, dron_handle, -1, sim.simx_opmode_blocking)
    return dron_pos[0], dron_pos[1], dron_pos[2]


def get_drone_orientation(clientID, dron_handle):
    _, orientation = sim.simxGetObjectOrientation(clientID, dron_handle, -1, sim.simx_opmode_blocking)
    return orientation[2]