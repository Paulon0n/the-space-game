
import pygame
import sys
import os
from Environment import Environment
from Player import Player
from Mind import Mind
from Background import Stars
import Color


pygame.init()


def drawBar(barW, pos, color,  value, high, desc):
    
    pygame.draw.rect(env.getScreen(), Color.BLACK, (0, 5+15*pos, barW, 10))
    pygame.draw.rect(env.getScreen(), color, (0, 5+15*pos, barW, 10), 1)
    #if player.inship:
    val = (barW-1)/(high+.000001) * value
    if val < 0 : val = 0
    if val > 298: val = 298
    pygame.draw.rect(Environment.getScreen(), color, (1, 6+15*pos, val, 8))
    myfont.set_bold(True)
    label = myfont.render(str(value)+"/"+str(high), 1, (255, 255, 0))
    screen.blit(label, (barW, 1+15*pos))
    screen.blit(myfont.render(desc, 1, (255, 255, 255)), (0, 1+15*pos))
    myfont.set_bold(False)

def drawEnt(pos, ent, width, height, pad):
    height = height + pad
    st = ent.state
    lncol = (40, 40, 40)
    bxcol = lncol
    if st == Mind.ATTACK or st == Mind.BERZERK or st == Mind.FIRE:
        lncol = Color.RED
        bxcol = lncol
    if st == Mind.ROAM:
        lncol = (16, 38, 14)
        bxcol = (0, 255, 0)
    x, y = ent.creature.projectedPos(Player.player.get_cam())
    x2, y2 = width, 5+height*pos+(height+2)/2
    if x >= x2 :
        pygame.draw.line(env.getScreen(), lncol, (x, y), (x2, y2))
    
    y = 5+(height*pos)+pos+2
    pygame.draw.rect(env.getScreen(), Color.BLACK, (0, y, width, height+2-pad))
    pygame.draw.rect(env.getScreen(), bxcol, (0, y, width, height+2-pad), 1)
    screen.blit(ent.creature.img, (0, y+1))
    
    
pitch, yaw, roll = 0, 1, 2
lens = 10



sw, sh = 800, 600  # screen width & height
os.environ['SDL_VIDEO_CENTERED'] = '1'
env = Environment(sw, sh)
player = Player()
Environment.player = player
bkg = Stars.init(player.cam)

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.SysFont("consolas", 15)

screen = env.getScreen()
screen.set_alpha(None)
pygame.display.set_caption('Test game')
clock = pygame.time.Clock()
FPS = 120

player.set_cam_pos(0, -10, -5)

pygame.event.get()
pygame.mouse.get_rel()
pygame.mouse.set_visible(0)
pygame.event.set_grab(1)

planets =[]
# these are testers
#for i in range(100):
#    planets += [Planets((random.randint(-5000, 5000), random.randint(-5000, 5000)))]
#planet = Planets([0, -500, 0])
#sun = Sun((0, -500))
#Environment.sun = sun
for i in range(10):
    Mind(player.cam)

#Asteroid.create()



crashed = False
lscv = 0

mbd = False
start_timer  = 0
shotType = 0
deltaTime2 = 1
mouseRel = False
while not crashed:
    pygame.display.set_caption(('FPS: ' + str("%.2f" % (1000/deltaTime2))))
    #clock.tick(FPS)
    deltaTime2 = clock.tick(FPS)
    deltaTime = deltaTime2 / 1000
    
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                crashed = True
            if event.key == pygame.K_SPACE:
                mouseRel = not mouseRel
                if mouseRel:
                    pygame.mouse.set_visible(1)
                    pygame.event.set_grab(0)
                else:
                    pygame.mouse.set_visible(0)
                    pygame.event.set_grab(1)
                    
        if not mouseRel:
            player.get_cam().events(event)
        
    Environment.updateGlobalPosition(player.cam.pos)
    Environment.update(player.cam)
    
    
    if player.inship:
        drawBar(300, 0, Color.BLUE, player.ship.stats.xp, player.ship.stats.nxtlvlxp, "XP")
        drawBar(300, 1, Color.RED, player.ship.weapon.getTemp(), 100, "TEMP")
        drawBar(300, 2, Color.GREEN, player.ship.stats.getHP(), player.ship.stats.getHTH(), "HP")
    else:
        drawBar(300, 0, Color.BLUE, player.creature.stats.xp, player.creature.stats.nxtlvlxp, "XP")
        drawBar(300, 1, Color.RED, player.creature.weapon.getTemp(), 100, "TEMP")
        drawBar(300, 2, Color.GREEN, player.creature.stats.getHP(), player.creature.stats.getHTH(), "HP")
    
    i = 0
    for e in Environment.visible_creatures:
        drawEnt(2+i, e, 128, 32, 2)
        i += 1
    
    label = myfont.render(str("%.2f" % player.cam.pos.length()) + "   gPos:"+str(Environment.gpos), 1, (255, 255, 255))
    screen.blit(label, (256, 1+15*4))
    pygame.display.flip()
   
    key = pygame.key.get_pressed()

    player.get_cam().update(deltaTime, key)


pygame.quit()
sys.exit()


        
