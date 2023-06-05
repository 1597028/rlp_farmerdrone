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

# Filtros de colores hsv
greenBajo = np.array([45, 100, 20], np.uint8)
greenAlto = np.array([75, 255, 255], np.uint8)
whiteBajo = np.array([0, 0, 200], np.uint8)
whiteAlto = np.array([180, 30, 255], np.uint8)
brownBajo = np.array([10, 100, 20], np.uint8)
brownAlto = np.array([30, 255, 200], np.uint8)
blueBajo = np.array([99, 115, 150], np.uint8)
blueAlto = np.array([110, 255, 255], np.uint8)
pinkBajo = np.array([110, 45, 180], np.uint8)
pinkAlto = np.array([130, 70, 255], np.uint8)

def setHuertecilloWet():
    filtro_huerto = "Seco_a_mojado"
    _ , huerto_handle = sim.simxGetObjectHandle(clientID, filtro_huerto, sim.simx_opmode_blocking)

    sim.simxSetObjectIntParameter(clientID, huerto_handle, 10, sim.sim_objintparam_visibility_layer, sim.simx_opmode_blocking)


def takePhoto(cam, option, x, animales_escapados):
    if (option == 0):
        if (x >= (x_min_huerto - 0.5)):
            # Captamos la imagen del dron
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Cargamos la imagen con el huerto mojado
            imgWet = cv2.imread('mojau.jpg')
            #imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)

            # Realizamos la diferencia de imagenes
            imgRes = cv2.absdiff(imgInicial, imgWet)

            # Hacemos la media de la imagen
            mean = np.mean(imgRes)

            # Si la media es mayor a un llindar, el trozo de huerto es distinto al mojado
            if (mean >= 40):
                print("Huerto seco!\n")
                detectar_huerto.append(0)
            else:
                print("Huerto mojado!\n")
                detectar_huerto.append(1)

    elif (option == 1):
        if (x >= (x_min_huerto - 0.5)):
            # Captamos la imagen del dron
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Usamos el filtro de color verde hsv
            hsv = cv2.cvtColor(imgInicial, cv2.COLOR_RGB2HSV)
            maskGreen = cv2.inRange(hsv, greenBajo, greenAlto)
            maskGreenVis = cv2.bitwise_and(
                imgInicial, imgInicial, mask=maskGreen)

            # Si existe el color verde
            if (np.mean(maskGreenVis) > 0):
                # Cargamos la imagen con el huerto mojado
                imgWet = cv2.imread('mojau.jpg')
                #imgWet = cv2.cvtColor(imgWet, cv2.COLOR_BGR2RGB)

                # Realizamos la diferencia de imagenes
                imgRes = cv2.absdiff(imgInicial, imgWet)

                # Hacemos la media de la imagen
                mean = np.mean(imgRes)

                # Si la media es mayor a un llindar, el trozo de huerto es distinto al mojado
                if (mean >= 40):
                    print("Huerto seco!\n")
                    detectar_huerto.append(0)
                else:
                    print("Huerto mojado!\n")
                    detectar_huerto.append(1)
    elif (option == 2):
        # Comprobamos que el dron no entre en el rango de ningun cerco
        dron_pos_x, dron_pos_y, _ = get_drone_pos(
            clientID, dron_handle)
        if (dron_pos_x < -1.8 and dron_pos_x > -3.7) and (dron_pos_y > -2.5 and dron_pos_y < -0.4):
            pass
        elif (dron_pos_y > 1.3 and dron_pos_y < 3.3) and (dron_pos_x > -3.9 and dron_pos_x < -2.0):
            pass
        else:
            # Comprobamos la imagen actual
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Aplicamos la mascara para detectar el color blanco
            imgRGB = cv2.cvtColor(imgInicial, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)
            maskCow = cv2.inRange(hsv, whiteBajo, whiteAlto)
            _ = cv2.bitwise_and(
                imgRGB, imgRGB, mask=maskCow)

            # Contamos cuantos pixeles existen de color blanco
            temp = 0
            for x in range(np.shape(maskCow)[0]):
                for y in range(np.shape(maskCow)[1]):
                    if (maskCow[x, y] != 0):
                        temp += 1

            # Si existe algun pixel abierto, lo comprobamos
            if temp > 0:
                # Cogemos la imagen de referencia
                imgCow = cv2.imread('vacas.jpg')

                # Aplicamos mascara para detectar el color blanco
                hsv = cv2.cvtColor(imgCow, cv2.COLOR_BGR2HSV)
                maskCow = cv2.inRange(hsv, whiteBajo, whiteAlto)
                _ = cv2.bitwise_and(
                    imgCow, imgCow, mask=maskCow)

                # Contamos cuantos pixeles existen de color blanco
                ind = 0
                for x in range(np.shape(maskCow)[0]):
                    for y in range(np.shape(maskCow)[1]):
                        if (maskCow[x, y] != 0):
                            ind += 1
                # Dividimos entre los animales dentro del cerco para saber cuanto ocupa una vaca
                mean_pixels = ind/6

                # Cogemos el valor medio en pixeles de una vaca anteriormente calculado y comprobamos si en la
                # imagen actual existen 1 o más vacas (podrian ser 2 animales escapados juntos), ademas
                # aplicamos un llindar por si existen pixeles desaparecidos o mal calculados
                llindar = int(mean_pixels * 0.2)
                for x in range(1, animales_escapados[0] + 1):
                    if (temp > ((mean_pixels - llindar) * x) and temp < ((mean_pixels + llindar)*x)):
                        print("Hay", str(x), "vaca/s suelta/s aqui")
                        animales_escapados[0] -= x
                        error = True
                        for v in animales:
                            if (v[2] == False):
                                if v[1][0] > (dron_pos_x - 0.6) and v[1][0] < (dron_pos_x + 0.6):
                                    if v[1][1] > (dron_pos_y - 0.6) and v[1][1] < (dron_pos_y + 0.6):
                                        sim.simxSetObjectPosition(
                                            clientID, v[0], -1, [v[1][0], v[1][1], -10], sim.simx_opmode_blocking)
                                        v[2] = True
                                        error = False
                        if (error):
                            print("Error: Aqui no hay", str(x), "animal/es")
                            animales_escapados[0] += x
                        print()

    elif (option == 3):
        # Comprobamos que el dron no entre en el rango de ningun cerco
        dron_pos_x, dron_pos_y, _ = get_drone_pos(
            clientID, dron_handle)
        if (dron_pos_x < -1.8 and dron_pos_x > -3.7) and (dron_pos_y > -2.5 and dron_pos_y < -0.4):
            pass
        elif (dron_pos_y > 1.3 and dron_pos_y < 3.3) and (dron_pos_x > -3.9 and dron_pos_x < -2.0):
            pass
        else:
            # Comprobamos la imagen actual
            _, resolution, image = sim.simxGetVisionSensorImage(
                clientID, cam, 0, sim.simx_opmode_oneshot_wait)
            imgInicial = np.array(image, dtype=np.uint8)
            imgInicial.resize([resolution[1], resolution[0], 3])

            # Aplicamos la mascara para detectar el color rosa
            hsv = cv2.cvtColor(imgInicial, cv2.COLOR_BGR2HSV)
            maskPig = cv2.inRange(hsv, pinkBajo, pinkAlto)
            _ = cv2.bitwise_and(
                imgInicial, imgInicial, mask=maskPig)

            # Contamos cuantos pixeles existen de color rosa
            temp = 0
            for x in range(np.shape(maskPig)[0]):
                for y in range(np.shape(maskPig)[1]):
                    if (maskPig[x, y] != 0):
                        temp += 1

            # Si existe algun pixel abierto, lo comprobamos
            if (temp > 0):
                # Cogemos la imagen de referencia
                imgPig = cv2.imread('cerdos.jpg')

                # Aplicamos mascara para detectar el color rosa
                hsv = cv2.cvtColor(imgPig, cv2.COLOR_BGR2HSV)
                maskPig = cv2.inRange(hsv, pinkBajo, pinkAlto)
                _ = cv2.bitwise_and(
                    imgPig, imgPig, mask=maskPig)

                # Contamos cuantos pixeles existen de color rosa
                ind = 0
                for x in range(np.shape(maskPig)[0]):
                    for y in range(np.shape(maskPig)[1]):
                        if (maskPig[x, y] != 0):
                            ind += 1

                # Dividimos entre los animales dentro del cerco para saber cuanto ocupa un cerdo
                mean_pixels = ind/9
                # Cogemos el valor medio en pixeles de una gallina anteriormente calculado y comprobamos si en la
                # imagen actual existen 1 o más gallinas (podrian ser 2 animales escapados juntos), ademas
                # aplicamos un llindar por si existen pixeles desaparecidos o mal calculados
                llindar = int(mean_pixels * 0.2)
                for x in range(1, animales_escapados[0] + 1):
                    if (temp > ((mean_pixels * x) - llindar) and temp < ((mean_pixels * x) + llindar)):
                        print("Hay", str(x), "cerdo/s suelto/s aqui")
                        animales_escapados[0] -= x
                        error = True
                        for c in animales:
                            if (c[2] == False):
                                if c[1][0] > (dron_pos_x - 0.6) and c[1][0] < (dron_pos_x + 0.6):
                                    if c[1][1] > (dron_pos_y - 0.6) and c[1][1] < (dron_pos_y + 0.6):
                                        sim.simxSetObjectPosition(
                                            clientID, c[0], -1, [c[1][0], c[1][1], -10], sim.simx_opmode_blocking)
                                        c[2] = True
                                        error = False
                        if (error):
                            print("Error: Aqui no hay", str(x), "animal/es")
                            animales_escapados[0] += x
                        print()


