from gamemodel import *
from graphics import *

EXPLOSION_TIME = 1/2
FRAME_RATE = 50

class GameGraphics:
    def __init__(self, game):
        self.game = game

        # open the window
        self.win = GraphWin("Cannon game" , 640, 480, autoflush=False)
        self.win.setCoords(-110, -10, 110, 155)
        
        # draw the terrain
        line = Line(Point(-110,0), Point(110,0))
        line.draw(self.win)

        self.draw_cannons = [self.drawCanon(0), self.drawCanon(1)]
        self.draw_scores  = [self.drawScore(0), self.drawScore(1)]
        self.draw_projs   = [None, None]

    def drawCanon(self,playerNr):

        #Calls player number.
        player = self.game.getPlayers()[playerNr]

        #Creates both cubes, gives them a position, gives them a color.
        cannon = Rectangle(Point(player.position-self.game.cannonSize/2,0),Point(player.position+self.game.cannonSize/2,self.game.cannonSize))
        cannon.setFill(player.color)
        cannon.draw(self.win)
        return cannon

    def drawScore(self,playerNr):

        #Calls player number.
        player = self.game.getPlayers()[playerNr]

        #Draws two separate texts under each player.
        #The "-playerXpos/2" part means that i position the text below the cannon, and the distance down is half the size of the cannon.
        text = Text(Point(player.position,-self.game.cannonSize/2),"Score 0") 
        text.draw(self.win)
        return text

    def explode(self,playerNr):
        players = self.game.getPlayers()
        otherPlayer = players[1 - playerNr]
        color = self.game.getPlayers()[playerNr].color
        explosionSize = self.game.cannonSize
        explosion = None
        #Explosion animation
        while explosionSize < self.game.cannonSize*2:
            if explosion:
                explosion.undraw()
            explosion = Circle(Point(otherPlayer.position, self.game.cannonSize/2),explosionSize)
            explosion.setFill(color)
            explosion.draw(self.win)
            explosionSize += self.game.cannonSize / EXPLOSION_TIME / FRAME_RATE
            update(50)
        explosion.undraw()


    def fire(self, angle, vel):
        player = self.game.getCurrentPlayer()
        proj = player.fire(angle, vel)

        circle_X = proj.getX()
        circle_Y = proj.getY()

        # Removes the previous projectile if it existed
        # Each player can only have at most one projectile drawn at a time
        # Before drawing a new one, undraws the old one
        currentPlayerNr = self.game.getCurrentPlayerNumber()
        if self.draw_projs[currentPlayerNr]:
            self.draw_projs[currentPlayerNr].undraw()

        # Draws the projectile. The projectile's current position is the center of the circle. The radius comes from ball size and color is determined by the player color
        radius = self.game.getBallSize()
        circle = Circle(Point(circle_X, circle_Y), radius)
        circle.setFill(player.getColor())
        circle.draw(self.win)
        self.draw_projs[currentPlayerNr] = circle

        while proj.isMoving():
            proj.update(1/50)

            # move is a function in graphics. It moves an object dx units in x direction and dy units in y direction
            circle.move(proj.getX() - circle_X, proj.getY() - circle_Y)

            circle_X = proj.getX()
            circle_Y = proj.getY()

            update(50)

        return proj

    def updateScore(self,playerNr):
        # Removes the old score text
        self.draw_scores[playerNr].undraw()

        # The x position of the score matches the player's cannon x position, while the y position is set just below the cannon at half the cannon size
        player = self.game.getPlayers()[playerNr]
        x = player.getX()
        y = -self.game.getCannonSize() / 2
        # Creates a new Text object with the player's updated score and draws it on screen
        new_text = Text(Point(x, y), f"Score {player.getScore()}")
        new_text.draw(self.win)

        # Saves the text object so it can be updated next time
        self.draw_scores[playerNr] = new_text

    def play(self):
        while True:
            player = self.game.getCurrentPlayer()
            oldAngle,oldVel = player.getAim()
            wind = self.game.getCurrentWind()

            # InputDialog(self, angle, vel, wind) is a class in gamegraphics
            inp = InputDialog(oldAngle,oldVel,wind)
            # interact(self) is a function inside InputDialog. It runs a loop until the user presses either the quit or fire button
            if inp.interact() == "Fire!": 
                angle, vel = inp.getValues()
                inp.close()
            elif inp.interact() == "Quit":
                exit()
            
            player = self.game.getCurrentPlayer()
            other = self.game.getOtherPlayer()
            proj = self.fire(angle, vel)
            distance = other.projectileDistance(proj)

            if distance == 0.0:
                player.increaseScore()
                playerNr = self.game.getCurrentPlayerNumber()
                self.explode(playerNr)
                self.updateScore(playerNr)
                self.game.newRound()

            self.game.nextPlayer()


class InputDialog:
    def __init__ (self, angle, vel, wind):
        self.win = win = GraphWin("Fire", 200, 300)
        win.setCoords(0,4.5,4,.5)
        Text(Point(1,1), "Angle").draw(win)
        self.angle = Entry(Point(3,1), 5).draw(win)
        self.angle.setText(str(angle))
        
        Text(Point(1,2), "Velocity").draw(win)
        self.vel = Entry(Point(3,2), 5).draw(win)
        self.vel.setText(str(vel))
        
        Text(Point(1,3), "Wind").draw(win)
        self.height = Text(Point(3,3), 5).draw(win)
        self.height.setText("{0:.2f}".format(wind))
        
        self.fire = Button(win, Point(1,4), 1.25, .5, "Fire!")
        self.fire.activate()
        self.quit = Button(win, Point(3,4), 1.25, .5, "Quit")
        self.quit.activate()

    def interact(self):
        while True:
            pt = self.win.getMouse()
            if self.quit.clicked(pt):
                return "Quit"
            if self.fire.clicked(pt):
                return "Fire!"

    def getValues(self):
        a = float(self.angle.getText())
        v = float(self.vel.getText())
        return a,v

    def close(self):
        self.win.close()


class Button:

    def __init__(self, win, center, width, height, label):

        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1,p2)
        self.rect.setFill('lightgray')
        self.rect.draw(win)
        self.label = Text(center, label)
        self.label.draw(win)
        self.deactivate()

    def clicked(self, p):
        return self.active and \
               self.xmin <= p.getX() <= self.xmax and \
               self.ymin <= p.getY() <= self.ymax

    def getLabel(self):
        return self.label.getText()

    def activate(self):
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = 1

    def deactivate(self):
        self.label.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = 0


GameGraphics(Game(11,3)).play()