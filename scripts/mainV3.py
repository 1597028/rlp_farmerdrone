import math
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
import warnings
warnings.filterwarnings("ignore")

import sim
from utils import connect
from utils import get_drone_pos
from utils import get_drone_orientation

greenBajo = np.array([45, 100, 20], np.uint8)
greenAlto = np.array([75, 255, 255], np.uint8)

# HAY QUE TENER UNA FOTO DEL CESPED MOJADO ANTES!!
def takePhoto(cam, option, x):
    if (option == 0):
        if (x >= x_min_huerto):
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])
            # plt.imshow(imgInicial)
            # plt.show()

            imgWet = cv2.imread('mojau.jpg')
            imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)
            # plt.imshow(imgWet)
            # plt.show()

            imgRes = cv2.absdiff(imgInicial, imgWet)

            mean = np.mean(imgRes)
            print(mean)

            if (mean >= 45):
                print("Huerto seco!\n")
            else:
                print("Huerto mojado!\n")
    if (option == 1):
        if (x >= x_min_huerto):
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])
            # plt.imshow(imgInicial)
            # plt.show()

            hsv = cv2.cvtColor(imgInicial, cv2.COLOR_RGB2HSV)
            maskGreen = cv2.inRange(hsv, greenBajo, greenAlto)
            maskGreenVis = cv2.bitwise_and(
                imgInicial, imgInicial, mask=maskGreen)
            #cv2.imshow('frame', imgInicial)
            #cv2.imshow('maskRed', maskGreen)
            #cv2.imshow('maskRedvis', maskGreenVis)
            # cv2.waitKey(0)

            if (np.mean(maskGreenVis) > 0):
                imgWet = cv2.imread('mojau.jpg')
                imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)
                # plt.imshow(imgWet)
                # plt.show()

                imgRes = cv2.absdiff(imgInicial, imgWet)

                mean = np.mean(imgRes)
                print(mean)

                if (mean >= 45):
                    print("Huerto seco!\n")
                else:
                    print("Huerto mojado!\n")


def moveDron(option):
    if (option == 0 or option == 1):
        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(clientID, dron_handle)

        new_x = list(np.arange(dron_pos_x, x_min_huerto, step=x_step))
        for x in new_x:
            time.sleep(0.05)
            sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                      sim.simx_opmode_blocking)
        dron_pos_x = x_min_huerto
        while dron_pos_y < y_max_huerto:

            new_x = list(np.arange(dron_pos_x, x_max_huerto, step=x_step))
            new_y = list(
                np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
            if dron_pos_x < (x_max_huerto - threshold):  # Ida dron

                # Cada 12 tics la camara encuentra un cuadrado totalmente nuevo
                i = 12
                for x in new_x:
                    if (i % 12 == 0):
                        takePhoto(cam, option, x)
                    time.sleep(0.05)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                              sim.simx_opmode_blocking)
                    i += 1

                # set variables
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(90), step=0.05))
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)
                # Llega final x rotar izquierda
                for angle in angle_rot:
                    time.sleep(0.05)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                # Mover hacia y
                for y in new_y:
                    time.sleep(0.05)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                              sim.simx_opmode_blocking)

                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(180), step=0.05))
                # final avance rotar izquierda
                for angle in angle_rot:
                    time.sleep(0.05)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

            # vuelta dron
            if dron_pos_x > (x_min_huerto - threshold):
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                new_x = list(np.arange(dron_pos_x, x_min_huerto, step=-x_step))

                i = 12
                for x in new_x:
                    if (i % 12 == 0):
                        takePhoto(cam, option, x)
                    time.sleep(0.05)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                              sim.simx_opmode_blocking)
                    i += 1

                # llega final vuelta girar derecha
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(90), step=0.05))

                for angle in angle_rot:
                    time.sleep(0.05)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                # termina de rotar avanza en y
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                new_y = list(
                    np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
                for y in new_y:
                    time.sleep(0.05)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                              sim.simx_opmode_blocking)

                # termina avance y rotar derecha
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(0), step=0.05))

                for angle in angle_rot:
                    time.sleep(0.05)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)


clientID = connect(19999)

# Establecer parámetros del plano
plano_nombre = 'Cesped'  # Nombre del objeto que representa el plano en CoppeliaSim
x_min_huerto = 0.297
x_max_huerto = 4.6
y_min_huerto = -4.7
y_max_huerto = 4.6

# Establecer parámetros del dron
dron_nombre = 'target_dron'  # Nombre del objeto que representa el dron en CoppeliaSim
x_inicial = -4.6752
y_inicial = -4.6990

# Establecer parámetros de la camara
camara = 'Vision_sensor'  # Nombre del objeto que representa la camara en CoppeliaSim

if clientID != -1:

    # Obtener identificador del plano
    _, plano_handle = sim.simxGetObjectHandle(
        clientID, plano_nombre, sim.simx_opmode_blocking)

    # Obtener tamaño del plano
    # _, plano_dimensiones = sim.simxGetObjectFloatParameter(clientID, plano_handle, 10, sim.simx_opmode_blocking)
    _, minX = sim.simxGetObjectFloatParameter(clientID, plano_handle, sim.sim_objfloatparam_objbbox_min_x,
                                              sim.simx_opmode_blocking)
    _, maxX = sim.simxGetObjectFloatParameter(clientID, plano_handle, sim.sim_objfloatparam_objbbox_max_x,
                                              sim.simx_opmode_blocking)
    _, minY = sim.simxGetObjectFloatParameter(clientID, plano_handle, sim.sim_objfloatparam_objbbox_min_y,
                                              sim.simx_opmode_blocking)
    _, maxY = sim.simxGetObjectFloatParameter(clientID, plano_handle, sim.sim_objfloatparam_objbbox_max_y,
                                              sim.simx_opmode_blocking)
    largo_plano = maxX - minX
    ancho_plano = maxY - minY

    # Obtener identificador del dron y la camara
    _, dron_handle = sim.simxGetObjectHandle(
        clientID, dron_nombre, sim.simx_opmode_blocking)
    _, cam = sim.simxGetObjectHandle(
        clientID, camara, sim.simx_opmode_blocking)

    print('Acciones del dron:\n 0) Detectar Huerto Entero \n 1) Detectar Huerto (solo plantaciones) \n 2) Detectar Animales')
    option = int(input('Escoge una acción a realizar: '))
    dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(clientID, dron_handle)

    dron_height = 2.3
    z_step = 0.2
    x_step = 0.05
    y_step = 0.05
    y_movement = 0.7
    threshold = 0.1

    new_z = list(np.arange(dron_pos_z, dron_height, step=z_step))

    # Subir el dron
    for z in new_z:
        time.sleep(0.05)
        sim.simxSetObjectPosition(
            clientID, dron_handle, -1, [dron_pos_x, dron_pos_y, z], sim.simx_opmode_blocking)
    dron_pos_z = dron_height

    moveDron(option)
