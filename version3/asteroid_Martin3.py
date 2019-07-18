import pyglet
import random
import math
#import thread


def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

            
class PhysicalObject(pyglet.sprite.Sprite):
    """A sprite with physical properties such as velocity"""

    def __init__(self, image, *args, **kwargs):
        super(PhysicalObject, self).__init__(image, *args, **kwargs)

        # In addition to position, we have velocity
        self.velocity_x, self.velocity_y = 0.0, 0.0

        # And a flag to remove this object from the game_object list
        self.dead = False

    def update(self, dt):
        """This method should be called every frame."""

        # Update position according to velocity and time
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Wrap around the screen if necessary
        self.check_bounds()

    def check_bounds(self):
        """Use the classic Asteroids screen wrapping behavior"""
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = 800 + self.image.width / 2
        max_y = 600 + self.image.height / 2
        if self.x < min_x:
            self.x = max_x
        if self.y < min_y:
            self.y = max_y
        if self.x > max_x:
            self.x = min_x
        if self.y > max_y:
            self.y = min_y

    def collides_with(self, other_object):
        """Determine if this object collides with another"""

        # Calculate distance between object centers that would be a collision,
        # assuming square resources
        collision_distance = self.image.width / 2 + other_object.image.width / 2

        # Get distance using position tuples
        actual_distance = distance(self.position, other_object.position)

        return (actual_distance <= collision_distance)

    def handle_collision_with(self, other_object):
        self.dead = True




class Asteroid(PhysicalObject):
    """An asteroid that divides a little before it dies"""

    def __init__(self, image, *args, **kwargs):
        super(Asteroid, self).__init__(image=image, *args, **kwargs)
        self.velocity_x = random.random() * 40
        self.velocity_y = random.random() * 40
        self.collgroup1 = True
        self.collgroup2 = False

        # Slowly rotate the asteroid as it moves
        self.rotate_speed = random.random() * 100.0 - 50.0

    def update(self, dt):
        #("asteroidupdate",self,dt)
        super(Asteroid, self).update(dt)
        self.rotation += self.rotate_speed * dt

class Player(PhysicalObject):
    """Physical object that responds to user input"""

    def __init__(self, image, *args, **kwargs):
        super(Player, self).__init__(image=image, *args, **kwargs)
        self.collgroup1 = False
        self.collgroup2 = True

        
        self.engine_visible = False

        # Set some easy-to-tweak constants
        self.thrust = 300.0
        self.rotate_speed = 200.0

        # Let pyglet handle keyboard events for us
        self.key_handler = pyglet.window.key.KeyStateHandler()

    def update(self, dt):
        # Do all the normal physics stuff
        super(Player, self).update(dt)

        if self.key_handler[pyglet.window.key.LEFT]:
            self.rotation -= self.rotate_speed * dt
        if self.key_handler[pyglet.window.key.RIGHT]:
            self.rotation += self.rotate_speed * dt

        if self.key_handler[pyglet.window.key.UP]:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x += force_x
            self.velocity_y += force_y

            ## If thrusting, update the engine sprite
            #self.engine_sprite.rotation = self.rotation
            #self.engine_sprite.x = self.x
            #self.engine_sprite.y = self.y
            self.engine_visible = True
        else:
            # Otherwise, hide it
            self.engine_visible = False

    def delete(self):
        # We have a child sprite which must be deleted when this object
        # is deleted from batches, etc.
        #self.engine_sprite.delete()
        super(Player, self).delete()
        
class Engine(pyglet.sprite.Sprite):
    
    def __init__(self, image, boss, *args, **kwargs):
        super(Engine, self).__init__(img=image, *args, **kwargs)
        self.boss = boss
        self.collgroup1 = False
        self.collgroup2 = False
        self.dead = False
        
    def update(self, dt):
        super(Engine, self).update(dt)
        if self.boss.engine_visible:
            self.visible = True
        else:
            self.visible = False
        self.rotation = self.boss.rotation
        self.x = self.boss.x
        self.y = self.boss.y
        if self.boss.dead:
            self.dead = True
            