def moveDron(option, animales_escapados):
    if (option == 0 or option == 1):
        dron_height = 8.65
        little_step = 0.1
        y_movement = 2.6
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
            #time.sleep(0.01)
            sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                      sim.simx_opmode_blocking)
        dron_pos_x = x_min_huerto

        new_y = list(np.arange(dron_pos_y, y_min_huerto, step=little_step))
        time.sleep(1)
        for y in new_y:
            #time.sleep(0.01)
            sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                      sim.simx_opmode_blocking)
            temp = y
        dron_pos_y = temp
        time.sleep(1)
        while dron_pos_y < y_max_huerto:
            new_x = list(np.arange(dron_pos_x, x_max_huerto, step=x_step))
            new_y = list(
                np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
            if dron_pos_x < (x_max_huerto - threshold):  # Ida dron

                # Cada 50 tics la camara encuentra un cuadrado totalmente nuevo
                i = 50
                for x in new_x:
                    #time.sleep(0.075)
                    if (i % 50 == 0):
                        takePhoto(cam, option, x, animales_escapados)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                              sim.simx_opmode_blocking)
                    i += 1

                time.sleep(1)
                # set variables
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(90), step=0.05))
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)
                # Llega final x rotar izquierda
                for angle in angle_rot:
                    time.sleep(0.075)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                # Mover hacia y
                for y in new_y:
                    #time.sleep(0.075)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                              sim.simx_opmode_blocking)

                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(180), step=0.05))
                # final avance rotar izquierda
                for angle in angle_rot:
                    time.sleep(0.075)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                time.sleep(1)
            # vuelta dron
            if dron_pos_x > (x_min_huerto - threshold):
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                new_x = list(np.arange(dron_pos_x, x_min_huerto, step=-x_step))

                i = 50
                for x in new_x:
                    #time.sleep(0.075)
                    if (i % 50 == 0):
                        takePhoto(cam, option, x, animales_escapados)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                              sim.simx_opmode_blocking)
                    i += 1

                time.sleep(1)

                # llega final vuelta girar derecha
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(90), step=0.05))

                for angle in angle_rot:
                    time.sleep(0.075)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                # termina de rotar avanza en y
                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                new_y = list(
                    np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
                for y in new_y:
                    #time.sleep(0.075)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                              sim.simx_opmode_blocking)

                # termina avance y rotar derecha
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(0), step=0.05))

                for angle in angle_rot:
                    time.sleep(0.075)
                    sim.simxSetObjectOrientation(
                        clientID, dron_handle, -1, [0, 0, angle], sim.simx_opmode_blocking)

                dron_pos_x, dron_pos_y, _ = get_drone_pos(
                    clientID, dron_handle)

                time.sleep(1)
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

        time.sleep(1)

        while dron_pos_y < maxY:
            if (animales_escapados[0] == 0):
                return
            new_x = list(np.arange(dron_pos_x, x_min_huerto, step=x_step))
            new_y = list(
                np.arange(dron_pos_y, dron_pos_y + y_movement, step=y_step))
            if dron_pos_x < (x_min_huerto - threshold):  # Ida dron
                # Cada 13 tics la camara encuentra un cuadrado totalmente nuevo, nosotros calcularemos cada 7 tics (medio bloque)
                i = 7
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 7 == 0):
                        time.sleep(0.1)
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

                new_x = list(np.arange(dron_pos_x, minX, step=-x_step))

                i = 7
                for x in new_x:
                    time.sleep(0.05)
                    if (i % 7 == 0):
                        time.sleep(1)
                        takePhoto(cam, option, x, animales_escapados)
                    sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                              sim.simx_opmode_blocking)
                    i += 1

                # llega final vuelta girar derecha
                orientation = get_drone_orientation(clientID, dron_handle)
                angle_rot = list(
                    np.arange(orientation, math.radians(90), step=0.05))

                for angle in angle_rot:
                    time.sleep(0.1)
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

