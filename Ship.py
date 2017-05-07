# Ship
import math
import Color
import Environment

from RPGStats import RPGStats
from Vex import Vex
from Line import Line
from MyMaths import rotate2d
from Weapon import Weapon

class Ship:
    ships = []
    def __init__(self, parent, pos = [0, 0]):
        
        self.parent = parent
        self.stats = RPGStats()
        self.pos = Vex(pos[0], pos[1])
        self.rot = 0
        self.stats.lvlUP()
        
        self.weapon = Weapon(self, [0, 0, .1], [.5, .5, .5], 3)
        self.vexs = []
        self.vexs.extend([Vex(-.5,  .5,   0), Vex(  .5,  .5,    0), Vex( 0.0, -.5,    0), 
                            Vex(0.0,  .5, -.3), Vex( -.25,  .45, -.15), Vex( .25,  .45, -.15)])
        
        self.lines = []
        self.lines.extend([
            Line(self.vexs[0], self.vexs[4]), 
            Line(self.vexs[4], self.vexs[5]),
            Line(self.vexs[5], self.vexs[1]),
            Line(self.vexs[1], self.vexs[2]), 
            Line(self.vexs[2], self.vexs[0]), 
            Line(self.vexs[2], self.vexs[3]), 
            Line(self.vexs[3], self.vexs[0]), 
            Line(self.vexs[3], self.vexs[1]), 
            Line(self.vexs[2], self.vexs[4]), 
            Line(self.vexs[2], self.vexs[5])
        ])
        
        self.shieldVexs = []
        self.shieldEdges = []
        self.shieldRot = [0, 0, 0]
        self.occupied = False
        
        #construct player shield
        sides = 10
        size = 2
        self.shieldRadius = size
        mi = 0
        for sz in range(1, 2):
            sides = int(sides+sz/2)
            #sides = int(sides)
            for i in range(sides):
                angle_deg = (360 / sides) * i 
                angle_rad = 3.14159265359 / 180 * angle_deg
                x = 0 + size*sz * math.cos(angle_rad)
                y = 0 + size*sz * math.sin(angle_rad)
                self.shieldVexs.extend([Vex(x, y, 0)])
            
            for i in range(mi, len(self.shieldVexs)):
                if i + 1 < len(self.shieldVexs):
                    self.shieldEdges.extend([Line(self.shieldVexs[i], self.shieldVexs[i + 1])])
                else:
                    self.shieldEdges.extend([Line(self.shieldVexs[i], self.shieldVexs[mi])])
                    mi=i+1
        
    def getShieldRadius(self):
        return self.shieldRadius
        
    def setParent(self, par):
        self.parent = par
        
    def isOccupied(self):
        return self.occupied
    
    def setOccupied(self, val):
        self.occupied = val
        
    def totalDamage(self):
        return self.stats.getSTR()
        
    def shoot(self, pos, rot, ant):
        self.weapon.Shoot(pos, rot, ant)
        
    def syncPos(self, pos):
        self.pos = pos.copy()
        
    def updatePlayerShip(self, cam):
        env = Environment.Environment    
        self.weapon.update()
        for line in self.lines:
            points = []
            for vec in (line.seg[0], line.seg[1]):
                if not self.isOccupied():
                    x, y, z = ((vec.rotate2dXY(-self.rot)-cam.pos + self.pos).rotate2dXY(cam.rot[1])).Pos()  # roll
                    y, z = rotate2d((y + cam.mov[2], z), cam.rot[0])  # pitch
                else:
                    x, y, z = (vec+self.pos).Pos()
                    y += cam.mov[2]
                    z -= (cam.pos.Z())
                    y, z = rotate2d((y, z), cam.rot[0])  # pitch
                
                f = env.fov / (z+.0000001)
                if(f > env.lim):
                    x, y = x * f, y * f
                else:
                    x, y = x*1000, y*1000
                points += [(env.cx() + int(x), env.cy() + int(y))]
            if (env.inScreen(points[0]) or env.inScreen(points[1])):
                env.add_edge(Color.NEONBLUE, points)
        self.shieldRot[1] = cam.rot[1]
        
        shldH = -(self.stats.getHP()/self.stats.getHTH())/4
        for line in self.shieldEdges:
            points = []
            fs = []
            for vec in (line.seg[0], line.seg[1]):
                if not self.isOccupied():
                    x, y, z = ((vec.rotate2dXY(-self.rot)-cam.pos + self.pos).rotate2dXY(cam.rot[1])).Pos()  # roll
                    y, z = rotate2d((y + cam.mov[2], z), cam.rot[0])  # pitch
                else:
                    x ,  y, z = vec.rotate2dXY(self.shieldRot[1]).Pos()
                    #x, y = rotate2d((x, y), self.shieldRot[1])  # roll
                    x += self.pos.X()
                    y += self.pos.Y() + cam.mov[2]
                    z += self.pos.Z() - cam.pos.Z()

                    y, z = rotate2d((y, z), cam.rot[0])  # pitch
                
                f = env.fov / (z + .00000001)
                if(f > env.lim):
                    x, y = x * f, y * f
                else:
                    x, y = x*1000, y*1000
                points += [(env.cx() + int(x), env.cy() + int(y))]
                fs += [f]
                
            if (env.inScreen(points[0]) or env.inScreen(points[1])):
                env.add_edge(Color.BLUE, points, 1, 1, shldH, fs)
                    
    def updateCreatureShip(self, cam, pos, ang):
        env = Environment.Environment
        self.weapon.update()
        if cam.pos.dist2D(self.pos) < 300:
            for line in self.lines:
                points = []
                
                for vec in (line.seg[0], line.seg[1]):
                    v = ((vec.rotate2dXY(math.radians(ang))-cam.pos + pos).rotate2dXY(cam.rot[1])).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitch
                    
                    f = env.fov / (v.z() +.00000001)
                    if(f < env.lim):
                        f = 1000
                    v = v * f
                    v = v + env.center
                    points += [v.p2D()]
                if (env.inScreen(points[0]) or env.inScreen(points[1])):
                    env.add_edge(Color.NEONBLUE, points)
                    
            hth = -(self.stats.getHP()/self.stats.getHTH())/2
            for line in self.shieldEdges:
                points = []
                fs = []
                for vec in (line.seg[0], line.seg[1]):
                    v = (vec.rotate2dXY( math.radians(ang))-cam.pos+pos).rotate2dXY(cam.rot[1]).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitch

                    f = env.fov / (v.z() +.00000001)
                    fs += [f]
                    if(f < env.lim):
                        f = 1000
                    v = v * f
                    v = v + env.center
                    points += [v.p2D()]
                    
                if (env.inScreen(points[0]) or env.inScreen(points[1])):
                    env.add_edge(Color.BLUE, points, 1, 1, hth, fs)
                    
    @staticmethod
    def remove_unoccupied(ship):
        try:
            Ship.ships.remove(ship)
        except:
            print("boot?")
        
    @staticmethod
    def add_unoccupied(ship):
        Ship.ships += [ship]
        
    @staticmethod
    def updateUnOccupied(cam):
        env = Environment.Environment
        for self in Ship.ships:
            if not self.isOccupied() and cam.pos.dist2D(self.pos) < 300:
                for line in self.lines:
                    points = []
                    
                    for vec in (line.seg[0], line.seg[1]):
                        v = ((vec.rotate2dXY(-self.rot)+self.pos-cam.pos).rotate2dXY(cam.rot[1])).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitch
                        
                        f = env.fov / (v.z() +.00000001)
                        if(f < env.lim):
                            f = 1000
                        v = v * f
                        v = v + env.center
                        points += [v.p2D()]
                    if (env.inScreen(points[0]) or env.inScreen(points[1])):
                        env.add_edge(Color.NEONBLUE, points)
                        
                hth = -(self.stats.getHP()/self.stats.getHTH())/2
                for line in self.shieldEdges:
                    points = []
                    fs = []
                    for vec in (line.seg[0], line.seg[1]):
                        v = ((vec.rotate2dXY(-self.rot)+self.pos-cam.pos).rotate2dXY(cam.rot[1])).rotate2dYZ(cam.mov[2], cam.rot[0])  # pitch
                        
                        f = env.fov / (v.z() +.00000001)
                        fs += [f]
                        if(f < env.lim):
                            f = 1000
                        v = v * f
                        v = v + env.center
                        points += [v.p2D()]
                        
                    if (env.inScreen(points[0]) or env.inScreen(points[1])):
                        env.add_edge(Color.BLUE, points, 1, 1, hth, fs)
