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

        # Ignore bullet collisions if we're supposed to
        if not self.reacts_to_bullets and other_object.is_bullet:
            return False
        if self.is_bullet and not other_object.reacts_to_bullets:
            return False

        # Calculate distance between object centers that would be a collision,
        # assuming square resources
        collision_distance = self.image.width / 2 + other_object.image.width / 2

        # Get distance using position tuples
        actual_distance = distance(self.position, other_object.position)

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
        self.collgroup1 = True
        self.collgroup2 = False

        # Slowly rotate the asteroid as it moves
        self.rotate_speed = random.random() * 100.0 - 50.0

    def update(self, dt):
        super(Asteroid, self).update(dt)
        self.rotation += self.rotate_speed * dt

    def handle_collision_with(self, other_object):
        super(Asteroid, self).handle_collision_with(other_object)
        Viewer.score += 1

        # Superclass handles deadness already
        if self.dead and self.scale > 0.25:
            num_asteroids = random.randint(2, 3)
            for i in range(num_asteroids):
                new_asteroid = Asteroid(image=self.image, x=self.x, y=self.y)#, batch=self.batch)
                new_asteroid.rotation = random.randint(0, 360)
                new_asteroid.velocity_x = random.random() * 70 + self.velocity_x
                new_asteroid.velocity_y = random.random() * 70 + self.velocity_y
                new_asteroid.scale = self.scale * 0.5
                Viewer.game_objects.append(new_asteroid)
            
            
    #def delete(self):
        #super(Asteroid, self).delete()
        #self.delete()
        #Viewer.player_dead = True

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
        self.bullet_speed = 700.0

        # Player should not collide with own bullets
        self.reacts_to_bullets = False

        # Tell the game handler about any event handlers
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.event_handlers = [self, self.key_handler]

    def update(self, dt):
        # Do all the normal physics stuff
        super(Player, self).update(dt)

        if self.key_handler[pyglet.window.key.LEFT]:
            self.rotation -= self.rotate_speed * dt
        if self.key_handler[pyglet.window.key.RIGHT]:
            self.rotation += self.rotate_speed * dt

        if self.key_handler[pyglet.window.key.UP]:
            # Note: pyglet's rotation attributes are in "negative degrees"
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x += force_x
            self.velocity_y += force_y
            
            self.engine_visible = True
        else:
            # Otherwise, hide it
            self.engine_visible = False
            
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.fire()

    def fire(self):
        # Note: pyglet's rotation attributes are in "negative degrees"
        angle_radians = -math.radians(self.rotation)

        # Create a new bullet just in front of the player
        ship_radius = self.image.width / 2
        bullet_x = self.x + math.cos(angle_radians) * ship_radius
        bullet_y = self.y + math.sin(angle_radians) * ship_radius
        new_bullet = Bullet(image=Viewer.bullet_image, x=bullet_x, y=bullet_y,)# batch=self.batch)

        # Give it some speed
        bullet_vx = self.velocity_x + math.cos(angle_radians) * self.bullet_speed
        bullet_vy = self.velocity_y + math.sin(angle_radians) * self.bullet_speed
        new_bullet.velocity_x, new_bullet.velocity_y = bullet_vx, bullet_vy

        # Add it to the list of objects to be added to the game_objects list
        Viewer.game_objects.append(new_bullet)

        # Play the bullet sound
        Viewer.bullet_sound.play()

    def delete(self):
        super(Player, self).delete()
        Viewer.player_dead = True
        
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
            
    #def delete(self):
    #    self.delete()

class Bullet(PhysicalObject):
    """Bullets fired by the player"""

    def __init__(self, image, *args, **kwargs):
        super(Bullet, self).__init__(image=image, *args, **kwargs)
        self.collgroup1 = False
        self.collgroup2 = True

        # Bullets shouldn't stick around forever
        pyglet.clock.schedule_once(self.die, 0.5)

        # Flag as a bullet
        self.is_bullet = True

    def die(self, dt):
        self.dead = True

