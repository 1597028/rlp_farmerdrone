from utils import get_drone_orientation
from utils import get_drone_pos
from utils import connect
import sim
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
from sympy import *
import warnings
warnings.filterwarnings("ignore")


greenBajo = np.array([45, 100, 20], np.uint8)
greenAlto = np.array([75, 255, 255], np.uint8)
whiteBajo = np.array([0, 0, 200], np.uint8)
whiteAlto = np.array([180, 20, 255], np.uint8)
brownBajo = np.array([10, 100, 20], np.uint8)
brownAlto = np.array([30, 255, 200], np.uint8)
blueBajo = np.array([99, 115, 150], np.uint8)
blueAlto = np.array([110, 255, 255], np.uint8)


# HAY QUE TENER UNA FOTO DEL CESPED MOJADO ANTES!!


def takePhoto(cam, option, x, animales_escapados):
    if (option == 0):
        if (x >= x_min_huerto):
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            imgWet = cv2.imread('mojau.jpg')
            imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)

            imgRes = cv2.absdiff(imgInicial, imgWet)

            mean = np.mean(imgRes)
            print(mean)

            if (mean >= 40):
                print("Huerto seco!\n")
            else:
                print("Huerto mojado!\n")
    elif (option == 1):
        if (x >= x_min_huerto):
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            hsv = cv2.cvtColor(imgInicial, cv2.COLOR_RGB2HSV)
            maskGreen = cv2.inRange(hsv, greenBajo, greenAlto)
            maskGreenVis = cv2.bitwise_and(
                imgInicial, imgInicial, mask=maskGreen)

            if (np.mean(maskGreenVis) > 0):
                imgWet = cv2.imread('mojau.jpg')
                imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)

                imgRes = cv2.absdiff(imgInicial, imgWet)

                mean = np.mean(imgRes)
                print(mean)

                if (mean >= 40):
                    print("Huerto seco!\n")
                else:
                    print("Huerto mojado!\n")
    elif (option == 2):
        # Comprobamos que el dron no entre en el rango de ningun cerco
        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)
        if (dron_pos_x < -1.8 and dron_pos_x > -3.7) and (dron_pos_y > -2.5 and dron_pos_y < -0.4):
            pass
        elif (dron_pos_y > 1.3 and dron_pos_y < 3.3) and (dron_pos_x > -3.9 and dron_pos_x < -2.0):
            pass
        else:
            # Cogemos la imagen de referencia
            imgCow = cv2.imread('vacas.jpg')

            # Aplicamos mascara para detectar el color blanco
            hsv = cv2.cvtColor(imgCow, cv2.COLOR_BGR2HSV)
            maskCow = cv2.inRange(hsv, whiteAlto, whiteAlto)
            maskCowVis = cv2.bitwise_and(
                imgCow, imgCow, mask=maskCow)

            # Contamos cuantos pixeles existen de color blanco
            temp = 0
            for x in range(np.shape(maskCow)[0]):
                for y in range(np.shape(maskCow)[1]):
                    if (maskCow[x, y] != 0):
                        temp += 1
            # Dividimos entre los animales dentro del cerco para saber cuanto ocupa una vaca
            mean_pixels = temp/6

            # Comprobamos la imagen actual
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Aplicamos la mascara para detectar el color blanco
            imgRGB = cv2.cvtColor(imgInicial, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)
            maskCow = cv2.inRange(hsv, whiteAlto, whiteAlto)
            maskCowVis = cv2.bitwise_and(
                imgRGB, imgRGB, mask=maskCow)

            # Contamos cuantos pixeles existen de color blanco
            temp = 0
            for x in range(np.shape(maskCow)[0]):
                for y in range(np.shape(maskCow)[1]):
                    if (maskCow[x, y] != 0):
                        temp += 1

            # Cogemos el valor medio en pixeles de una vaca anteriormente calculado y comprobamos si en la
            # imagen actual existen 1 o más vacas (podrian ser 2 animales escapados juntos), ademas
            # aplicamos un llindar por si existen pixeles desaparecidos o mal calculados
            llindar = 30
            for x in range(1, animales_escapados[0] + 1):
                if (temp > ((mean_pixels - llindar) * x) and temp < ((mean_pixels + llindar)*x)):
                    print("Hay ", x, " vaca/s suelta/s aqui\n")
                    animales_escapados[0] -= x
    elif (option == 3):
        # Comprobamos que el dron no entre en el rango de ningun cerco
        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)
        if (dron_pos_x < -1.8 and dron_pos_x > -3.7) and (dron_pos_y > -2.5 and dron_pos_y < -0.4):
            pass
        elif (dron_pos_y > 1.3 and dron_pos_y < 3.3) and (dron_pos_x > -3.9 and dron_pos_x < -2.0):
            pass
        else:
            # Cogemos la imagen de referencia
            imgChicken = cv2.imread('gallinas.jpg')

            # Aplicamos mascara para detectar el color blanco
            hsv = cv2.cvtColor(imgChicken, cv2.COLOR_BGR2HSV)
            maskChicken = cv2.inRange(hsv, whiteBajo, whiteAlto)
            maskChickenVis = cv2.bitwise_and(
                imgChicken, imgChicken, mask=maskChicken)

            # Contamos cuantos pixeles existen de color blanco
            temp = 0
            for x in range(np.shape(maskChicken)[0]):
                for y in range(np.shape(maskChicken)[1]):
                    if (maskChicken[x, y] != 0):
                        temp += 1

            # Dividimos entre los animales dentro del cerco para saber cuanto ocupa una gallina
            mean_pixels = temp/11

            # Comprobamos la imagen actual
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Aplicamos la mascara para detectar el color blanco
            imgRGB = cv2.cvtColor(imgInicial, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)
            maskChicken = cv2.inRange(hsv, whiteBajo, whiteAlto)
            maskChickenVis = cv2.bitwise_and(
                imgRGB, imgRGB, mask=maskChicken)

            # Contamos cuantos pixeles existen de color blanco
            temp = 0
            for x in range(np.shape(maskChicken)[0]):
                for y in range(np.shape(maskChicken)[1]):
                    if (maskChicken[x, y] != 0):
                        temp += 1

            # Cogemos el valor medio en pixeles de una gallina anteriormente calculado y comprobamos si en la
            # imagen actual existen 1 o más gallinas (podrian ser 2 animales escapados juntos), ademas
            # aplicamos un llindar por si existen pixeles desaparecidos o mal calculados
            llindar = 5
            print("ANIMALES", animales_escapados[0])
            for x in range(1, animales_escapados[0] + 1):
                if (temp > ((mean_pixels - llindar) * x) and temp < ((mean_pixels + llindar)*x)):
                    print("Hay ", x, " gallina/s suelta/s aqui\n")
                    animales_escapados[0] -= x


