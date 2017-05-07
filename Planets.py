
import math
import pygame
import random

import Color
import ParticleEngine

from Vex import Vex
from MyMaths import rand2D
from Noise import Noise
import Environment
from Line import Line

ZERO = Vex(0, 0, 0)

class Planets:
    maxSize = 100
    minSize = 100
    maxRad = 150
    minRad = 50
    con = 1
    pl = []
    def __init__(self, pos=[0, 0]):
        self.pos = Vex(pos[0], pos[1])
        self.rot = [0, 0, 0]
        self.surfPoints = []
        self.surfProjPoints = []
        self.edges = []
        self.atmosPoints = []
        self.atmosProjPoints = []
        self.atmosEdge = []
        self.rad = random.randint(self.minRad, self.maxRad)
        self.xoffset = random.randint(1, 99999999999)
        self.yoffset = random.randint(1, 99999999999)
        self.corHealth = 1000
        self.corOffset = 0
        self.surfColor = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.atmosColor = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        Noise()
        self.doSurface()
        self.doAtmosphere()
        Planets.pl.extend([self])
        

    def update(self, cam):
        env = Environment.Environment
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        
        self.drawCore( cam)
        if ptpdst < env.renderDist:
            self.corOffset = 99999999999
            for i, p in enumerate(self.atmosPoints):
                v = (p+self.pos-cam.pos).rotate2dXY(cam.rotSC[0]).rotate2dYZ(cam.mov[2], cam.rotSC[1])  # pitch
                    
                f = env.fov / (v.z()+.000000001)
                if(f < env.lim):
                    f = 1000
                v = v * f
                v = v + env.center
                self.atmosProjPoints[i] = v.p2D()
  
            env.add_edge(self.atmosColor, self.atmosProjPoints, 1, 2)
            

            for i, p in enumerate(self.surfPoints):
                v = (p+self.pos-cam.pos).rotate2dXY(cam.rotSC[0]).rotate2dYZ(cam.mov[2], cam.rotSC[1])  # pitch
                    
                f = env.fov / (v.z()+.000000001)
                if(f < env.lim):
                    f = 1000
                v = v * f
                v = v + env.center
                self.surfProjPoints[i] = v.p2D()
                if ptpdst < env.renderDist:
                    self.corOffset = min(v.y(), self.corOffset)
                
                    
            for pointz in self.edges:
                
                points = [self.surfProjPoints[pointz[0][0]], self.surfProjPoints[pointz[0][1]]]
                if ptpdst < env.renderDist: 
                    esc = env.screenClip(points)
                    if esc[0]:
                        points = esc[1]
                    if (env.inScreen(points[0]) or env.inScreen(points[1])):
                        if pointz[1] == 0:
                            env.add_edge(self.surfColor, points, 4)
                        else:
                            env.add_edge(Color.YELLOW, points, 1)
        if ptpdst >= env.renderDist:
            p1 = self.pos.projectedPos( cam)
            if p1[0]:
                points = [(p1[1].x()-self.rad*p1[1].z(), p1[1].y()), (p1[1].x()+self.rad*p1[1].z(), p1[1].y())]
                esc = env.screenClip(points)
                if esc[0]:
                    points = esc[1]
                if (env.inScreen(points[0]) or env.inScreen(points[1])):
                    env.add_edge(self.surfColor, points, 4)
        #Environment.add_edge(self.color, self.surfProjPoints, 0, 2)
            

                
    def drawCore(self, cam):
        env = Environment.Environment
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        if ptpdst < env.renderDist:
            p = self.pos.projectedPos( cam)
            if p[0]:
                di = int((2+self.corHealth/100)*p[1].z())
                pygame.draw.circle(env.getScreen(), (132, 6, 6), p[1].integer().p2D(), di, 0)
    def drawCoreCover(self, cam):
        env = Environment.Environment
        ptpdst = cam.pos.dist2D(self.pos) #player to planet distance
        if ptpdst < env.renderDist:
            p = self.pos.projectedPos( cam)
            if p[0]:
                xy1 = p[1].integer().p2D()
                h1 = 3*p[1].z()
                di = int((2+self.corHealth/100)*p[1].z())
                #(132, 6, 6)
                pygame.draw.ellipse(env.getScreen(), (132, 6, 6) , ((xy1[0]-di, (self.corOffset-h1)+1.5), (di*2, 2*h1)), 0)
    @staticmethod
    def testShotHit(shot):
        x, y, z = shot.pos.Pos()
        lx, ly, lz = shot.lpos.Pos()
        sp = Vex(x, y)
        lsp = Vex(lx, ly)
        dmg = shot.damage/100.0
        for p in Planets.pl:
            d = p.pos.dist2D(sp)
            if d < p.atmos:
                shln = Line(sp-p.pos, lsp-p.pos)
                for lines2 in p.edges:
                    if lines2[1] != 1:
                        lines = Line(p.surfPoints[lines2[0][0]], p.surfPoints[lines2[0][1]])
                        #lines = lines2[0]
                        li = shln.find_intersection(lines)
                        if li:
                            if li.length() > 50:
                                ParticleEngine.Emitter(li+p.pos, shot.angle_rad, 2)
                                a1 = math.atan2(lines.seg[0].Y(), lines.seg[0].X())
                                a2 = math.atan2(lines.seg[1].Y(), lines.seg[1].X())
                                d1 = ZERO.dist2D(lines.seg[0])-dmg
                                d2 = ZERO.dist2D(lines.seg[1])-dmg
                                lines.seg[0].set2D(math.cos(a1)*d1, math.sin(a1)*d1)
                                lines.seg[1].set2D(math.cos(a2)*d2, math.sin(a2)*d2)
                            return True
            if d <= (2+p.corHealth/100):
                hp = (2+p.corHealth/100)
                ang = sp.ang2D(p.pos)
                ParticleEngine.Emitter(Vex(hp*math.cos(ang), hp*math.sin(ang))+p.pos, shot.angle_rad, 2)
                p.corHealth-=dmg
                return True
        return False
    

    @staticmethod
    def testRadiusCollision(ent, np, rad):
        for p in Planets.pl:
            d = np.dist2D(p.pos)
            if d <= p.atmos:
                for lines2 in p.edges:
                    lines = (Line(p.surfPoints[lines2[0][0]], p.surfPoints[lines2[0][1]]), lines2[1])
                        
                    #lines = (Line(lines2[0][0], lines2[0][1]), lines2[1])
                    if lines[1] == 0 or (lines[1] == 1 and ent.inship):
                        delta = np-p.pos # new position relative to planet position
                        ds = lines[0].ClosestPointOnLine(delta) 
                        cpol = delta.dist2D(ds)
                        if cpol<=rad:
                            a = -(lines[0].angle())+math.pi
                            v = Vex(math.sin(a)*rad,  math.cos(a)*rad)+ds+p.pos
                            ParticleEngine.Emitter(ds+p.pos, a, 2)
                            return v
        return None
    
    @staticmethod
    def inAtmosphere(pos):
        for p in Planets.pl:
            if pos.dist2D(p.pos) <= p.atmos:
                return True
        return False
    def getPos(self):
        return self.pos

    def getSurface(self):
        return self.surfPoints
    
    def doAtmosphere(self):
        pickRndSurfacePoints = self.minSize
        step = (360.0 / pickRndSurfacePoints)
        mi = 0
        stp = 1
        for surfacePoint in range(pickRndSurfacePoints):
            sx = math.sin(math.radians(step * surfacePoint))
            sy = math.cos(math.radians(step * surfacePoint))
            x = sx * (self.atmos/Planets.con)*stp
            y = sy * (self.atmos/Planets.con)*stp
            x = sx * (self.atmos)
            y = sy * (self.atmos)
            self.atmosPoints += [Vex(x, y)]
            self.atmosProjPoints += [(0, 0)]

        for i in range(mi, len(self.atmosProjPoints)):
            if i + 1 < len(self.atmosProjPoints):
                self.atmosEdge.append((self.atmosProjPoints[i], self.atmosProjPoints[i + 1]))
            else:
                self.atmosEdge.append((self.atmosProjPoints[i], self.atmosProjPoints[mi]))
                mi = i+1
    
    def doSurface(self):
        pickRndSurfacePoints = random.randint(self.minSize, self.maxSize)
        step = (360.0 / pickRndSurfacePoints)
        mi = 0
        stp = 1
        maxH = 0
        for surfacePoint in range(pickRndSurfacePoints):
            sx = math.sin(math.radians(step * surfacePoint))
            sy = math.cos(math.radians(step * surfacePoint))
            x = sx * (self.rad/Planets.con)*stp
            y = sy * (self.rad/Planets.con)*stp
            #h = (Noise.Perlin3D(x, y, 0, 16, 1, 0, 4))*2
            h = rand2D(x, y)*2
            
            x = sx * (self.rad +h)
            y = sy * (self.rad +h)
            if maxH < h:maxH = h
            self.surfPoints += [Vex(x, y)]
            self.surfProjPoints += [(0, 0)]
            
        self.atmos = maxH + self.rad/5 + self.rad
        
        for i in range(mi, len(self.surfProjPoints)):
            r2 = 0
            r1 = random.randint(0, 20)
            if r1 ==0:r2 =1
            if i + 1 < len(self.surfProjPoints):
                self.edges.append(((i, i + 1), r2))
            else:
                self.edges.append(((i, mi), r2))
                mi = i+1

    
