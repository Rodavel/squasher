import pygame, sys
import random
from pygame.locals import *

WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)
GOLD = (255, 255, 0)

WINDOWWIDTH = 640
WINDOWHEIGHT = 480 
WIDTH = 20
HEIGHT = 20
SCORENEWTAR = 1

SCORECOORDS = (500, 464)
GOSCORECOORDS = (320, 50)
SCORESIZE = 32
SCOREFONT = 'freesansbold.ttf'
SCORECOLOR = RED

TIMECOORDS = (320, 464)
TIMESIZE = 32
TIMEFONT = 'freesansbold.ttf'
TIMECOLOR = GREEN

LOWERNUM = 2  #For random speed generation
HIGHERNUM = 5 #For random speed generation
TARGETNUM = 5
TRYFIXCOLLISION = 10
TRYFIXWALLCOLLISION = 10
SUBSTRACTRESISTANCE = 10
GAMEOVER = True

clock = pygame.time.Clock()


def main():
	global DISPLAYSURF
	
	squasher = GameState()
	squasher.initTargets()
	

	
	
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),0,32)
	pygame.display.set_caption ('Squasher: The squash begins!')
	DISPLAYSURF.fill(WHITE)
	#pygame.event.set_grab(1)
	
	
	while True:
		DISPLAYSURF.fill(WHITE)
		
		squasher.scoreDisplay()
		squasher.timeDisplay()
		
		squasher.checkCollisions()
		squasher.drawTargets()
		squasher.handleEvents()
	
				
		if squasher.targetPointed():
				squasher.gameOver(GAMEOVER)
		if squasher.mousePress:
			if squasher.blueTarget.locked(squasher.mousex, squasher.mousey):
				squasher.blueTarget.newCoord()
				squasher.score += 1
				squasher.newTargetScore += 1
				squasher.disappear = 0
			squasher.mousePress = False
		
		if squasher.newTargetScore == SCORENEWTAR:
			squasher.addTargets(1)
			squasher.newTargetScore = 0
			
		if squasher.disappear >= 2500:
			squasher.blueTarget.newCoord()
			squasher.disappear = 0
			squasher.blueTarget.addColor(BLUE)
		
		if squasher.milliseconds > (100 + squasher.count):
			squasher.disappear += 100
			squasher.count += 100
			colorChange = int (squasher.disappear/2500.0*255.0)
			squasher.blueTarget.addColor((colorChange,colorChange,255))
					
				
		if squasher.milliseconds > 1000:
			squasher.count = 0
			squasher.seconds += 1
			squasher.milliseconds -= 1000
		if squasher.seconds > 59:
			squasher.minutes += 1
			squasher.seconds = 0
			
		pygame.display.update()
		squasher.milliseconds += clock.tick_busy_loop(60)
		

