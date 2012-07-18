# Author: Shao Zhang, Phil Saltzman, and Eddie Canaan
# Last Updated: 4/19/2005
#
# This tutorial will demonstrate some uses for intervals in Panda
# to move objects in your panda world.
# Intervals are tools that change a value of something, like position, rotation
# or anything else, linearly, over a set period of time. They can be also be
# combined to work in sequence or in Parallel
#
# In this lesson, we will simulate a carousel in motion using intervals.
# The carousel will spin using an hprInterval while 4 pandas will represent
# the horses on a traditional carousel. The 4 pandas will rotate with the
# carousel and also move up and down on their poles using a LerpFunc interval.
# Finally there will also be lights on the outer edge of the carousel that
# will turn on and off by switching their texture with intervals in Sequence
# and Parallel

import direct.directbase.DirectStart
from panda3d.core import Lerp
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import NodePath
from panda3d.core import Vec3, Vec4
from direct.interval.IntervalGlobal import *   #Needed to use Intervals
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from direct.task import Task

#Importing math constants and functions
from math import pi, sin, cos
from PandaServer import *

envir = '/Developer/Panda3D/models/environment.egg.pz'

class World(ShowBase):
  def __init__(self):
    ShowBase.__init__(self)
    #This creates the on screen title that is in every tutorial
    self.title = OnscreenText(text="IMU Glove",
                              style=1, fg=(1,1,1,1),
                              pos=(0.87,-0.95), scale = .07)

    base.setBackgroundColor(.6, .6, 1) #Set the background color
    #base.disableMouse()                #Allow manual positioning of the camera
    #camera.setPosHpr ( 0, -8, 2.5, 0, -9, 0 )  #Set the cameras' position
                                               #and orientation

    self.environ = loader.loadModel("models/environment")
    self.environ.reparentTo(self.render)
    self.environ.setScale(0.25, 0.25, 0.25)
    self.environ.setPos(-8, 42, 0)

    self.loadModels()                  #Load and position our models
    #self.setupLights()                 #Add some basic lighting
    self.SetupTasks()               #Create the needed intervals and put the
                                       #carousel into motion
    #camera.setPosHpr ( 0, 0, 30, 0, 0, 0 )  #Set the cameras' position
    self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
    self.taskMgr.add(self.moveHandTask, "MoveHandTask")

  def loadModels(self):
    self.hand  = loader.loadModel("/Users/kutenai/proj/BSU/MastersThesis/Software/scripts/Panda/models/HandBase.egg")
    self.hand.reparentTo(self.render)

    self.fingers = [self.hand.attachNewNode("finger"+str(i))
                   for i in range(4)]
    self.models = [loader.loadModel("/Users/kutenai/proj/BSU/MastersThesis/Software/scripts/Panda/models/Fingertip.egg")
                   for i in range(4)]
    self.moves = [0 for i in range(4)]

    for i in range(4):
      #set the position and orientation of the ith panda node we just created
      #The Z value of the position will be the base height of the pandas.
      #The headings are multiplied by i to put each panda in its own position
      #around the carousel
      self.fingers[i].setPosHpr(5, i*0.7+0.7, 0,270,0,0)

      #Load the actual panda model, and parent it to its dummy node
      self.models[i].reparentTo(self.fingers[i])
      #Set the distance from the center. This distance is based on the way the
      #carousel was modeled in Maya
      self.models[i].setY(.85)

  def notifyPos(self,pos):
    self.z = pos
    self.hand.set(pos)

  def SetupTasks(self):

    self.move = LerpFunc(
        self.basicMoves,
        duration = 20,
        fromData = 0,
        toData = 100,
        extraArgs=[self.hand]
    )

    self.x = 0
    self.y = 0
    self.z = 2
    #self.move.loop()
    self.hand.setX(self.x)
    self.hand.setY(self.y)
    self.hand.setZ(self.z)

  def basicMoves(self,val, hand):
    self.x = (val % 10)/10
    self.y = (val % 20)/20
    self.z = (val % 50)/50
    hand.setX(self.x)
    hand.setY(self.y)
    hand.setZ(self.z)

  def moveHandTask(self,task):
    angleDegrees = task.time * .0
    angleRadians = angleDegrees * (pi / 180.0)
    self.hand.setHpr(0, angleDegrees, 0)
    return Task.cont

  def spinCameraTask(self,task):
    angleDegrees = task.time * 6.0
    angleRadians = angleDegrees * (pi / 180.0)
    self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
    self.camera.setHpr(angleDegrees, 0, 0)
    return Task.cont

w = World()
w.run()
