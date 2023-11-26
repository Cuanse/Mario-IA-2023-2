# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 11:48:24 2023

@author: jtiquet
"""

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.clock import Clock

from kivy.vector import Vector
from kivy.properties import NumericProperty, ReferenceListProperty

from agent import Agent
import uuid
import random



def getImage(path, region):
    texture = CoreImage(path).texture
    row, column, sizex, sizey = region
    #print(row, column, sizex, sizey)
    region = texture.get_region(
        16 * column, texture.height - 16 * (row), sizex, sizey)
    image = Image(texture=region)
    image.allow_stretch = True
    # -- Apparently these variables are static global between hitboxes? bug maybe
    image.size_hint_x = 1
    image.size_hint_y = 1

    image.pos_hint['x'] = 0
    image.pos_hint['y'] = 0

    return image


def WidgetCollision(widget_item, game):
    '''

    Parameters
    ----------
    widget_item : Widget
        te item inherent from game that want to confirm if it collide with something.
    game : Widget
        The game where it is located.

    Returns
    -------
    iscollision : Bool
        if there is a confirmed collision.
    collide_widget : List of Widgets
        The widgets whith whom it collide.

    '''
    iscollision = False
    collide_widget = []

    # -1 to avoid principal layout (is also a children)
    for i in range(0, len(game.children)-1):
        obj = game.children[i]
        if not obj == widget_item:
            if widget_item.collide_widget(obj):
                iscollision = True
                collide_widget.append(obj)

    return iscollision, collide_widget


class MarioGame(Widget):
    isready = False
    EnemyList = []
    BrickList = []
    FloorList = []
    PipeList = []
    PowerupList = []
    EntityList = []
    visibleentityList = []
    timer = 0
    stateId = 0
    agentOrders = []
    currentState = 0
    infolabel = Label(text='Press click \nto start simulation',color=(0,0,0,1), font_size='15sp',pos = (650, 100))

    def __str__(self):
        return 'MarioGame'

    def load_textures(self):
        #self.add_widget(Label(text='hello to my\n nono zone',color=(0,0,0,1), font_size='20sp',pos = (500, 100)))
        self.add_widget(self.infolabel)
        self.mario.hitbox.add_widget(self.mario.getImage())
        
        # -- I got lazy to complicate myself into searching positions, each squeare lenght is 16.
        CreateEnemy(self, 300+16*6, 24)
        manyBricks(self, 1, 300+16*6, 24+16*3)
        manyBricks(self, 1, 300+16*4, 24+16*3)
        manyBricks(self, 1, 300+16*2, 24+16*3)
        
        # manyFloor(self,36,0,8)
        GiantFloor(self, 0, 69*16)
        GiantFloor(self, 70*16, 16*16)
        manyBricks(self, 1, 70*16+16*6, 24+16*3)
        manyBricks(self, 1, 70*16+16*8, 24+16*3)
        CreateEnemy(self, 70*16+16*14, 24+16*7)
        manyBricks(self, 9, 70*16+16*10, 24+16*6)
        
        manyBricks(self, 4, 70*16+16*22, 24+16*6)
        manyBricks(self, 1, 70*16+16*26, 24+16*3)
        CreateEnemy(self, 70*16+16*28, 24)
        CreateEnemy(self, 70*16+16*28, 24)
        manyBricks(self, 2, 70*16+16*30, 24+16*3)
        CreateEnemy(self, 70*16+16*42, 24)
        CreateEnemy(self, 70*16+16*43, 24)
        GiantFloor(self, 89*16, 63*16)
        manyHardBricks(self, 4, 134*16, 24)
        manyHardBricks(self, 3, 135*16, 24+16*1)
        manyHardBricks(self, 2, 136*16, 24+16*2)
        manyHardBricks(self, 1, 137*16, 24+16*3)
        
        manyHardBricks(self, 4, 140*16, 24)
        manyHardBricks(self, 3, 140*16, 24+16*1)
        manyHardBricks(self, 2, 140*16, 24+16*2)
        manyHardBricks(self, 1, 140*16, 24+16*3)
        
        manyHardBricks(self, 5, 148*16, 24)
        manyHardBricks(self, 4, 149*16, 24+16*1)
        manyHardBricks(self, 3, 150*16, 24+16*2)
        manyHardBricks(self, 2, 151*16, 24+16*3)
        
        manyHardBricks(self, 4, 155*16, 24)
        manyHardBricks(self, 3, 155*16, 24+16*1)
        manyHardBricks(self, 2, 155*16, 24+16*2)
        manyHardBricks(self, 1, 155*16, 24+16*3)
        GiantFloor(self, 155*16, 57*16)

        GiantPipe(self, 448)
        GiantPipe(self, 448+10*16)
        CreateEnemy(self, 448+12*16, 24)
        GiantPipe(self, 448+18*16)
        CreateEnemy(self, 448+19*16, 24)
        CreateEnemy(self, 448+20*16, 24)
        GiantPipe(self, 448+29*16)
        GiantPipe(self, 448+135*16)
        GiantPipe(self, 448+151*16)
        manyHardBricks(self, 9, 448+153*16, 24)
        manyHardBricks(self, 8, 448+154*16, 24+16*1)
        manyHardBricks(self, 7,448+155*16, 24+16*2)
        manyHardBricks(self, 6, 448+156*16, 24+16*3)
        manyHardBricks(self, 5, 448+157*16, 24+16*4)
        manyHardBricks(self, 4, 448+158*16, 24+16*5)
        manyHardBricks(self, 3, 448+159*16, 24+16*6)
        manyHardBricks(self, 2, 448+160*16, 24+16*7)

        CreateMushroom(self, 300, 50)

        #CreateStar(self, 300, 50)

        self.Alice = Agent()
        # self.Alice.lastdecision()

        self.EntityList = self.EnemyList+self.PowerupList

    def update(self, dt):
        if self.isready and self.mario.isalive:
            if self.timer == 2000 or not self.mario.isalive:
                self.mario.isalive= True
                self.Alice.remember()
                self.timer = 0
                '''
                self.clear_widgets(self.children)
                self.load_textures()
                '''
                self.mario.pos = (64, 50)
                self.gamepov.pos = (0,0)
                
            if self.timer == 0:
                self.agentOrders = self.Alice.getOrders()
    
            for widget in self.children:
                if widget.x <= self.right:
                    #print(widget.parent.__str__(), widget.__str__())
                    if widget in self.EntityList:
                        if widget not in self.visibleentityList:
                            self.visibleentityList.append(widget)
    
            prevStatId = self.currentState
            isexploring = True if self.agentOrders == [] else False
            #print(self.agentOrders, dt, isexploring)
            if isexploring:
                nextStatId = uniqueId = uuid.uuid1()
                # print(uniqueId)
                timer = self.timer
                options = self.mario.mvoptions
                heuristic = self.Alice.getHeuristic()
                self.Alice.setStats(uniqueId, timer, options, heuristic)
                actionindex = self.Alice.takedecision(prevStatId, options)
            else:
                actionindex = self.agentOrders.pop()
                self.currentState = self.Alice.maxheuristicId
    
            
    
            self.mario.mv(actionindex)
            for entity in self.visibleentityList:
                entity.mv()
    
            # -- Mario Reach center of game and pov must change to everything
            # BE CAREFUL: it updates position, so Agent/state info will change
            if self.mario.center_x > self.center_x:
                for widget in self.children:
                    if not widget == self.infolabel:
                        widget.x += -self.mario.velocity_x
    
            if isexploring:
                self.Alice.setTransition(prevStatId, actionindex, nextStatId)
                self.currentState = nextStatId
            self.timer += 1
            self.infolabel.text = f'intento:63997\ntimer:{self.timer}\nobj_State:{self.currentState}\nAction:{actionindex}\nReward:{self.gamepov.right}'

    def on_touch_up(self, touch):
        #self.mario.setMove_x()
        pass

    def on_touch_down(self, touch):
        self.mario.jump()
        #self.mario.setMove_x(vel=self.mario.velocity_x+1,acel=1)
        self.isready = True


class MarioApp(App):
    def build(self):
        game = MarioGame()
        game.load_textures()
        Clock.schedule_interval(game.update, 1/30)
        return game


class Entity():
    acel_x = NumericProperty(0)
    acel_y = NumericProperty(-1)

    velocity_x = NumericProperty(-1)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __str__(self):
        return 'Entity'

    def __init__(self):
        self.gravity = -1
        self.gravity_limit = -1

    def gravityLimits(self):
        # -- Gravity limits --
        if self.acel_y > self.gravity_limit:
            self.acel_y += self.gravity
        else:
            self.acel_y = self.gravity_limit

        if self.velocity_y < -4:
            self.velocity_y = -4

    def colisionFilters(self):
        pass

    def setMove_x(self, vel=0, acel=0):
        self.acel_x = acel
        self.velocity_x = vel

    def setMove_y(self, vel=0, acel=0):
        self.acel_y = acel
        self.velocity_y = vel


class GamePov(Widget):
    def __str__(self):
        return 'innecesary junk'
    pass


class Mario(Widget, Entity):
    mvoptions = [False, True, True, True]
    isGrown = False
    isStar = False
    invencible = 0
    isalive = True

    '''
    # NO BUILDERS -> kivy implementation
    def __init__(self):
        self.add_widget(self.getImage())
    '''

    def __str__(self):
        return 'mario'

    def getImage(self):
        # Mario Sprite has some junk pixels
        image = getImage('.\\img\\mario_bros.png', (3, 11, 16, 16))
        image.pos = self.pos
        return image

    def getImageGrown(self):
        # Mario Sprite has some junk pixels
        image = getImage('.\\img\\mario_bros.png', (2, 11, 16, 32))
        image.pos = self.pos
        return image

    def getImageInvencible(self):
        # Mario Sprite has some junk pixels
        image = getImage('.\\img\\mario_bros.png', (15, 11, 16, 16))
        image.pos = self.pos
        return image

    def getImageInvencibleGrown(self):
        # Mario Sprite has some junk pixels
        image = getImage('.\\img\\mario_bros.png', (14, 11, 16, 32))
        image.pos = self.pos
        return image

    def mv(self, actionindex):
        # - Invencible filters
        if not self.invencible == 0:
            if self.invencible == 1:
                self.isStar = False
                self.Grow() if self.isGrown else self.shrink()
            self.invencible -= 1
        # - 4 index is always True because it represent "waiting"
        # - [Jump, right, left, wait]
        self.setMove_x()
        self.mvoptions = [False, True, True, True]
        self.isalive = True
        canjump = False
        '''
        loco = random.randint(0, 18)
        
        if loco == 0:
            pass
        elif loco == 1:
            self.velocity_x = -1
        elif loco == 2:
            #self.jump()
            canjump = True
        else:
            self.velocity_x = 1
        '''

        if actionindex == 0:
            canjump = True
        elif actionindex == 1:
            self.setMove_x(4)
        elif actionindex == 2:
            self.setMove_x(-4)
        elif actionindex == 3:
            pass

        iscollide, who = WidgetCollision(self, self.parent)
        self.velocity_x += self.acel_x  # There is no aceleration in x yet
        self.velocity_y += self.acel_y

        self.gravityLimits()

        # -- Colission Filters --
        if iscollide:
            # print(who)
            for item in who:
                if item in self.parent.EnemyList:
                    if self.isStar:
                        self.kill(item)
                    else:
                        #and self.y >= item.y - abs(self.velocity_y)
                        if not (self.center_y > item.top ):
                            if self.invencible == 0:
                                if self.isGrown:
                                    print(self.y,item.top,self.velocity_y)
                                    self.shrink()
                                    self.invencible = 60
                                else:
                                    
                                    self.isalive = False
                                    self.pos = (64, 50)
                                    self.parent.timer = 0
                        else:
                            # miniJump
                            self.setMove_y(vel=1, acel=2)
                            # Kill Enemy
                            self.kill(item)
                elif item in self.parent.BrickList or item in self.parent.FloorList or item in self.parent.PipeList:

                    # There is a priority order
                    if self.y <= item.top and self.y >= item.top - abs(self.velocity_y):
                        if canjump:
                            self.jump()
                        #print(f'NormalCollisionBlock - {item}')
                        self.mvoptions[0] = True
                        self.y = item.top
                        if self.velocity_y < 0:
                            self.setMove_y()
                    elif item.y <= self.top and item.y >= self.top - abs(self.velocity_y):
                        #print('break it - your on bottom of it')
                        if self.isGrown:
                            self.breakit(item) 
                        self.top = item.y
                        if self.velocity_y > 0:
                            self.setMove_y()
                    elif self.right >= item.x and self.right >= item.x - abs(self.velocity_x):
                        #print(f'touching right - {item}')
                        self.mvoptions[1] = False
                        self.right = item.x
                        if self.velocity_x > 0:
                            self.setMove_x()
                    elif item.right == self.x:
                        #print(f'touching left - {item}')
                        self.mvoptions[2] = False
                        #self.x = item.right
                        if self.velocity_x < 0:
                            self.setMove_x()
                elif item in self.parent.PowerupList:
                    self.consume(item)

        # update position once all collision filters have passed
        self.pos = Vector(*self.velocity) + self.pos

        if self.y < -10:
            self.isalive = False
        if self.x < 0:
            self.x = 0
            self.mvoptions[2] = False

    def jump(self):
        self.acel_y = 3

    def kill(self, enemy):
        print('-------- DEEEEEEEEEEEAD ---------')
        self.parent.EnemyList.pop(self.parent.EnemyList.index(enemy))
        self.parent.visibleentityList.pop(
            self.parent.visibleentityList.index(enemy))
        self.parent.remove_widget(enemy)

    def breakit(self, block):
        self.parent.BrickList.pop(self.parent.BrickList.index(block))
        self.parent.remove_widget(block)

    def Grow(self):
        self.isGrown = True
        self.hitbox.clear_widgets(self.hitbox.children)
        self.hitbox.size = (16, 32)
        self.size = (16, 32)
        self.hitbox.add_widget(self.getImageGrown())

    def shrink(self):
        self.isGrown = False
        self.hitbox.clear_widgets(self.hitbox.children)
        self.hitbox.size = (16, 16)
        self.size = (16, 16)
        self.hitbox.add_widget(self.getImage())

    def consume(self, powerup):
        self.parent.PowerupList.pop(self.parent.PowerupList.index(powerup))
        self.parent.visibleentityList.pop(
            self.parent.visibleentityList.index(powerup))
        self.parent.remove_widget(powerup)
        if powerup.__str__() == 'mushroom':
            if not self.isGrown:
                self.Grow()
        if powerup.__str__() == 'star':
            self.isStar = True
            self.hitbox.clear_widgets(self.hitbox.children)
            self.hitbox.add_widget(self.getImageInvencibleGrown(
            ) if self.isGrown else self.getImageInvencible())
            self.invencible = 150


class Brick(Widget):
    def __str__(self):
        return 'brick'

    def getImage(self):
        image = getImage('.\\img\\tile_set.png', (1, 1, 16, 16))
        image.pos = self.pos
        return image

class HardBrick(Widget):
    def __str__(self):
        return 'hardbrick'

    def getImage(self):
        image = getImage('.\\img\\tile_set.png', (2, 0, 16, 16))
        image.pos = self.pos
        return image

def manyBricks(game, number, wherex, wherey):
    # An example of how iterate on this previous objects
    lineofBricks = []
    for i in range(number):
        lineofBricks.append(Brick())
    count = 0
    for e in lineofBricks:
        e.hitbox.add_widget(e.getImage())
        #e.hitbox.add_widget(Label(text='0,35',color=(0,0,0,1), font_size='10sp'))
        e.pos = (wherex, wherey)
        game.add_widget(e)
        game.BrickList.append(e)
        wherex += 16
    # -- END EXAMPLE

def manyHardBricks(game, number, wherex, wherey):
    # An example of how iterate on this previous objects
    lineofBricks = []
    for i in range(number):
        lineofBricks.append(HardBrick())
    count = 0
    for e in lineofBricks:
        e.hitbox.add_widget(e.getImage())
        #e.hitbox.add_widget(Label(text='0,35',color=(0,0,0,1), font_size='10sp'))
        e.pos = (wherex, wherey)
        game.add_widget(e)
        game.BrickList.append(e)
        wherex += 16
    # -- END EXAMPLE
class Pipe(Widget):
    def __str__(self):
        return 'pipe'

    def getImage(self):
        image = getImage('.\\img\\tile_set.png', (10, 0, 32, 32))
        image.pos = (self.x, self.y)
        return image

    def getTube(self):
        image = getImage('.\\img\\tile_set.png', (10, 0, 32, 16))
        image.pos = self.pos
        return image


def GiantPipe(game, wherex, height=2):
    test = Pipe()
    test.size = (32, 16*height)
    test.pos = (wherex, 24)
    test.hitbox.add_widget(test.getImage())
    test.hitbox.add_widget(Label(text='0,1',color=(0,0,0,1)))
    # test.hitbox.add_widget(test.getTube())
    game.PipeList.append(test)
    game.add_widget(test)


class Enemy(Widget, Entity):
    def __str__(self):
        return 'enemy'

    def getImage(self):
        # enemies.png has an entire line of junk pixels
        image = getImage('.\\img\\enemies.png', (2, 1, 16, 16))
        image.pos = self.pos
        return image

    def mv(self):

        iscollision, who = WidgetCollision(self, self.parent)
        self.velocity_x += self.acel_x
        self.velocity_y += self.acel_y
        self.gravityLimits()
        # -- Collision Filters
        if iscollision:
            for item in who:
                if item in self.parent.BrickList or item in self.parent.FloorList or item in self.parent.PipeList:
                    if self.y <= item.top and self.y >= item.top - abs(self.velocity_y):
                        if self.velocity_y < 0:
                            self.velocity_y = 0
                            self.y = item.top
                    elif self.right == item.x:
                        if self.velocity_x > 0:
                            self.velocity_x *= -1
                    elif item.right == self.x:
                        if self.velocity_x < 0:
                            self.velocity_x *= -1
        self.pos = Vector(*self.velocity) + self.pos


def CreateEnemy(game, wherex, wherey):
    test = Enemy()
    test.pos = (wherex, wherey)
    test.hitbox.add_widget(test.getImage())
   # test.hitbox.add_widget(Label(text='0,1',color=(0,0,0,1), font_size='10sp'))
    game.add_widget(test)
    game.EnemyList.append(test)


class Floor(Widget):
    def __str__(self):
        return 'floor'
    # -- its atributes are implemented already in .kv file
    pass


def GiantFloor(game, wherex, lenght):
    initialFloor = Floor()
    initialFloor.pos = (wherex, -8)
    initialFloor.size = (lenght, 32)
    game.add_widget(initialFloor)
    game.FloorList.append(initialFloor)


def manyFloor(game, number, wherex, wherey):
    lineofFloor = []
    for i in range(number):
        lineofFloor.append(Floor())
    for e in lineofFloor:
        e.pos = (wherex, wherey)
        game.add_widget(e)
        game.FloorList.append(e)
        wherex += 16


class Mushroom(Widget, Entity):
    def __str__(self):
        return 'mushroom'

    def getImage(self):
        image = getImage('.\\img\\item_objects.png', (1, 0, 16, 16))
        image.pos = self.pos
        return image

    def mv(self):

        iscollision, who = WidgetCollision(self, self.parent)
        self.velocity_x += self.acel_x
        self.velocity_y += self.acel_y
        self.gravityLimits()
        # -- Collision Filters
        if iscollision:
            for item in who:
                if item in self.parent.BrickList or item in self.parent.FloorList or item in self.parent.PipeList:
                    if self.y <= item.top and self.y >= item.top - abs(self.velocity_y):
                        if self.velocity_y < 0:
                            self.velocity_y = 0
                            self.y = item.top
                    elif self.right == item.x:
                        if self.velocity_x > 0:
                            self.velocity_x *= -1
                    elif item.right == self.x:
                        if self.velocity_x < 0:
                            self.velocity_x *= -1
        self.pos = Vector(*self.velocity) + self.pos


def CreateMushroom(game, wherex, wherey):
    test = Mushroom()
    test.pos = (wherex, wherey)
    test.hitbox.add_widget(test.getImage())
    game.add_widget(test)
    game.PowerupList.append(test)


class Star(Widget, Entity):
    def __str__(self):
        return 'star'

    def getImage(self):
        image = getImage('.\\img\\item_objects.png', (4, 0, 16, 16))
        image.pos = self.pos
        return image

    def mv(self):

        iscollision, who = WidgetCollision(self, self.parent)
        self.velocity_x += self.acel_x
        self.velocity_y += self.acel_y
        self.gravityLimits()
        # -- Collision Filters
        if iscollision:
            for item in who:
                if item in self.parent.BrickList or item in self.parent.FloorList or item in self.parent.PipeList:
                    if self.y <= item.top and self.y >= item.top - abs(self.velocity_y):
                        if self.velocity_y < 0:
                            self.velocity_y = 0
                            self.y = item.top
                        self.jump()
                    elif item.y == self.top:
                        if self.velocity_y > 0:
                            self.velocity_y = 0
                            self.top = item.y
                    elif self.right == item.x:
                        if self.velocity_x > 0:
                            self.velocity_x *= -1
                    elif item.right == self.x:
                        if self.velocity_x < 0:
                            self.velocity_x *= -1
        self.pos = Vector(*self.velocity) + self.pos

    def jump(self):
        self.acel_y = 3


def CreateStar(game, wherex, wherey):
    test = Star()
    test.pos = (wherex, wherey)
    test.hitbox.add_widget(test.getImage())
    game.add_widget(test)
    game.PowerupList.append(test)

if __name__ == '__main__':
    MarioApp().run()