class GameState:
	def __init__(self):
		self.score = 0
		self.seconds = 0
		self.milliseconds = 0
		self.minutes = 0
		self.mousex = 0
		self.mousey = 0
		self.disappear = 0
		self.count = 0
		self.newTargetScore = 0
		self.mousePress = False
		self.gameOverScore = 0
		
		self.scoreText = TextScreen(SCORECOORDS, SCOREFONT, SCORESIZE, SCORECOLOR)
		self.timeText = TextScreen(TIMECOORDS, TIMEFONT, TIMESIZE, TIMECOLOR)
		self.gameOverScoreText = TextScreen(GOSCORECOORDS, SCOREFONT, SCORESIZE, SCORECOLOR)
		
		self.blueTarget = Target(0, 0, WIDTH, HEIGHT)
		self.redTargets = []
		
		return
		
	def restartGame(self):
		self.score = 0
		self.seconds = 0
		self.milliseconds = 0
		self.minutes = 0
		self.mousex = 0
		self.mousey = 0
		self.disappear = 0
		self.count = 0
		self.newTargetScore = 0
		self.mousepress = False
		self.redTargets = []
		self.addTargets(TARGETNUM)
		return		
		
	def addTargets(self, numTargets):
		for x in range(numTargets):	
			target = Target(0,0, WIDTH, HEIGHT)
			while(self.targetPointed(False, target)): #Checks that target is not build on top of pointer
				target.newCoord()
			for gameTarget in self.redTargets:        #Checks that target it not build on top of another target
				targetCollision = target.getRect().colliderect(gameTarget.getRect())
				while targetCollision:
					target.newCoord()
					targetCollision = target.getRect().colliderect(gameTarget.getRect())
			#target.addColor((random.randint(0, 255), 0, 0)) #Random Red
			#target.addColor(RED)
			self.redTargets.append(target)
		for targets in self.redTargets:
			targets.inputMovement(randomInt(LOWERNUM, HIGHERNUM), randomInt(LOWERNUM, HIGHERNUM))
			targets.colorByMovement()	
		return
		
	def initTargets(self):
		self.blueTarget.newCoord()
		self.blueTarget.addColor(BLUE)
		self.addTargets(TARGETNUM)
		return
		
	def checkCollisions(self):
		tries = 0
		xpriority = False
		ypriority = False
		for target in self.redTargets:
			target.move()
			target.avoidWall()
		for x in range(len(self.redTargets)):
			for y in range(x + 1, len(self.redTargets)):
				targetCollision = self.redTargets[x].getRect().colliderect(self.redTargets[y].getRect())
				if targetCollision:
					if self.redTargets[y].resistance >= self.redTargets[x].resistance: 
						self.redTargets[x].changeMovement(True, True, False)
						self.redTargets[x].resistance = 255
						self.redTargets[y].resistance = 0
						ypriority = True
					elif self.redTargets[y].resistance < self.redTargets[x].resistance: 
						self.redTargets[y].changeMovement(True, True, False)
						self.redTargets[y].resistance = 255
						self.redTargets[x].resistance = 0
						xpriority = True
					while targetCollision:
						if xpriority:
							self.redTargets[y].move()
						if ypriority:
							self.redTargets[x].move()
						#self.redTargets[y].move()
						tries +=1
						xpriority = False
						ypriority = False
						if tries < TRYFIXCOLLISION:
							targetCollision = self.redTargets[x].getRect().colliderect(self.redTargets[y].getRect())
						else:
							tries = 0
							targetCollision = False
					#self.redTargets[x].randomColors()
			self.redTargets[x].resetOnce()
			self.redTargets[x].resetWallHit()
	def drawTargets(self):
		self.blueTarget.draw()
		for target in self.redTargets:
			target.draw()
		return
		
	def handleEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
			elif event.type == MOUSEMOTION:
				self.mousex, self.mousey = event.pos
			elif event.type == MOUSEBUTTONDOWN:
				self.mousex, self.mousey = event.pos
				self.mousePress = True
		return
		
	def scoreDisplay(self):
		self.scoreText.display('Score: ' + str (self.score))
		return
		
	def gameOverScoreDisplay(self):
		self.gameOverScoreText.display('Score: ' + str (self.score))
		return
		
	def timeDisplay(self):
		self.timeText.display(str (self.minutes) + ' : ' + str (self.seconds) )
		return
	
	def targetPointed(self, targets = True, targetCheck = None):
		if targets:
			for target in self.redTargets:
				if target.locked(self.mousex, self.mousey):
					return True
		else:
			if targetCheck.locked(self.mousex, self.mousey):
				return True
		return False
		
	def gameOver(self, enabled = True):
		if enabled:
			over = True
			DISPLAYSURF.fill(WHITE)
			gameOverText = TextScreen( (WINDOWWIDTH/2, WINDOWHEIGHT/2), SCOREFONT, 64, BLACK)
			retryText = TextScreen(SCORECOORDS, SCOREFONT, 32, BLACK) 
			gameOverText.display("Game Over")
			retryText.display("Press r to retry")
			self.gameOverScoreDisplay()
			while over:
				for event in pygame.event.get():
					if event.type == QUIT:
						pygame.quit()
						sys.exit()
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							pygame.quit()
							sys.exit()
						if event.key == K_r:
							over = False
							#print "It is beginning again!"
				pygame.display.update()
				self.milliseconds += clock.tick_busy_loop(60)
				self.milliseconds = 0
			self.restartGame()
		return
			