class Viewer():
    
    width = 0
    height = 0
    game_objects = []
    #collision_objects[]
    
    def __init__(self,width=800,height=600):
        Viewer.width = width
        Viewer.height  = height
        self.load_resources()
        # Set up a window
        self.game_window = pyglet.window.Window(self.width, self.height)
        self.on_draw = self.game_window.event(self.on_draw)
        
        
        
        # Set up the two top labels
        self.score_label = pyglet.text.Label(text="Score: 0", x=10, y=575)
        self.level_label = pyglet.text.Label(text="Version 3: Basic Collisions",
                                x=400, y=575, anchor_x='center')

        # Initialize the player sprite
        self.player_ship = Player(image=self.player_image, x=400, y=300)
        Viewer.game_objects.append(self.player_ship)

        # Make three asteroids so we have something to shoot at 
        self.asteroids = self.load_asteroids(1, self.player_ship.position)
        Viewer.game_objects.extend(self.asteroids)

        # Make three sprites to represent remaining lives
        self.player_lives = self.player_lives(2)
        
        # Create a child sprite to show when the ship is thrusting
        self.engine_sprite = Engine(image=self.engine_image, boss=self.player_ship) #*args, **kwargs)
        Viewer.game_objects.append(self.engine_sprite)
        
        # Tell the main window that the player object responds to events
        self.game_window.push_handlers(self.player_ship.key_handler)
        # Tell pyglet to do its thing
        pyglet.app.run()
        
    def load_resources(self):
        # Tell pyglet where to find the resources
        pyglet.resource.path = ['data']
        pyglet.resource.reindex()
        # Load the three main resources and get them to draw centered
        self.player_image = pyglet.resource.image("player.png")
        center_image(self.player_image)

        self.bullet_image = pyglet.resource.image("bullet.png")
        center_image(self.bullet_image)

        self.asteroid_image = pyglet.resource.image("asteroid.png")
        center_image(self.asteroid_image)
        
        # The engine flame should not be centered on the ship. Rather, it should be shown 
        # behind it. To achieve this effect, we just set the anchor point outside the
        # image bounds.
        self.engine_image = pyglet.resource.image("engine_flame.png")
        self.engine_image.anchor_x = self.engine_image.width * 1.5
        self.engine_image.anchor_y = self.engine_image.height / 2
    
    def player_lives(self, num_icons):
        """Generate sprites for player life icons"""
        player_lives = []
        for i in range(num_icons):
            new_sprite = pyglet.sprite.Sprite(img=self.player_image,x=785 - i * 30, y=585,)
            new_sprite.scale = 0.5
            player_lives.append(new_sprite)
        return player_lives

    def load_asteroids(self, num_asteroids, player_position):
        """Generate asteroid objects with random positions and velocities, 
        not close to the player"""
        asteroids = []
        for i in range(num_asteroids):
            asteroid_x, asteroid_y = player_position
            while distance((asteroid_x, asteroid_y), player_position) < 100:
                asteroid_x = random.randint(0, 800)
                asteroid_y = random.randint(0, 600)
            new_asteroid = Asteroid(image=self.asteroid_image,x=asteroid_x, y=asteroid_y,)# batch=batch)
            new_asteroid.rotation = random.randint(0, 360)
            asteroids.append(new_asteroid)
        return asteroids
        
    def on_draw(self):
        self.game_window.clear()
        for symbol in self.player_lives:
            symbol.draw()
        if not self.engine_sprite.dead:
            self.engine_sprite.draw()
        if not self.player_ship.dead:
            self.player_ship.draw()
        for asteroid in [a for a in self.asteroids if not a.dead]:
            asteroid.draw()
        self.level_label.draw()
        self.score_label.draw()

def update(dt):     
    for obj in Viewer.game_objects:
        obj.update(dt)
    #Get rid of dead objects
    for o in [obj for obj in Viewer.game_objects if obj.dead]:
        #Remove the object from any batches it is a member of
        o.delete()
        # Remove the object from our list
        Viewer.game_objects.remove(o)
    # To avoid handling collisions twice, we employ nested loops of ranges.
    # This method also avoids the problem of colliding an object with itself.
    for i in [x for x in Viewer.game_objects if x.collgroup1 is True and not x.dead]:
        for j in [y for y in Viewer.game_objects if y.collgroup2 is True and not y.dead]:
                if i.collides_with(j):
                    i.handle_collision_with(j)
                    j.handle_collision_with(i)
    
    
if __name__ == "__main__":
    # Update the game 120 times per second
    pyglet.clock.schedule_interval(update, 1 / 120.0)
    Viewer(800,600)