def moveDron(option, animales_escapados):
    if (option == 0 or option == 1):
        dron_height = 2.3
        little_step = 0.1
        y_movement = 0.7
        threshold = 0.1

        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)

        new_z = list(np.arange(dron_pos_z, dron_height, step=little_step))

        # Subir el dron
        for z in new_z:
            time.sleep(0.05)
            sim.simxSetObjectPosition(
                clientID, dron_handle, -1, [dron_pos_x, dron_pos_y, z], sim.simx_opmode_blocking)
        dron_pos_z = dron_height

        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)

        new_x = list(np.arange(dron_pos_x, x_min_huerto, step=little_step))
        for x in new_x:
            time.sleep(0.05)
            sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                      sim.simx_opmode_blocking)
        dron_pos_x = x_min_huerto

        while dron_pos_y < y_max_huerto:
            if (animales_escapados[0] == 0):
                return

            new_x = list(np.arange(dron_pos_x, x_max_huerto, step=x_step))
            new_y = list(
                np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
            if dron_pos_x < (x_max_huerto - threshold):  # Ida dron

                # Cada 13 tics la camara encuentra un cuadrado totalmente nuevo
                i = 13
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 13 == 0):
                        takePhoto(cam, option, x, animales_escapados)
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

                i = 13
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 13 == 0):
                        takePhoto(cam, option, x, animales_escapados)
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
    elif (option == 2 or option == 3):
        dron_height = 3.9
        little_step = 0.1
        y_movement = 0.7
        threshold = 0.1

        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)

        new_z = list(np.arange(dron_pos_z, dron_height, step=little_step))

        # Subir el dron
        for z in new_z:
            time.sleep(0.05)
            sim.simxSetObjectPosition(
                clientID, dron_handle, -1, [dron_pos_x, dron_pos_y, z], sim.simx_opmode_blocking)
        dron_pos_z = dron_height

        dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(
            clientID, dron_handle)

        time.sleep(7)

        while dron_pos_y < maxY:
            new_x = list(np.arange(dron_pos_x, maxX, step=x_step))
            new_y = list(
                np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
            if dron_pos_x < (maxX - threshold):  # Ida dron

                # Cada 13 tics la camara encuentra un cuadrado totalmente nuevo
                i = 13
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 13 == 0):
                        takePhoto(cam, option, x, animales_escapados)
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
            if dron_pos_x > (maxX - threshold):
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                new_x = list(np.arange(dron_pos_x, minX, step=-x_step))

                i = 13
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 13 == 0):
                        takePhoto(cam, option, x, animales_escapados)
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
    else:
        print("Opción no disponible")


clientID = connect(19999)

# Establecer parámetros del plano
plano_nombre = 'Cesped'  # Nombre del objeto que representa el plano en CoppeliaSim

x_min_huerto = 0.29
x_max_huerto = 4.6
x_step = 0.05

y_min_huerto = -4.65
y_max_huerto = 4.65
y_step = 0.05

# Establecer parámetros del dron
dron_nombre = 'target_dron'  # Nombre del objeto que representa el dron en CoppeliaSim
x_inicial = -4.6
y_inicial = -4.6

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

    print('Acciones del dron:\n 0) Detectar Huerto Entero \n 1) Detectar Huerto (solo plantaciones) \n 2) Detectar Vacas \n 3) Detectar Gallinas')
    option = int(input('Escoge una acción a realizar: '))
    dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(clientID, dron_handle)
    temp = 0
    if (option == 2):
        temp = int(input("Cuantas vacas se han escapado? "))
    elif (option == 3):
        temp = int(input("Cuantas gallinas se han escapado? "))
    
    animales_escapados = [temp]

    moveDron(option, animales_escapados)

    if (option == 2 or option == 3):
        if (animales_escapados != 0):
            print("No se han podido encontrar todos los animales.\nHa/n quedado ",
                  animales_escapados, " animal/es suelto/s")
        else:
            print("Se han encontrado todos los animales")
