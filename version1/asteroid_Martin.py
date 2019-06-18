import pyglet
import random
import math
#from game import load, resources


def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)




def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

class Viewer():
    
    width = 0
    height = 0
    
    def __init__(self,width=800,height=600):
        Viewer.width = width
        Viewer.height  = height  # = self.width, self.height 
        
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
        self.level_label = pyglet.text.Label(text="Version 1: Static Graphics",
                                x=400, y=575, anchor_x='center')

        # Initialize the player sprite
        self.player_ship = pyglet.sprite.Sprite(img=self.player_image, x=400, y=300)

        # Make three asteroids so we have something to shoot at 
        self.asteroids = self.load_asteroids(3, self.player_ship.position)

        pyglet.app.run()

    def load_asteroids(self, num_asteroids, player_position):
        """Generate asteroid objects with random positions and velocities, 
        not close to the player"""
        asteroids = []
        for i in range(num_asteroids):
            asteroid_x, asteroid_y = player_position
            while distance((asteroid_x, asteroid_y), player_position) < 100:
                asteroid_x = random.randint(0, 800)
                asteroid_y = random.randint(0, 600)
            new_asteroid = pyglet.sprite.Sprite(img=self.asteroid_image,
                                                x=asteroid_x, y=asteroid_y)
            new_asteroid.rotation = random.randint(0, 360)
            asteroids.append(new_asteroid)
        return asteroids


    #@game_window.event
    def on_draw(self):
        self.game_window.clear()

        self.player_ship.draw()
        for asteroid in self.asteroids:
            asteroid.draw()

        self.level_label.draw()
        self.score_label.draw()


if __name__ == "__main__":
    # Tell pyglet to do its thing
    Viewer(800,600)
    #
