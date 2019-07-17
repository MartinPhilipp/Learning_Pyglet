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
        super(PhysicalObject, self).__init__(image,*args, **kwargs)

        # Velocity
        self.velocity_x, self.velocity_y = 0.0, 0.0

        # Flags to toggle collision with bullets
        self.reacts_to_bullets = True
        self.is_bullet = False

        # Flag to remove this object from the game_object list
        self.dead = False

        # List of new objects to go in the game_objects list
        self.new_objects = []

        # Tell the game handler about any event handlers
        # Only applies to things with keyboard/mouse input
        self.event_handlers = []
        #print("init aufgerufen", self)
    def update(self, dt):
        """This method should be called every frame."""
        
        # Update position according to velocity and time
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        #print(self,self.x,self.y)
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

        # Ignore bullet collisions if we're supposed to
        if not self.reacts_to_bullets and other_object.is_bullet:
            return False
        if self.is_bullet and not other_object.reacts_to_bullets:
            return False

        # Calculate distance between object centers that would be a collision,
        # assuming square resources
        collision_distance = self.image.width * 0.5 * self.scale \
                             + other_object.image.width * 0.5 * other_object.scale

        # Get distance using position tuples
        actual_distance = util.distance(self.position, other_object.position)

        return (actual_distance <= collision_distance)

    def handle_collision_with(self, other_object):
        if other_object.__class__ is not self.__class__:
            self.dead = True



class Asteroid(PhysicalObject):
    """An asteroid that divides a little before it dies"""

    def __init__(self, image, *args, **kwargs):
        super(Asteroid, self).__init__(image=image, *args, **kwargs)
        self.velocity_x = random.random() * 40
        self.velocity_y = random.random() * 40

        # Slowly rotate the asteroid as it moves
        self.rotate_speed = random.random() * 100.0 - 50.0

    def update(self, dt):
        #("asteroidupdate",self,dt)
        super(Asteroid, self).update(dt)
        self.rotation += self.rotate_speed * dt

    def handle_collision_with(self, other_object):
        super(Asteroid, self).handle_collision_with(other_object)

        # Superclass handles deadness already
        if self.dead and self.scale > 0.25:
            num_asteroids = random.randint(2, 3)
            for i in range(num_asteroids):
                new_asteroid = Asteroid(x=self.x, y=self.y, batch=self.batch)
                new_asteroid.rotation = random.randint(0, 360)
                new_asteroid.velocity_x = random.random() * 70 + self.velocity_x
                new_asteroid.velocity_y = random.random() * 70 + self.velocity_y
                new_asteroid.scale = self.scale * 0.5
                self.new_objects.append(new_asteroid)
                
class Player(PhysicalObject):
    """Physical object that responds to user input"""

    def __init__(self, image, *args, **kwargs):
        super(Player, self).__init__(image=image, *args, **kwargs)

        # Set some easy-to-tweak constants
        self.thrust = 300.0
        self.rotate_speed = 200.0

        self.keys = dict(left=False, right=False, up=False)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.keys['up'] = True
        elif symbol == pyglet.window.key.LEFT:
            self.keys['left'] = True
        elif symbol == pyglet.window.key.RIGHT:
            self.keys['right'] = True

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.keys['up'] = False
        elif symbol == pyglet.window.key.LEFT:
            self.keys['left'] = False
        elif symbol == pyglet.window.key.RIGHT:
            self.keys['right'] = False

    def update(self, dt):
        # Do all the normal physics stuff
        super(Player, self).update(dt)

        if self.keys['left']:
            self.rotation -= self.rotate_speed * dt
        if self.keys['right']:
            self.rotation += self.rotate_speed * dt

        if self.keys['up']:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x += force_x
            self.velocity_y += force_y


class Viewer():
    
    width = 0
    height = 0
    game_objects = []
    
    def __init__(self,width=800,height=600):
        Viewer.width = width
        Viewer.height  = height
        
        # Set up a window
        self.game_window = pyglet.window.Window(self.width, self.height)
        self.on_draw = self.game_window.event(self.on_draw)
        
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
        
        # Set up the two top labels
        self.score_label = pyglet.text.Label(text="Score: 0", x=10, y=575)
        self.level_label = pyglet.text.Label(text="Version 2: Basic Motion",
                                x=400, y=575, anchor_x='center')

        # Initialize the player sprite
        self.player_ship = Player(image=self.player_image, x=400, y=300)
        Viewer.game_objects.append(self.player_ship)

        # Make three asteroids so we have something to shoot at 
        self.asteroids = self.load_asteroids(5, self.player_ship.position)
        # Store all objects that update each frame in a list
        Viewer.game_objects = [self.player_ship] + self.asteroids

        # Make three sprites to represent remaining lives
        self.player_lives = self.player_lives(2)
        
        #pyglet.clock.schedule_interval(self, 1 / 120.0)
        # Tell the main window that the player object responds to events
        self.game_window.push_handlers(self.player_ship)
        # Tell pyglet to do its thing
        pyglet.app.run()
        
    def player_lives(self, num_icons):
        """Generate sprites for player life icons"""
        player_lives = []
        for i in range(num_icons):
            new_sprite = pyglet.sprite.Sprite(img=self.player_image,x=785 - i * 30, y=585,)
            new_sprite.scale = 0.5
            player_lives.append(new_sprite)
            print("player_lives!")
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
            #new_asteroid = pyglet.sprite.Sprite(img=self.asteroid_image, x=asteroid_x, y=asteroid_y)
            new_asteroid = Asteroid(image=self.asteroid_image,x=asteroid_x, y=asteroid_y,)# batch=batch)
            new_asteroid.rotation = random.randint(0, 360)
            #new_asteroid.velocity_x, new_asteroid.velocity_y = random.random() * 40, random.random() * 40
            asteroids.append(new_asteroid)
        return asteroids

    def on_draw(self):
        self.game_window.clear()
        for symbol in self.player_lives:
            symbol.draw()
        self.player_ship.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        self.level_label.draw()
        self.score_label.draw()

def update(dt):
    #print("Update!",dt)
    for obj in Viewer.game_objects:
        #print(obj)
        obj.update(dt)   
    
if __name__ == "__main__":
    # Update the game 120 times per second
    pyglet.clock.schedule_interval(update, 1 / 120.0)
    Viewer(800,600)
  
