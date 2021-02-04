import arcade
import random
import math
from abc import ABC, abstractmethod


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BULLET_RADIUS =30
BULLET_SPEED = 20
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.05
SHIP_RADIUS = 30

INITIAL_ROCK_COUNT = 5

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MEDIUM_ROCK_SPIN = -2
MEDIUM_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2
class Point:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        
class Velocity:
    def __init__(self):
        self.x = 0
        self.y = 0
        
class Flying_Object(ABC):
    def __init__(self,img):
        self.center = Point()
        self.velocity = Velocity()
        self.alive = True
        self.img = img
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.radius = SHIP_RADIUS
        self.angle = 0
        self.speed = 0
        self.direction = 0
        self.velocity.dx = math.cos(math.radians(self.direction)) * self.speed
        self.velocity.dy = math.sin(math.radians(self.direction)) * self.speed
        
    def advance(self):
        self.center.y += self.velocity.dy
        self.center.x += self.velocity.dx
        
    def is_alive(self):
        return self.alive
    
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x,self.center.y,self.width,self.height,self.texture,self.angle,255)
   
    def wrap(self):
        if self.center.x > SCREEN_WIDTH:
            self.center.x -= SCREEN_WIDTH
        if self.center.x < 0:
            self.center.x += SCREEN_WIDTH
        if self.center.y > SCREEN_HEIGHT:
            self.center.y -= SCREEN_HEIGHT
        if self.center.y < 0:
            self.center.y += SCREEN_HEIGHT
  
class Bullet(Flying_Object):
    def __init__(self,ship_angle,ship_x,ship_y):
        super().__init__("images/laser.png")
        self.radius = BULLET_RADIUS
        self.life = BULLET_LIFE
        self.speed = BULLET_SPEED
        self.angle = ship_angle +90
        self.center.x = ship_x
        self.center.y = ship_y
        
               
    def fire(self):
        self.velocity.dx = math.cos(math.radians(self.angle )) * BULLET_SPEED
        self.velocity.dy = math.sin(math.radians(self.angle )) * BULLET_SPEED
        
    def advance(self):
        super().advance()
        self.life -= 1
        if (self.life <= 0):
            self.alive = False
        
        
