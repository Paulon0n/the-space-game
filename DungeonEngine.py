'''

    Construct a Dungeon crawler
    Use random generation to create a dungeon
    
'''
from Vex import Vex
from Line import Line

class Room:
    points = [(-.5, -.17), (-.5, -.5), (-.17, -.5), 
             (.17,-.5), (.5, -.5), (.5, -.17), 
             (.5, .17), (.5, .5), (.17, .5), 
             (-.17, .5), (-.5, .5), (-.5, .17) ]
    halls = [((-.17, -.5), (.17, -.5)), 
             ((.5, -.17), (.5, .17)), 
             ((.17, .5), (-.17, .5)), 
             ((-.5, .17), (-.5, -.17)) ]
    ways = [(0, -.25), (.25, 0), (0, .25), (-.25, 0)]
    def __init__(self):
        
        self.pos = Vex(0, 0, 0)
        self.scale = Vex(1, 1)
        self.rotate = 0.0
        self.waypoints = []
        self.connect = []

class Hall:
    def __init__(self, ra, rb, raw, rbw):
        self.rooms = [ra, rb]
        self.waysC = [raw, rbw]
        
