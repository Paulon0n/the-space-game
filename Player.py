# Player
import pygame
import math

import Color
import Ship
import Creature
import DrawINFO

from Vex import Vex
from RPGStats import RPGStats
from ParticleEngine import Emitter
from Planets import Planets
from Asteroid import Asteroid


class Player:
    
    sensorPoints = []
    sensorEdges = []
    player = None
    
    def __init__(self, pos=[0, 0, 0], rot=[0.0, 0.0, 0.0]):
        self.creature = Creature.Creature(self)
        Creature.Creature.PlayerCreature = self.creature
        self.ship = Ship.Ship(self)
        self.ship.weapon.setFireRate(20)
        self.ship.weapon.setCoolrate(200)
        self.inship = False
        self.pos = Vex(pos[0], pos[1], pos[2])
        self.rot = rot
        
        self.cam = Camera(self)
        Player.setPlayer(self)
        self.stats = RPGStats()
        self.stats.lvlUP()
        self.enterShip(self.ship)
        
    def getRadius(self):
        if self.inship:
            return self.ship.getShieldRadius()
        else:
            return self.creature.getRadius()
            
    def totalDamage(self):
        return self.stats.getSTR()*2
        
    def get_cam(self):
        return self.cam
    
    def isAlive(self):
        out = False
        if self.inship:
            if self.ship.stats.hp>0:out = True
        else:
            if self.stats.hp > 0 : out = True
        return out
    
    def exitShip(self):
        self.inship = False
        self.ship.pos = self.cam.pos.copy()
        self.ship.pos.setZ(0)
        self.ship.rot = self.cam.rot[1]
        self.ship.setOccupied(False)
        Ship.Ship.add_unoccupied(self.ship)
        self.ship.setParent(None)
        self.ship = None
        
    
    def enterShip(self, ship):
        Ship.Ship.remove_unoccupied(ship)
        self.ship = ship
        ship.setParent(self)
        self.inship = True
        self.cam.pos = ship.pos.copy().setZ(self.cam.pos.z())
        self.cam.rot[1] = ship.rot
        ship.pos = Vex(0, 0, 0)
        ship.setOccupied(True)
        
    @staticmethod
    def setPlayer(thing):
        Player.player = thing
        
    @staticmethod
    def testShotHit(sh):
        if sh.source != Player.player:
            x, y, z = sh.pos.Pos()
            
            dmg = sh.damage
            player = Player.player
            v = Vex(x, y, z)
            if v.dist2D(player.cam.pos)<=2:
                tdmg = int(dmg - player.stats.getDEX()*(player.stats.doLUK()*10))
                if tdmg>0:
                    DrawINFO.DrawINFO(player.cam.pos.X(), player.cam.pos.Y(), 0, tdmg)
                    if player.inship:
                        player.ship.stats.hpDMG(tdmg)
                    else:
                        player.creature.stats.hpDMG(tdmg)
                else:
                    DrawINFO.DrawINFO(player.cam.pos.X(), player.cam.pos.Y(), 0, "MISS", Color.GREEN)
                return True
        return False
    
    def set_cam_pos(self, x, y, z):
        self.cam.pos.set(x, y, z)
        #self.cam.pos[0]=x;self.cam.pos[1]=y;self.cam.pos[2]=z
    def shoot(self):
        if self.inship:
            self.ship.shoot(self.cam.pos, self.cam.rot[1], self)
        else:
            self.creature.weapon.Shoot(self.cam.pos, self.cam.rot[1], self)
            
    def update(self, cam):
        if Camera.mbd:
            Player.player.shoot()
        self.creature.selfUpdatePlayer( cam, self.pos)
        if self.ship:self.ship.updatePlayerShip(cam)
        
    
   
                

class Camera:
    maxTilt =  math.pi/2 - .3
    mbd = False
    # initialize camera
    def __init__(self, player):
        self.pos = Vex(0.0, 0.0, 0.0)
        self.lpos = self.pos.copy()
        self.rot = [0.0, 0.0, 0.0]
        self.rotSC= [0.0, 0.0]
        self.mov = [0.0, 0.0, 0.0]
        self.sway = 0
        self.sway2 = 0
        self.player = player
        self.minHeight = 1.45
        self.maxHeightS = 60.0
        self.maxHeightC = 30.0
        self.delta = 0
        self.top = True
    # handle events that effect camera
    def events(self, event):
        
        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_rel()
            self.rot[1] -= x / 150  # rol
            self.rot[2] += y / 200  # pitch
            