class Ship(Flying_Object):
    def __init__(self):
        super().__init__("images/falcon.png")
        self.angle = 1
        self.center.x = (SCREEN_WIDTH/2)
        self.center.y = (SCREEN_HEIGHT/2)
        self.radius = SHIP_RADIUS
        
    def left(self):
        self.angle += SHIP_TURN_AMOUNT
    def right(self):
        self.angle -= SHIP_TURN_AMOUNT
    def thrust(self):
        self.velocity.dx -= math.cos(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        self.velocity.dy += math.sin(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        
    def neg_thrust(self):
        self.velocity.dx += math.cos(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        self.velocity.dy -= math.sin(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        
class Asteroid(Flying_Object):
    def __init__(self,img):
        super().__init__(img)
        self.radius = 0.0
        
class SmallRock(Flying_Object):
    def __init__(self):
        super().__init__("images/roka.png")
        self.radius = SMALL_ROCK_RADIUS
        
    def advance(self):
        super().advance()
        self.angle += SMALL_ROCK_SPIN
        
    def break_apart(self, asteroids):
        self.alive = False
        
class MediumRock(Flying_Object):
    def __init__(self):
        super().__init__("images/roka.png")
        self.radius = MEDIUM_ROCK_RADIUS
        
    def advance(self):
        super().advance()
        self.angle += MEDIUM_ROCK_SPIN
        
    def break_apart(self, asteroids):
        small = SmallRock()
        small.center.x = self.center.x
        small.center.y = self.center.y
        small.velocity.dy = self.velocity.dy + 1.5
        small.velocity.dx = self.velocity.dx + 1.5
        
        small2 = SmallRock()
        small2.center.x = self.center.x
        small2.center.y = self.center.y
        small2.velocity.dy = self.velocity.dy + 1.5
        small2.velocity.dx = self.velocity.dx + 1.5
        
        asteroids.append(small)
        asteroids.append(small2)
        self.alive = False
        
class LargeRock(Asteroid):
    def __init__(self):
        super().__init__("images/roka.png")
        self.radius = BIG_ROCK_RADIUS
        self.center.x = random.randint(1,150)
        self.center.y = random.randint(1,150)
        self.direction = random.randint(1,150)
        self.speed = BIG_ROCK_SPEED
        self.velocity.dx = math.cos(math.radians(self.direction)) * self.speed
        self.velocity.dy = math.sin(math.radians(self.direction)) * self.speed
        
    def advance(self):
        super().advance()
        self.angle += BIG_ROCK_SPIN
        
    def break_apart(self, asteroids):
        med1 = MediumRock()
        med1.center.x = self.center.x
        med1.center.y = self.center.y
        med1.velocity.dy = self.velocity.dy + 2
        
        med2 = MediumRock()
        med2.center.x = self.center.x
        med2.center.y = self.center.y
        med2.velocity.dy = self.velocity.dy - 2
        
        small = SmallRock()
        small.center.x = self.center.x
        small.center.y = self.center.y
        small.velocity.dy = self.velocity.dy + 5
        
        asteroids.append(med1)
        asteroids.append(med2)
        asteroids.append(small)
        self.alive = False
        

class Game(arcade.Window):
    def __init__(self,width,height):
        super().__init__(width,height)
        
        arcade.set_background_color(arcade.color.SMOKY_BLACK)
        
        self.held_keys = set()
        
        self.asteroids = []
        for i in range(INITIAL_ROCK_COUNT):
            bigAst = LargeRock()
            self.asteroids.append(bigAst)
            
        self.ship = Ship()
        
        self.bullet = []
    
    def on_draw(self):
        arcade.start_render()
        
        for asteroid in self.asteroids:
            asteroid.draw()
            
        for bullet in self.bullet:
            bullet.draw()
            
        self.ship.draw()
        
    def remove_not_alive_object(self):
        for bullet in self.bullet:
            if not bullet.alive:
                self.bullet.remove(bullet)
                
        for asteroid in self.asteroids:
            if not asteroid.alive:
                self.asteroids.remove(asteroid)
                
    def check_collisions(self):
        for bullet in self.bullet:
            for asteroid in self.asteroids:
                    if((bullet.alive) and (asteroid.alive)):
                        distance_x = abs(asteroid.center.x - bullet.center.x)
                        distance_y = abs(asteroid.center.y - bullet.center.y)
                        max_dist = asteroid.radius + bullet.radius
                        if ((distance_x < max_dist) and (distance_y < max_dist)):
                            asteroid.break_apart(self.asteroids)
                            bullet.alive = False
                            asteroid.alive = False
            for asteroid in self.asteroids:
                if((self.ship.alive) and (asteroid.alive)):
                        distance_x = abs(asteroid.center.x - self.ship.center.x)
                        distance_y = abs(asteroid.center.y - self.ship.center.y)
                        max_dist = asteroid.radius + self.ship.radius
                        if ((distance_x < max_dist) and (distance_y < max_dist)):
                            self.ship.alive = False       
                
                           
        
    def update(self,delta_time):
        self.check_keys()
        for asteroid in self.asteroids:
            asteroid.advance()
            
        for bullet in self.bullet:
            bullet.advance()
            
        self.remove_not_alive_object()
        self.check_collisions()
            
        self.ship.advance()
        
    def check_keys(self):
        if arcade.key.LEFT in self.held_keys:
            self.ship.left()
        if arcade.key.RIGHT in self.held_keys:
            self.ship.right()
        if arcade.key.UP in self.held_keys:
            self.ship.thrust()
        if arcade.key.DOWN in self.held_keys:
            self.ship.neg_thrust()
        
    def on_key_press(self,key:int,modifiers:int):
        if self.ship.alive:
            self.held_keys.add(key)
            
            if key == arcade.key.SPACE:
                bullet = Bullet(self.ship.angle,self.ship.center.x, self.ship.center.y)
                self.bullet.append(bullet)
                bullet.fire()
            
    def on_key_release(self,key:int,modifiers:int):
        if key in self.held_keys:
            self.held_keys.remove(key)
    
window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()
    

    

