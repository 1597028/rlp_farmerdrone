# Farmer Drone
Dron capaz de volar sobre campos de cultivo para controlar al ganado, observar la calidad del terreno y activar zonas de riego.

# Table of Contents
<img src="drone.png"/>

* [What is this?](#1)
   * [Requeriments](#R)
   * [Description](#2)
   * [Hardware Scheme](#3)
   * [Software Architecture](#4)
      * [3D Point Cloud tomato detection](#5)
        * [HSI Threshold Color](#HSI)
        * [PassThrough Filter](#P)
        * [Clustering and RANSAC](#CR)
      * [Inverse kinematics algorithm](#6)
      * [Movement](#M)
   * [Simulation](#7)
   * [Testing and results](#8)
   * [3D Pieces](#9)
   * [Amazing contributions](#10)   
   * [Video](#11)
   * [Authors](#12)


# What is this? <a name="1"></a>
The main objective of Farmer Drone is to maintain an exhaustive control over farmland and livestock by means of the use of a drone that will be able to fly at low altitude to control the livestock and observe the quality of the terrain.

# Requeriments <a name="R"></a>
For running each sample code:

- Python 3.7

- numpy

- math

- matplotlib
- cv2
- <a href="http://www.open3d.org/docs/release/getting_started.html">open3d</a>
- <a href="https://leomariga.github.io/pyRANSAC-3D/">pyRANSAC3D</a>

# Description <a name="2"></a>
FarmerDrone is a robot capable of harvesting tomatoes autonomously through different growing lines and deposit them in a box attached to the base.

The main mechanical component is a anthropomorphic 5-axis robotic arm plus clamp which allows you a sufficient range to harvest tomatoes you have on the growing lines on each side.  At the end of the arm it has a special 3-finger gripper which allows us to take the tomatoes more easily and correctly.

 Matt-Omato's movement through the tomato plants is linear. Moves back and forth through rails so you don't lose straight line  and thus avoid possible shock with the tomateras. Matt-Omato has two proximity sensors which allow him to change direction if he detects any object.
 
 The other most important part of Matt-Omato is the RGB-D camera that has built-in. Thanks to it it is able to detect the tomatoes and obtain the coordinates of them.  This will also allow us to define a threshold that types of tomatoes we agree to harvest and which we do not.
 
  Generally speaking Matt-Omato is able to:
  -  Detect tomato coordinates using a 3D point cloud.
  -  Calculate the angles of rotation of the arm motors in order to move the manipulator through inverse kinematics.
  -   Move autonomously through the tomato plants thanks to the rails and proximity sensors

# Hardware Scheme <a name="3"></a>
This is the hardware scheme made for Matt-Omato. In it we can find the existence of a NEMA engine for the base of the robotic arm which allows us to move 360 degrees.  You can also see a total of 6 servo motors which 5 of them are for the arm and one for RGB-D camera support  which gives us color and depth information about the captured scene. We can also find 2 DC motors for the movement of the wheels. And finally the two proximity sensors to be able to detect the greenhouse walls for example.
<img src="https://user-images.githubusercontent.com/65310531/119172049-b4a35b80-ba65-11eb-9e4f-c1f1f7883818.png" align="center" width="700" alt="hardware_scheme"/>

# Software Architecture <a name="4"></a>
In order to develop the software part of Matt-Omato, we have divided the development into two parts. 

In the diagram below you can see Matt-Omato's internal process in relation to the software. In it, there are two differentiated parts. On the one hand we have everything related to the computer vision that is going to be able to detect the tomatoes and get the coordinates of them. And on the other hand we have the calculation of the position of the robotic arm thanks to the inverse kinematics.

<img src="https://user-images.githubusercontent.com/65310531/119315245-f145a180-bc75-11eb-8d6a-ff82f964df6d.png" align="center" width="500" alt="software_scheme"/>

## 3D Point Cloud tomato detection <a name="5"></a>
 <img src="https://user-images.githubusercontent.com/65310531/119176651-a9532e80-ba6b-11eb-9cd7-0cd376f4e653.png" align="right" width="320" alt="cloud"/>
 In order to provide Matt-Omato with computer vision, it has been necessary to integrate an RGB-D camera that provides depth and color information. Thanks to this we are able to create the 3D point cloud of the scene.
 
In order to obtain the coordinates of the tomatoes at the end of the computer vision algorithm, the following steps have been followed to facilitate our work on the 3D point cloud and tomato detection.
 
 ### HSI Threshold <a name="HSI"></a>
  

At this stage we pass the RGB values obtained by the camera to the HSI color space which is more similar to human vision and easier to parameterize. Once we have the point cloud in this color space, we have defined a threshold which will allow us to keep only those points we are interested in. In this case with tomato colors such as medium ripe green, orange about to ripen and deep red representing a ripe tomato. These are the colors that we accept that Matt-Omato harvests.
 
  ### PassThrough Filter <a name="P"></a>
At this stage the total number of points within the 3D cloud is reduced. The idea is to define a bounding box that limits us to a range in which to keep only those points that fall inside. In this way we will only keep the tomatoes that are close to the camera and remove those background points that the camera can detect. This will make the execution time very small.
  
  ### Clustering and RANSAC <a name="CR"></a>
  
In order to detect all tomatoes in the scene individually, it is necessary to develop an algorithm capable of separating all the groups of points. That is why we have used a clustering algorithm which allows us to group the points by groups establishing the minimum amount of points that we want to have to form one. In this way we also avoid possible noise that may have crept in from the previous stages.

Finally, in order to obtain the coordinates of the tomatoes, we have used a RANSAC algorithm to adjust the points of each cluster to the sphere shape defined by RANSAC. Using the "pyRansac3D" library we are able to obtain the centers of these spheres and therefore the centers of the tomatoes.


## Inverse Kinematics with geometrical method and kinematic decoupling <a name="6"></a>
To solve the inverse kinematics part, we do it geometrically, where it is necessary to know the distance between each joint as well as the inclination in degrees of the arm pitch. We used kinematic decoupoling, that is a calculation made by Pieper, in 1968 who achieved the the point of the gripper.

We use Euler angles. We can get these angles with the elevation and turn of the gripper.With these options we get some complex equations which give more than one result (singular points).

This will allow us to move the Matt-Omato robotic arm to any 3D coordinate that results in the computer vision part. The actuator located at the tip of the robotic arm allows us to correctly pick up the tomato without any damages.

## Movement <a name="M"></a>
<img src="https://user-images.githubusercontent.com/65310531/119307007-4def8f00-bc6b-11eb-8a46-fb86680cb764.png" align="right" width="250" alt="cloud"/>
In order to be able to move Matt-Omato autonomously, he has been provided with two distance sensors capable of detecting any element in front of or behind him. 

Matt-Omato starts his movement in a straight line thanks to the rails and cannot deviate from them. The steps that Matt-Omato follows internally for the movement are as follows:
1. Does the depth sensor detect any elements in front of it?
2. If it detects any element
   - Rotate camera joint to point to the other line of tomato plants
3. If no element is detected
   - Runs computer vision algorithm
   - If detects a tomato
      - Performs inverse kinematics
      - Takes the tomato and place it in the box
   - If does not detect tomato
      - Moves in the indicated direction for one second
      - Back to point 1

# Simulation <a name="7"></a>
In order to test Matt-Omato it has been necessary to use the CoppeliaSim software where we have the whole robot recreated in real size with all the hardware components and all the software components (Python). We have a total of 10 scenes where the difficulty increases according to the number of tomato plants, the number of tomatoes in each tomato plant, the size of the tomatoes and the color of the tomatoes.

<img width="1604" alt="" src="https://www.youtube.com/watch?v=qB0N4pwrjE8&ab_channel=DJIAgriculture">

# Testing and results <a name="8"></a>
To verify how good the proposed solution is, each of the created scenes has been run several times to check the accuracy of the XYZ coordinates of the tomatoes calculated by the computer vision algorithm and the coordinates of the tomatoes in CoppeliaSim. The results can be seen in the following table:

| Escena | Tomates | Error Total X | Error Medio X | Error Total Y | Error Medio Y  | Error Total Z | Error Medio Z  | Distancia Euclidiana | Error Medio Total |
|--------|---------|---------------|---------------|---------------|----------------|---------------|----------------|----------------------|-------------------|
|      1 |       4 |       0,10431 |     0,0260775 |      -0,13623 |     -0,0340575 |        0,0633 |       0,015825 |              0,21308 |           0,05327 |
|      2 |       8 |      0,330662 |    0,04133275 |      -0,42686 |     -0,0533575 |       0,07016 |        0,00877 |              0,54757 |        0,06844625 |
|      3 |       7 |        0,2093 |        0,0299 |      -0,28257 |   -0,040367143 |      0,103086 |    0,014726571 |               0,3822 |            0,0546 |
|      4 |       8 |        0,3357 |     0,0419625 |       -0,4614 |      -0,057675 |       0,10121 |     0,01265125 |              1,16614 |         0,1457675 |
|      5 |      13 |    0,52457715 | 0,04035208846 |   -0,77592288 | -0,05968637539 |    0,05861645 | 0,004508957692 |            0,9649308 |      0,0742254435 |
|      6 |      12 |    0,40989956 | 0,03415829667 |   -0,67678181 | -0,05639848417 |    0,03389403 |   0,0028245025 |            0,8138425 |     0,06782020461 |
|      7 |       8 |    0,30705157 | 0,03838144625 |   -0,46826173 | -0,05853271625 |    0,04832574 |   0,0060407175 |         0,5731481238 |     0,07164351548 |
|      8 |      26 |       0,92196 |       0,03546 |     -1,291836 |      -0,049686 |      0,091208 |       0,003508 |          1,589707329 |     0,06114258958 |
|      9 |      36 |       1,32336 |       0,03676 |     -1,968696 |      -0,054686 |     0,0455445 |    0,001265125 |          2,372576644 |     0,06590490678 |
|     10 |      16 |        0,5264 |        0,0329 |      -0,67744 |       -0,04234 |         0,152 |         0,0095 |         0,8712783215 |      0,0544548951 |

# 3D Pieces <a name="9"></a>
The following parts have been designed using TinkerCad software, the files can be found in the "Piezas 3D" folder.


| | | | |
|:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:|
|<img width="800" alt="Hélice" src="3d-pieces/helices.png">  Hélices |  <img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Arm 1|<img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Arm 2 | <img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Wrist |
|<img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=">  Robot base |  <img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Wheels |<img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Box | <img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Gripper finger |
|<img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Wheel support |  <img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Camera support|<img width="800" alt="screen shot 2017-08-07 at 12 18 15 pm" src=""> Proximity sensor|

# Amazing contributions <a name="10"></a>
This project is designed to facilitate and expedite the arduous task of harvesting. In this country, the agricultural sector is still a fundamental part. In places like Andalusia or Extremadura, most of the population is dedicated to it. In Almeria, for example, a city in Andalusia, is known for the large extensions of greenhouses, where apart from planting other kind of fruits and vegetables, tomatoes are the most frequent. The reason why we did this project is that we want to help farmers to facilitate and avoid the physical work involved, as we know firsthand that it is a very difficult job.

Our project has an interesting point from the harvesting point of view, as we pick the tomatoes with a 3 finger-gripper to ensure the right grip. With a rotation of the gripper, we get the tomato to pluck smoothly and without jerky gestures.

Matt-Omato only needs the human hand to start up. Once it is turned on, it will autonomously do all the work of harvesting tomatoes in a line of tomato plants thanks to the built-in rails that make it not deviate from its straight trajectory.

With the computer vision part, we want to provide our robot with good efficiency, as working with point clouds and RGB-D camera can make the acquisition and detection of tomatoes easier, faster and more efficient.

# Video <a name="11"></a>
[![Vídeo Matt-Omato](drone.png)](https://www.youtube.com/watch?v=YRAI7-MICbY&ab_channel=CoppeliaRobotics)

# Authors <a name="12"></a>
- Víctor Hernández Garrido - 1597028 - <a href="https://github.com/1597028">Github</a>
- Marc Serra Ruíz - 1603957 - <a href="https://github.com/1603957">Github</a>
- Adrián Nieto Núñez - 1569312 - <a href="https://github.com/adrian-nieto">Github</a>
- Joel Sánchez de Murga Pacheco - 1598948 - <a href="https://github.com/1598948">Github</a>