x_min_huerto = 1.24
x_max_huerto = 3.77
x_step = 0.05

y_min_huerto = -3.74
y_max_huerto = 3.76
y_step = 0.05

# Establecer parámetros del dron
dron_nombre = 'target_dron'  # Nombre del objeto que representa el dron en CoppeliaSim
x_inicial = -4.6
y_inicial = -4.6
z_inicial = 0.169

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

    print('Acciones del dron:\n 0) Detectar Huerto Entero \n 1) Detectar Huerto (solo plantaciones) \n 2) Detectar Vacas \n 3) Detectar Cerdos')
    option = int(input('Escoge una acción a realizar: '))
    dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(clientID, dron_handle)

    # Si la opcion son animales, hay que indicar cuantos animales se han escapado
    temp = 0
    animales = []
    if (option == 2):
        temp = int(input("Cuantas vacas se han escapado? "))
        # Guardamos los identificadores, las posiciones y si han sido encontrados de cada vaca
        for i in range(temp):
            _, vaca = sim.simxGetObjectHandle(
                clientID, "VacaFuera" + str(i+1), sim.simx_opmode_blocking)
            _, vacaPos = sim.simxGetObjectPosition(
                clientID, vaca, -1, sim.simx_opmode_blocking)
            animales.append([vaca, vacaPos, False])
    elif (option == 3):
        temp = int(input("Cuantos cerdos se han escapado? "))
        # Guardamos los identificadores, las posiciones y si han sido encontrados de cada cerdo
        for i in range(temp):
            _, cerdo = sim.simxGetObjectHandle(
                clientID, "CerdoFuera" + str(i+1), sim.simx_opmode_blocking)
            _, cerdoPos = sim.simxGetObjectPosition(
                clientID, cerdo, -1, sim.simx_opmode_blocking)
            animales.append([cerdo, cerdoPos, False])

    animales_escapados = [temp]
    detectar_huerto = []

    moveDron(option, animales_escapados)

    # Generamos una acción final dependiendo de la opción
    if (option == 0 or option == 1):
        print("Estado de los huertos:\n")
        for d in range(len(detectar_huerto)):
            if detectar_huerto[d] == 0:
                print("Huerto nº", str(d + 1), "esta seco :-(")
            else:
                print("Huerto nº", str(d + 1), "esta mojado :-)")
    if (option == 2 or option == 3):
        if (animales_escapados[0] != 0):
            print("No se han podido encontrar todos los animales.\nHa/n quedado ",
                  animales_escapados[0], " animal/es suelto/s :-(")
        else:
            print("Se han encontrado todos los animales :-)")

    # Movemos el dron a la posicion inicial
    print("Volviendo a la zona inicial...")
    dron_pos_x, dron_pos_y, dron_pos_z = get_drone_pos(clientID, dron_handle)

    if (dron_pos_x > x_inicial):
        new_x = list(np.arange(dron_pos_x, x_inicial - 0.1, step=-0.1))
    else:
        new_x = list(np.arange(dron_pos_x, x_inicial + 0.1, step=0.1))

    for x in new_x:
        time.sleep(0.05)
        sim.simxSetObjectPosition(clientID, dron_handle, -1, [x, dron_pos_y, dron_pos_z],
                                  sim.simx_opmode_blocking)
        temp = x
    dron_pos_x = temp

    if (dron_pos_y > y_inicial):
        new_y = list(np.arange(dron_pos_y, y_inicial - 0.1, step=-0.1))
    else:
        new_y = list(np.arange(dron_pos_y, y_inicial + 0.1, step=0.1))
    time.sleep(3)
    for y in new_y:
        time.sleep(0.05)
        sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, y, dron_pos_z],
                                  sim.simx_opmode_blocking)
        temp = y
    dron_pos_y = temp

    if (dron_pos_z > z_inicial):
        new_z = list(np.arange(dron_pos_z, z_inicial - 0.1, step=-0.1))
    else:
        new_z = list(np.arange(dron_pos_z, z_inicial + 0.1, step=0.1))
    time.sleep(3)
    for z in new_z:
        time.sleep(0.05)
        sim.simxSetObjectPosition(clientID, dron_handle, -1, [dron_pos_x, dron_pos_y, z],
                                  sim.simx_opmode_blocking)
        temp = z
    dron_pos_z = temp

    # Activamos el sistema de riego para las zonas secas
    time.sleep(1)
    ret, _, _, _, _ = sim.simxCallScriptFunction(clientID, 'Aspersor', sim.sim_scripttype_childscript,
                                                 'setParticleVisibility', [], [], [], bytearray(),
                                                 sim.simx_opmode_blocking)
    time.sleep(4)
    setHuertecilloWet()
    time.sleep(1)
    ret, _, _, _, _ = sim.simxCallScriptFunction(clientID, 'Aspersor', sim.sim_scripttype_childscript,
                                                 'setParticleVisibility', [], [], [], bytearray(),
                                                 sim.simx_opmode_blocking)