#            if self.rot[0] > 0:
#                self.rot[0] = 0
#            if self.rot[0] < -Camera.maxTilt:
#                self.rot[0] = -Camera.maxTilt
#            self.mov[2] = self.rot[0] * 2.5
#            print (str(self.rot[0]))
        if event.type == pygame.MOUSEBUTTONDOWN:
            Camera.mbd = True
        if event.type == pygame.MOUSEBUTTONUP:
            Camera.mbd = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                self.top = not self.top
                if self.top:
                    self.rot[0] = 0
                    self.sway2 = self.rot[0] * 2.5
                else:
                    self.rot[0] = -Camera.maxTilt
                    self.sway2 = self.rot[0] * 2.5
                    
            if event.key == pygame.K_j:
                if self.player.inship:
                    self.player.exitShip()
                else:
                    for ship in Ship.Ship.ships:
                        if ship.pos.dist2D(self.pos) < ship.getShieldRadius():
                            self.player.enterShip(ship)    
        self.rotSC = [[math.sin(self.rot[1]), math.cos(self.rot[1])], [math.sin(self.rot[0]), math.cos(self.rot[0])]]
        
    # update camera from keys and other
    def update(self, dt, key):
        height = 0
        if Player.player.inship:
            h = -self.maxHeightS - ((((self.maxHeightS-self.minHeight)/self.maxTilt)*self.rot[0])+self.minHeight)
        else:
            h = -self.maxHeightC - ((((self.maxHeightC-self.minHeight)/self.maxTilt)*self.rot[0])+self.minHeight)
        height =  h
        
        self.pos.setZ( height )
        s = dt*15
        
        self.sway *=.8
        self.mov[2] = -self.sway + self.sway2
        
        self.delta = s
        
        if self.player.inship:
            s = dt * 15
        else:
            s = dt * 2
            
        if key[pygame.K_u]:
            if Player.player.inship:
                Player.player.ship.weapon.temp = 0
            else:
                Player.player.creature.weapon.temp = 0
        
#        if key[pygame.K_r]:
#            self.minHeight -= s
#        if key[pygame.K_f]:
#            self.minHeight += s
        
        jump = 0
        enableJ = True
        if key[pygame.K_k] and key[pygame.K_w] and Player.player.inship and not Planets.inAtmosphere(Player.player.cam.pos):
            jump = 20
        elif key[pygame.K_k] and key[pygame.K_w] and not Player.player.inship:
            jump = .15
            
        # forward /backward
        ms = math.sin(self.rot[1])
        mc = math.cos(self.rot[1])
        if key:
            x, y = (s+jump) * ms, (s+jump) * mc
        
        testedA = Asteroid.testRadiusCollision(Player.player, self.pos, Player.player.getRadius())
        if testedA:
            self.pos.assign(testedA.setZ(self.pos.z()))
            
        tested = Planets.testRadiusCollision(Player.player, self.pos, Player.player.getRadius())
        if tested:
            self.pos.assign(tested.setZ(self.pos.z()))
        else:
            self.lpos.assign(self.pos)
        if key[pygame.K_w]:
            tested = Planets.testRadiusCollision(Player.player, self.pos+Vex(-x, -y), Player.player.getRadius())
            testedA = Asteroid.testRadiusCollision(Player.player, self.pos+Vex(-x, -y), Player.player.getRadius())
            if not tested:
                if not testedA:
                    enableJ = True
                    self.pos.setX(self.pos.X() - x )
                    self.pos.setY(self.pos.Y() - y )
                else:
                    self.pos.assign(testedA.setZ(self.pos.z()))
            else:
                self.pos.assign(tested.setZ(self.pos.z()))

        if key[pygame.K_s]:
            tested = Planets.testRadiusCollision(Player.player, self.pos+Vex(x, y), Player.player.getRadius())
            testedA = Asteroid.testRadiusCollision(Player.player, self.pos+Vex(x, y), Player.player.getRadius())
            if not tested:
                if not testedA:
                    self.pos.setX(self.pos.X() + x )
                    self.pos.setY(self.pos.Y() + y )
                else:
                    self.pos.assign(testedA.setZ(self.pos.z()))
            else:
                self.pos.assign(tested.setZ(self.pos.z()))

        # straff left /right
        x, y = s * ms, s * mc
        if key[pygame.K_a]:
            tested = Planets.testRadiusCollision(Player.player, self.pos+Vex(-y, x), Player.player.getRadius())
            testedA = Asteroid.testRadiusCollision(Player.player, self.pos+Vex(-y, x), Player.player.getRadius())
            if not tested:
                if not testedA:
                    self.pos.setX(self.pos.X() - y )
                    self.pos.setY(self.pos.Y() + x )
                else:
                    self.pos.assign(testedA.setZ(self.pos.z()))
            else:
                self.pos.assign(tested.setZ(self.pos.z()))

        if key[pygame.K_d]:
            tested = Planets.testRadiusCollision(Player.player, self.pos+Vex(y, -x), Player.player.getRadius())
            testedA = Asteroid.testRadiusCollision(Player.player, self.pos+Vex(y, -x), Player.player.getRadius())
            
            if not tested:
                if not testedA:
                    self.pos.setX(self.pos.X() + y )
                    self.pos.setY(self.pos.Y() - x )
                else:
                    self.pos.assign(testedA.setZ(self.pos.z()))
            else:
                self.pos.assign(tested.setZ(self.pos.z()))
        
        if jump == 10 and enableJ:
            Emitter(self.pos.copy().setZ(0), self.rot[1], 3)
            self.sway += jump/15
    
    