class Target:
	def __init__(self, xcoord, ycoord, width, height):
		self.x = xcoord
		self.y = ycoord
		self.w = width
		self.h = height
		self.c = None
		self.invertColors = False
		self.moveNotSet = True
		self.colorOnce = True
		self.greenMax = float (random.randint(0, 200))
		self.blueMax = float (random.randint(0, 200))
		self.resistance = 0
		self.onlyOnce = True
		self.resistantTimes = 0
		self.deltaX = 0
		self.deltaY = 0
		self.wallX = False
		self.wallY = False
	
	def colorByMovement(self):
		if self.colorOnce:
			lowerSpeed = float (LOWERNUM)
			higherSpeed = float (HIGHERNUM)
			redColorVariation = int ((float (self.deltaX) + self.deltaY)/(2.0 * higherSpeed)*255)
			#print redColorVariation
			self.c = (redColorVariation, 0, 0)
		self.colorOnce = False
		return
	
	def randomColors(self):
		red = random.randint(0,255)
		self.greenMax = float (random.randint(0, 200))
		self.blueMax = float (random.randint(0, 200))
		self.c = (red, int (self.greenMax), int (self.blueMax))
		return

	def getRect(self):
		return pygame.Rect(self.x, self.y, self.w, self.h)
	
	def properties(self):
		return (self.x, self.y, self.w, self.h)
	
	def addColor(self, color):
		self.c = color
		return
		
	def colorProp(self):
		return self.c
		
	def height(self):
		return self.h
		
	def locked(self, xcoord, ycoord):
		targetBox = pygame.Rect(self.x, self.y, self.w, self.h)
		return targetBox.collidepoint(xcoord,ycoord)
		
	def changeColor(self, color):
		self.c = color
		return
		
	def newCoord(self):
		newXcoord = int (random.random()*(WINDOWWIDTH - self.w))
		newYcoord = int (random.random()*(WINDOWHEIGHT - self.h - SCORESIZE))
		self.x = newXcoord
		self.y = newYcoord
		return
		
	def draw(self):
		pygame.draw.rect(DISPLAYSURF, self.c, self.properties())
	
	def inputMovement(self, deltaX, deltaY):
		if self.moveNotSet:
			self.deltaX = deltaX
			self.deltaY = deltaY
		self.moveNotSet = False
		return
	
	def changeMovement(self, changeX, changeY, wall = True):
		if wall:
			if changeX:
				self.deltaX *= -1
			if changeY:	
				self.deltaY *= -1
		else:
			if changeX and (not self.wallX):
				self.deltaX *= -1
			if changeY and (not self.wallY):	
				self.deltaY *= -1	
			self.resetWallHit()
		return
		
	def resetWallHit(self):
		self.wallX = False
		self.wallY = False			
		return
	
	def move(self):
		r, b, g = self.c
		newColor = (r, self.resistance, 0)
		self.addColor(newColor)
		self.x += self.deltaX
		self.y += self.deltaY
		if self.onlyOnce and self.resistantTimes >= 3:
			self.resistantTimes = 0
			newResistance = self.resistance - SUBSTRACTRESISTANCE
			if newResistance >= 0:
				self.resistance = newResistance
			self.onlyOnce = False
		self.resistantTimes += 1
		return
		
	def resetOnce(self):
		self.onlyOnce = True
		return
	
	def changeColorMove(self):
		self.x += self.deltaX
		self.y += self.deltaY
		r,b,g = self.c
		newGreen = int ((WINDOWWIDTH - self.x)/float (WINDOWWIDTH)*self.greenMax)
		newBlue = int ((WINDOWHEIGHT - self.y)/float (WINDOWHEIGHT)*self.blueMax)
		if newGreen < 0:
			newGreen = 0
		if newBlue < 0:
			newBlue = 0
		if self.invertColors:
			self.changeColor((r, newBlue, newGreen))
		else:
			self.changeColor((r, newGreen, newBlue))
		return
		
	def outOfX(self, xBoundary):
		xRight = self.x + self.w
		if xRight >= xBoundary:
			self.wallX = True 
			return True
		elif self.x < 0:
			self.wallX = True
			return True
		else:
			return False
			
	def outOfY(self, yBoundary):
		yBottom = self.y + self.h
		if yBottom >= yBoundary:
			self.wallY = True
			return True
		if self.y < 0:
			self.wallY = True
			return True
		else:
			return False
	def invertColorCollision(self):
		self.invertColors = not self.invertColors
		return
	
	def avoidWall(self):
		tries = 0
		if self.outOfX(WINDOWWIDTH):
			self.changeMovement(True, False)
			while self.outOfX(WINDOWWIDTH) and tries < 10:
				self.move()
				tries += 1
		if self.outOfY(WINDOWHEIGHT) and tries < 10:
			self.changeMovement(False, True)
			while self.outOfY(WINDOWHEIGHT):
				self.move()
				tries += 1
		return		
	
		
		
class TextScreen:
		def __init__(self, coords, font, size, color):
			self.xCoord, self.yCoord = coords
			self.font = font
			self.size = size
			self.color = color
			
		def display(self, text):
			fontObj = pygame.font.Font(self.font, self.size)
			textSurfaceObj = fontObj.render(text , True, self.color)
			textRectObj = textSurfaceObj.get_rect()
			
			textRectObj.center = (self.xCoord, self.yCoord)
			DISPLAYSURF.blit(textSurfaceObj, textRectObj)
			return	
			
def highlightBox(x, y):
	if boxTest.collidepoint(x,y):
		pygame.draw.rect(DISPLAYSURF, BLUE, (320, 240, WIDTH, HEIGHT))
		return
		
	
def gameOver():
	over = True
	DISPLAYSURF.fill(WHITE)
	gameOverText = TextScreen( (WINDOWWIDTH/2, WINDOWHEIGHT/2), SCOREFONT, 64, BLACK)
	retryText = TextScreen(SCORECOORDS, SCOREFONT, 32, BLACK) 
	gameOverText.display("Game Over")
	retryText.display("Press r to retry")
	while over:

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == K_r:
					over = False
					#print "It is beginning again!"
		pygame.display.update()
	return
	
def checkCollisions(targets):
	for target in targets:
		target.move()
		if target.outOfX(WINDOWWIDTH):
			target.changeMovement(True, False)
		if target.outOfY(WINDOWHEIGHT):
			target.changeMovement(False, True)
	for x in range(len(targets)):
		for y in range(x + 1, len(targets)):
			if targets[x].getRect().colliderect(targets[y].getRect()):
				targets[x].changeMovement(True, True)

	return
	
def randomInt(lowerNum, higherNum):
	return random.randint(lowerNum,higherNum)

def addTargets(targetList, numTargets):
	for x in range(numTargets):	
		target = Target(0,0, WIDTH, HEIGHT)
		target.newCoord()
		target.addColor(RED)
		targetList.append(target)
	for targets in targetList:
		targets.inputMovement(randomInt(LOWERNUM, HIGHERNUM), randomInt(LOWERNUM, HIGHERNUM))	
		
		
		
	
	

if __name__ == '__main__':
    main()
