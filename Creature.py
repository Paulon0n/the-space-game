# Creature
import math
import random
import pygame

import RPGStats
import Color

from Vex import Vex
import Environment
import Weapon


class Creature:
    Creatures = []
    PlayerCreature = None

    # State
    ROAM = 0
    
    def __init__(self, parent):
        # , Vex(0, -25), Vex(0, -.1)                   \/
        self.points = [Vex(.25, 0.0),Vex(0, -.1),  Vex(-.25, 0.0), Vex(0.0, -.25)]
        self.projectedPoints = [(0, 0) for x in range(len(self.points))]
        #self.edges = [(0, 1), (1,2), (2,3), (3, 0)]
        self.pos = Vex(0.0, 0.0, 0.0)
        self.scale = Vex(1.0, 1.0, 1.0)
        self.parent = parent
        self.ang = random.uniform(0, math.pi * 2.0)
        self.state = Creature.ROAM
        self.stats = RPGStats.RPGStats()
        self.stats.lvlUP()
        self.weapon = Weapon.Weapon(self, [0, 0, 0], [.2, .2, .2])
        self.speed = .1
        self.radius =.5
        Creature.Creatures.extend([self])
        self.pathNodes = []
        self.img = pygame.image.load('test2.png').convert()
        # creatures have shape
        
    def getRadius(self):
        return self.radius
        
    def totalDamage(self):
        return self.stats.getSTR()*2
        
    def selfUpdatePlayer(self, cam, pos):
        env = Environment.Environment
        self.weapon.update()
        for i, p in enumerate(self.points):
            v = p
            v = ((v+pos).setY(v.y()+cam.mov[2]).setZ(v.Z()-cam.pos.Z())).rotate2dYZ(0, cam.rot[0])  # pitch
            f = env.fov / (v.z()+.000000001)
            if(f <= env.lim):
                f = 1000
            self.projectedPoints[i] = (v * f + env.center).p2D()

        env.add_edge(Color.YELLOW, self.projectedPoints, 0, 2)

      
    def selfUpdate(self, cam, pos, ang):
        env = Environment.Environment
        self.weapon.update()
        inscreen = False
        if cam.pos.dist2D(pos) < 300:
            for i, p in enumerate(self.points):
                v = ((p*self.scale).rotate2dXY(math.radians(ang))+pos-cam.pos).rotate2dXY(cam.rot[1]).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitchh
                f = env.fov / (v.z()+.000000001)
                if(f < env.lim):
                    f = 1000
                p = (v * f + env.center).p2D()
                self.projectedPoints[i] = p
                if env.inScreen(p):
                    inscreen = True
            env.add_edge(Color.YELLOW, self.projectedPoints, 0, 2)
        return inscreen        
    
    @staticmethod
    def update(env, cam, pos):
        for c in reversed(Creature.Creatures):
            if c.health > 0:
                    
                if not c.pathNodes:
                    c.pos.set2D(math.sin(c.ang)*c.speed, math.cos(c.ang)*c.speed)
            else:
                Creature.Creatures.remove(c)
                
    #env, cam, self.pos, self.ang
    def projectedPos(self, cam):
        env = Environment.Environment
        v = Vex(0,0,0)
        pos = self.parent.pos
        v = (v - cam.pos + pos).rotate2dXY(cam.rot[1]).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitch

        f = env.fov / (v.z() +.00000001)
        if(f < env.lim):
            f = 1000
        v = v * f + env.center
        return v.p2D()