class Viewer():
    
    width = 0
    height = 0
    game_objects = []
    #collision_objects[]
    score = 0
    player_dead = False
    num_asteroids = 3
    player_live_numbers = 3
    #victory = False
    reset = False
    
    def __init__(self,width=800,height=600):
        Viewer.width = width
        Viewer.height  = height
        self.load_resources()
        # Set up a window
        self.game_window = pyglet.window.Window(self.width, self.height)
        self.on_draw = self.game_window.event(self.on_draw)
        
        # Set up the two top labels
        Viewer.score_label = pyglet.text.Label(text="Score: 0", x=10, y=575)
        self.level_label = pyglet.text.Label(text="Version 5: It's a Game!",
                                x=400, y=575, anchor_x='center')
        # Set up the game over label offscreen
        Viewer.game_over_label = pyglet.text.Label(text="GAME OVER",
                                    x=400, y=-300, anchor_x='center', font_size=48)
        
        self.counter = pyglet.clock.ClockDisplay()
        
        self.prepare_sprites()
        
        # Add any specified event handlers to the event handler stack
        #for obj in self.game_objects:
        #    for handler in obj.event_handlers:
        #        self.game_window.push_handlers(handler)
        # Tell pyglet to do its thing
        pyglet.app.run()
        
    def prepare_sprites(self):
        # Initialize the player sprite
        self.player_ship = Player(image=self.player_image, x=400, y=300)
        Viewer.game_objects.append(self.player_ship)
        # Tell the main window that the player object responds to events
        self.game_window.push_handlers(self.player_ship.key_handler)
        self.game_window.push_handlers(self.player_ship)

        # Make three asteroids so we have something to shoot at 
        self.asteroids = self.load_asteroids(self.num_asteroids, self.player_ship.position)
        Viewer.game_objects.extend(self.asteroids)
        
        # Make two sprites to represent remaining lives
        self.player_lives = self.player_live()
        
        # Create a child sprite to show when the ship is thrusting
        self.engine_sprite = Engine(image=self.engine_image, boss=self.player_ship) #*args, **kwargs)
        Viewer.game_objects.append(self.engine_sprite)
        
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
        
        Viewer.bullet_image = pyglet.resource.image("bullet.png")
        center_image(self.bullet_image)
        
        # Load the bullet sound _without_ streaming so we can play it more than once at a time
        Viewer.bullet_sound = pyglet.resource.media("bullet.wav", streaming=False)
        
        # The engine flame should not be centered on the ship. Rather, it should be shown 
        # behind it. To achieve this effect, we just set the anchor point outside the
        # image bounds.
        self.engine_image = pyglet.resource.image("engine_flame.png")
        self.engine_image.anchor_x = self.engine_image.width * 1.5
        self.engine_image.anchor_y = self.engine_image.height / 2
    
    def player_live(self):
        """Generate sprites for player life icons"""
        player_lives = []
        for i in range(Viewer.player_live_numbers):
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
        
    def reset_level(self):

        # Clear the event stack of any remaining handlers from other levels
        #while event_stack_size > 0:
        #    game_window.pop_handlers()
        #    event_stack_size -= 1

        for obj in Viewer.game_objects:
            #Remove the object from any batches it is a member of
            obj.delete()
            # Remove the object from our list
        Viewer.game_objects.clear()
        print(len(Viewer.game_objects),Viewer.game_objects)
        Viewer.player_dead = False

        # Initialize the player sprite
        self.player_ship = Player(image=self.player_image, x=400, y=300)
        Viewer.game_objects.append(self.player_ship)
        # Tell the main window that the player object responds to events
        self.game_window.push_handlers(self.player_ship.key_handler)
        self.game_window.push_handlers(self.player_ship)
        

        # Make three asteroids so we have something to shoot at 
        self.asteroids = self.load_asteroids(self.num_asteroids, self.player_ship.position)
        Viewer.game_objects.extend(self.asteroids)

        # Make two sprites to represent remaining lives
        self.player_lives = self.player_live()
        
        # Create a child sprite to show when the ship is thrusting
        self.engine_sprite = Engine(image=self.engine_image, boss=self.player_ship) #*args, **kwargs)
        Viewer.game_objects.append(self.engine_sprite)
        # Initialize the player sprite
        #self.player_ship = Player(x=400, y=300, batch=main_batch)

        # Make three sprites to represent remaining lives
        #player_lives = load.player_lives(num_lives, main_batch)

        # Make some asteroids so we have something to shoot at 
        #asteroids = load.asteroids(num_asteroids, player_ship.position, main_batch)

        # Store all objects that update each frame in a list
        #game_objects = [player_ship] + asteroids

        # Add any specified event handlers to the event handler stack
        #for obj in game_objects:
        #    for handler in obj.event_handlers:
        #        game_window.push_handlers(handler)
        #        event_stack_size += 1
        
    def on_draw(self):
        self.game_window.clear()
        for symbol in self.player_lives:
            symbol.draw()
        for obj in [x for x in Viewer.game_objects if not x.dead]:
            obj.draw()
        if Viewer.reset:
            Viewer.reset = False
            self.reset_level()
        self.level_label.draw()
        self.score_label.draw()
        self.game_over_label.draw()
        self.counter.draw()

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
                    Viewer.score_label.text = "Score: " + str(Viewer.score)
    #print(Viewer.game_objects)
    # Check for win/lose conditions
    if Viewer.player_dead:
        # We can just use the length of the player_lives list as the number of lives
        if Viewer.player_live_numbers > 0:
            Viewer.player_live_numbers -= 1
            Viewer.reset = True
        else:
            Viewer.game_over_label.y = 300
    
    elif len(Viewer.game_objects) == 2:
        Viewer.num_asteroids += 1
        #Viewer.player_ship.delete()
        Viewer.score += 10
        Viewer.reset = True
    
    
if __name__ == "__main__":
    # Update the game 120 times per second
    pyglet.clock.schedule_interval(update, 1 / 120.0)
    Viewer(800,600)
