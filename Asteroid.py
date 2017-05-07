'''
    Asteroid
'''
import math
import MyMaths
from random import randint, uniform
from Vex import Vex
import Environment
from Line import Line
import ParticleEngine


ZERO = Vex(0, 0, 0)

class Asteroid:
    asteroids = []
    def __init__(self, par, pos=Vex(0, 0, 0), minSize=4, maxSize=8):
        self.parent = par
        self.pos = pos
        self.scale = Vex(randint(1, 5), randint(1, 5))
        self.rot = math.radians(randint(0, 360))
        self.speed = uniform(0.001, 1)
        self.edges = []
        rc = randint(25, 255)
        self.color = (rc, rc, rc)
        self.corHealth = 300
        mi = 0
        self.points = []
        self.projectedPoints = []
        size = randint(8, 16)
        step = 360.0/size
        
        for i in range(0, size):
            sx = math.sin(math.radians(step * i))
            sy = math.cos(math.radians(step * i))
            d = MyMaths.rand2D(sx, sy)+2
            tv = Vex(sx*d, sy*d)
            self.points += [tv]
            self.projectedPoints += [0, 0]
        
        for i in range(mi, len(self.points)):
            if i + 1 < len(self.points):
                self.edges.append((i, i + 1))
            else:
                self.edges.append((i, mi))
                mi = i+1
    
    @staticmethod
    def add_asteroid(ast):
        Asteroid.asteroids += [ast]
    
    @staticmethod
    def remove_asteroid(ast):
        Asteroid.asteroids.remove(ast)
    
    @staticmethod
    def update(cam):
        env = Environment.Environment
        r1 = cam.rotSC[0]
        r2 = cam.rotSC[1]
        
        for self in Asteroid.asteroids:
            if cam.pos.dist2D(self.pos)<500:
                self.rot += .001
                self.pos.addVector(self.speed, self.rot)
                for i, p in enumerate(self.points):
                    v = (p.rotate2dXY(self.rot)*self.scale+self.pos-cam.pos).rotate2dXY(r1).rotate2dYZ(cam.mov[2], r2)  # pitch
                        
                    f = env.fov / (v.z()+.000000001)
                    if(f < env.lim):
                        f = 1000
                    v = v * f
                    v = v + env.center
                    self.projectedPoints[i] = v.p2D()
      
                env.add_edge(self.color, self.projectedPoints, 1, 2)
    
    @staticmethod
    def create(count = 10):
        sz = 100
        for i in range(0, count):
            a = Asteroid(Vex(randint(-sz, sz), randint(-sz, sz)))
            Asteroid.asteroids += [a]
    
    @staticmethod
    def testShotHit(shot):
        x, y, z = shot.pos.Pos()
        lx, ly, lz = shot.lpos.Pos()
        sp = Vex(x, y)
        lsp = Vex(lx, ly)
        #dmg = shot.damage/100.0
        for p in Asteroid.asteroids:
            d = p.pos.dist2D(sp)
            if d < 50:
                shln = Line(sp-p.pos, lsp-p.pos)
                for lines2 in p.edges:
                    lines = (Line((p.points[lines2[0]])*p.scale, (p.points[lines2[1]])*p.scale))
                    li = shln.find_intersection(lines)
                    if li:
                        ParticleEngine.Emitter(li+p.pos, shot.angle_rad, 2)
                        return True
        return False
    

    @staticmethod
    def testRadiusCollision(ent, np, rad):
        v = np.copy()
        out = Vex(0, 0)
        edit = False
        for p in Asteroid.asteroids:
            d = v.dist2D(p.pos)
            if d <= 20:
                for lines2 in p.edges:
                    lines = (Line(p.points[lines2[0]]*p.scale, p.points[lines2[1]]*p.scale))
                   
                    delta = v-p.pos # new position relative to asteroid position
                    ds = lines.ClosestPointOnLine(delta) 
                    cpol = delta.dist2D(ds)
                    if cpol<=rad:
                        rad+=.1
                        a = -(lines.angle())+math.pi
                        v = Vex(math.sin(a)*rad,  math.cos(a)*rad)+ds+p.pos
                        out.assign (v)
                        edit = True
        if edit:
            return out
        else:
            return None
