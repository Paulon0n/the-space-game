
import math
import random
import pygame
from MyMaths import rand2D
from Planets import Planets
import Environment
from Vex import Vex

class Sun:
    maxRange = 7000
    maxSize = 200
    minSize = 200
    maxRad = 400
    minRad = 200
    maxPlanets = 25
    minPlanets = 0
    counter = 0
    
    def __init__(self, pos=[0, 0], seed = 0):
        Planets.pl = []
        self.pos = Vex(random.randint(-2000, 2000), random.randint(-2000, 2000))
        self.rot = [0, 0, 0]
        self.points = []
        self.surfProjPoints = []
        self.edges = []
        self.corOffset = 0
        self.corHealth = 10000
        self.seed = seed
        random.seed(self.seed)
        self.rad = random.randint(Sun.minRad, Sun.maxRad)
        self.xoffset = random.randint(1, 99999999999)
        self.yoffset = random.randint(1, 99999999999)
        self.pickRndSurfacePoints = random.randint(Sun.minSize, Sun.maxSize)
        self.numPlanets = random.randint(Sun.minPlanets, Sun.maxPlanets)
        self.planets = []
        for i in range(self.numPlanets):
            ang_rad = math.radians(random.randint(0, 360))
            dist_sun = random.randint(self.maxRad*2+25, Sun.maxRange)
            px = math.sin(ang_rad)*dist_sun
            py = math.cos(ang_rad)*dist_sun
            p = Planets((px+self.pos.x(), py+self.pos.y()))
            for pl in Planets.pl:
                while pl.pos.dist2D(p.pos)<=pl.atmos+p.atmos and p != pl:
                    ang_rad = math.radians(random.randint(0, 360))
                    dist_sun = random.randint(self.maxRad*2+25, Sun.maxRange)
                    px = math.sin(ang_rad)*dist_sun
                    py = math.cos(ang_rad)*dist_sun
                    p.pos.set2D((px+self.pos.x(), py+self.pos.y()))
            self.planets += [p]
        
        step = math.radians(360.0 / self.pickRndSurfacePoints)
        for surfacePoint in range(self.pickRndSurfacePoints):
            sx = math.sin(step * surfacePoint)
            sy = math.cos(step * surfacePoint)
            x = sx * (self.rad)
            y = sy * (self.rad)
            h = rand2D(x, y)
            self.points += [Vex(sx * (self.rad+h), sy * (self.rad+h))]
            self.surfProjPoints += [0, 0]
        
        for i in range(len(self.points)):
            if i + 1 < len(self.points):
                self.edges.append([i, i + 1])
            else:
                self.edges.append([i, 0])

    def update(self):
        step = math.radians(360.0 / self.pickRndSurfacePoints)
        for surfacePoint in range(self.pickRndSurfacePoints):
            sx = math.sin(step * surfacePoint)
            sy = math.cos(step * surfacePoint)
            x = sx * (self.rad)
            y = sy * (self.rad)
            h = rand2D(x, y)*10
            self.points[surfacePoint].assign(Vex(sx * (self.rad+h), sy * (self.rad+h)))
        


    def update2(self, cam):
        env = Environment.Environment
        self.update()
        self.drawCore(cam)
        for p in self.planets:
            p.update(cam)
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        
        if ptpdst < env.renderDist+self.rad:
            self.corOffset = 99999999999
            for i, p in enumerate(self.points):
                v = (p+self.pos-cam.pos).rotate2dXY(cam.rotSC[0]).rotate2dYZ(cam.mov[2], cam.rotSC[1])  # pitch
                    
                f = env.fov / (v.z()+.000000001)
                if(f < env.lim):
                    f = 1000
                v = v * f
                v = v + env.center
                self.surfProjPoints[i] = v.p2D()
                if ptpdst < env.renderDist+self.rad:
                    self.corOffset = min(v.y(), self.corOffset)
            env.add_edge((170, 23, 23), self.surfProjPoints, 4, 2)

        if ptpdst >= env.renderDist+self.rad:
            p1 = self.pos.projectedPos( cam)
            if p1[0]:
                points = [(p1[1].x()-self.rad*p1[1].z(), p1[1].y()), (p1[1].x()+self.rad*p1[1].z(), p1[1].y())]
                esc = env.screenClip(points)
                if esc[0]:
                    points = esc[1]
                if (env.inScreen(points[0]) or env.inScreen(points[1])):
                    env.add_edge((170, 23, 23), points, 8)
            

                
    def drawCore(self, cam):
        env = Environment.Environment
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        if ptpdst < env.renderDist+self.rad:
            p = self.pos.projectedPos( cam)
            if p[0]:
                di = int((2+self.corHealth/1000)*p[1].z())
                pygame.draw.circle(env.getScreen(), (132, 6, 6), p[1].integer().p2D(), di, 0)
    def drawCoreCover(self, cam):
        env = Environment.Environment
        for pdc in self.planets:
            pdc.drawCoreCover(cam)
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        if ptpdst < env.renderDist+self.rad:
            p = self.pos.projectedPos(cam)
            if p[0]:
                xy1 = p[1].integer().p2D()
                h1 = 3*p[1].z()
                di = int((2+self.corHealth/1000)*p[1].z())
                rec = ((xy1[0]-di, (self.corOffset-h1)+1.5), (di*2, 2*h1))
                pygame.draw.ellipse(env.getScreen(), (132, 6, 6) , rec, 0)
        







   
