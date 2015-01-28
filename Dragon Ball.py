import pygame
import sys
import random
import os
from pygame.locals import *

pygame.init()
# Set up window, BGmusic and clock
WINW = 900
WINH = 500
windowSurface = pygame.display.set_mode((WINW, WINH))
transparentSurface = windowSurface.convert_alpha()
pygame.display.set_caption("Dragon Ball")
mainClock = pygame.time.Clock()
FPS = 50
pygame.mixer.music.load("Data/Sound/SS_mode_on.ogg")        # Background music when Super Sayan mode is on

# Set up color
BGCOLOR = (80, 80, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)
YELLOW = (255, 255, 0)
RED = (200, 10, 10)
GREEN = (10, 150, 10)

# set up game constants
SCORETHRESHOLD = 3000       # energy damage will be increased by 1 in every 3000 scores earned
MAXBARVALUE = 100
ENERGYBARW = MAXBARVALUE+2
ENERGYBARH = 10

class SOUND:    # Holds all the sound files' locations and names
	goSS = pygame.mixer.Sound("Data/Sound/Go_SS.ogg")           # Sound when going to Super Sayan mode
	charging = pygame.mixer.Sound("Data/Sound/Charging.ogg")        # Sound when charging Kamehameha
	releasing = pygame.mixer.Sound("Data/Sound/Releasing.ogg")      # Sound when releasing Kamehameha
	blink = pygame.mixer.Sound("Data/Sound/Blink.ogg")                  # Sound when character blinks
	shoot = pygame.mixer.Sound("Data/Sound/Shoot.ogg")                  # Sound for normal energy shooting
	charging_e = pygame.mixer.Sound("Data/Sound/Charging_e.ogg")        # Sound when charging explosive wave

class Background:       # holds background components
	STARMINSIZE = 2
	STARMAXSIZE = 8
	STARSPEED = 2
	stars = []

	def animate(self):               # Makes a background with stars going to left
		windowSurface.fill(BGCOLOR)
		starSize = random.randint(self.STARMINSIZE, self.STARMAXSIZE)         # randomly selects a size for a star
		starImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects\star.png"), (starSize, starSize))        # make the star image of the randomly chosen size
		self.stars.append({"rect": pygame.Rect(WINW, random.randint(0, WINH), 0, 0), "image" : starImg})             # append the star's rect info and image in the 'stars' list
		for s in self.stars[:]:
			windowSurface.blit(s["image"], s["rect"])           # loops over every star info in the 'stars' list and draw them on the screen according to the rect and image value they hold
			s["rect"].move_ip(-self.STARSPEED, 0)                       # move the current star to left according to the value of STARSPEED
			if s["rect"].right < 0:                                             # check if the star's right edge has gone past the left edge of the screen
				self.stars.remove(s)                                                 # remove the star if it has

class Object:       # creates game objects like meteor, comet and planets
	OBJMINSIZE = 25
	OBJMAXSIZE = 50
	OBJMINSPEED = 1
	OBJMAXSPEED = 5
	OBJECTRATE = 3
	objects = []           # Stores the rectangle info, speed, life and image data of all the objects (asteroids, comets and planets) in the screen
	PLANETRADIUS =280
	PLANETSPEED = 1
	PLANETLIFE = 250

	def add(self, time):       # adds new object on the screen according to the time.
		if time%25 == 0:                        # makes new asteoids on the screen in every 25 frames
			objectSize = random.randint(self.OBJMINSIZE, self.OBJMAXSIZE)
			# randomly chooose the asteroid image among the three asteroids
			objectImg = pygame.transform.scale(random.choice([pygame.image.load("Data/Image/Objects/asteroid1.png"), pygame.image.load("Data/Image/Objects/asteroid2.png"), pygame.image.load("Data/Image/Objects/asteroid3.png")]), (objectSize, objectSize))
			self.objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(self.OBJMINSPEED, self.OBJMAXSPEED), "life" : [objectSize, objectSize], "image" : objectImg})
		if time%100 == 0:                       # makes new comets on the screen in every 100 frames
			n = int((time/100)/10)
			if n > 5:               # limit max number of comets made once to 5
				n = 5
			for i in range(n):              # Adds more comets simultaneously on the screen with time
				objectSize = random.randint(self.OBJMINSIZE, self.OBJMAXSIZE)
				objectImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/comet.png"), (objectSize, objectSize))
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(self.OBJMINSPEED, self.OBJMAXSPEED), "life" : [objectSize+int(time/1000), objectSize+int(time/1000)], "image" : objectImg})
		if time%1500 == 0:              # makes planets on the screen in every 1000 frames
			if (time/1500) <= 3:         # the first three planets have relatively smaller radius and less life i.e easier to destroy
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(int(WINH/4), int(WINH/3)), self.PLANETRADIUS+(5*int(time/1000)), self.PLANETRADIUS+(5*int(time/1000))), "speed" : self.PLANETSPEED, "life" : [self.PLANETLIFE+int(time/1000)*25, self.PLANETLIFE+int(time/1000)*25], "image" : pygame.transform.scale(pygame.image.load("Data/Image/Objects/Planet.png"), ((5*int(time/1000))+self.PLANETRADIUS, (5*int(time/1000))+self.PLANETRADIUS))})
			else:                               # After the third planet, planets have large radius and more life i.e harder to destroy
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(int(WINH/4), int(WINH/3)), self.PLANETRADIUS+(5*int(time/1000)), self.PLANETRADIUS+(5*int(time/1000))), "speed" : self.PLANETSPEED, "life" : [2*self.PLANETLIFE+int(time/1000)*10, 2*self.PLANETLIFE+int(time/1000)*10], "image" : pygame.transform.scale(pygame.image.load("Data/Image/Objects/Planet.png"), (self.PLANETRADIUS+(5*int(time/1000)), self.PLANETRADIUS+(5*int(time/1000))))})

	def move(self):      # Moves the objects (asteroids, comets and planets) to left
		global score
		for o in self.objects[:]:
			o["rect"].move_ip(-o["speed"], 0)               # move object to left
			windowSurface.blit(o["image"], o["rect"])
			for e in Energy().energy[:]:                                     # loop over every energy blasts on the screen
				if e["rect"].colliderect(o["rect"]):          # check if the current object collides with any energy blast on the screen
					o["life"][0] -= e["damage"]                 # if it collides, reduce the life of the object according to the damage of the enegy
					Energy().energy.remove(e)                                # remove the energy blast that collided
					prevScore = score
					if o["life"][0] <= 0:                              # if the life of the object is zero or less
						score += o["life"][1]                       # increase the score by the value of life of the object
						if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and Energy().ENERGYDMG <= Energy().MAXENERGYDMG:
							Energy().ENERGYDMG += 1          # increase the damage of energy as you destroy more objects but upto the MAXENERGYDMG
						self.objects.remove(o)                           # then remove the object which was destroyed by the energy blast

class Energy:           # manages all sort of energy moves in the game
	ENERGYPERSECOND = 0.2
	ENERGYSPEED = 5
	ENERGYW = 55
	ENERGYH = 25
	ENERGYDMG = 10
	MAXENERGYDMG = 20
	energy = []     # stores the rectangle information and the image data of each energy as a dictionary in this list
	KAMEHAMEHADMG = 3.8
	EXPLOSIVEWAVEDMG = 1
	KAMEHAMEHA = {"rect" : pygame.Rect(0, 0, 0, 0), "damage" : KAMEHAMEHADMG}

	def add(self, char):       # Adds new energy dictionary to the list energy
		global t1, t2           # t1 and t2 value are used to make some delays in adding new energy on the screen without slowing down the whole game's FPS
		# t2's value is kept constant but t1's value is increased by 1 in every frame. if t1's value if the multiple integer of t2, then new energy is added
		# so in a sense, t2's value kinda acts like the value that determines after how many frame's should one energy be added after another energy
		# choose energy blast's image when super sayan mode is on
		if char.superSayan:
			energyImg = pygame.transform.scale(pygame.image.load("Data/Image/Hero/SS_Energy.png"), (self.ENERGYW, self.ENERGYH))
			x = 2               # x holds the integer value that will increase energy damage i.e make damage double if supersayan
		# choose energy blast's image when super sayan mode is off
		else:
			energyImg = pygame.transform.scale(pygame.image.load("Data/Image/Hero/Energy.png"), (self.ENERGYW, self.ENERGYH))
			x = 1               # make no change in energy's dame value if super sayan mode is off
		energyRect = energyImg.get_rect()               # get rect around the energy image
		energyRect.centery = char.rect.centery        # set its centery to player's centery
		energyRect.left = char.rect.right                  # set energy's left side to player's right side value
		t1 += 1                     # increase t1's value
		if t1%t2 == 0 or t1 == 9:               # if t1 is multiple of t2 or if t1 == 9 (which is for the 1st energy released when mouse click for the first time)
			SOUND.shoot.play()                  # play shoot sound
			self.energy.append({"rect" : energyRect, "image" : energyImg, "damage" : x*self.ENERGYDMG})           # add new energy

	def move(self):           # move the energies forward
		for e in self.energy[:]:
			e["rect"].move_ip(self.ENERGYSPEED, 0)
			windowSurface.blit(e["image"], e["rect"])
			if e["rect"].left > WINW:
				self.energy.remove(e)

	def kamehameha(self, char):                              # shoots Kamehameha
		global score, time, chargeTime, topScore, dead
		self.KAMEHAMEHA["rect"].width = 0                    # set initial width of kamehameha to zero so that it isn't visible on the screen
		self.KAMEHAMEHA["rect"].height = char.rect.height+40           # set its height a little bit greater than player's height
		if char.type == "hero":
			# set the kamehameha's left side equal to the player's right side so that it sees to come out from the hand and moves toward right
			self.KAMEHAMEHA["rect"].left = char.rect.right
		else:
			# set the kamehameha's left side equal to the player's left side so that it sees to come out from the hand and moves toward left
			self.KAMEHAMEHA["rect"].left = char.rect.left
		self.KAMEHAMEHA["rect"].centery = char.rect.centery        # align the kamehameha beam so that it emerges from the mid of the player
		if char.superSayan:                              # if Super Sayan mode is on
			self.KAMEHAMEHA["damage"] = 2*(self.KAMEHAMEHA["damage"]+chargeTime)           # Double the kamehameha's damage value in SS mode
		else:
			self.KAMEHAMEHA["damage"] = self.KAMEHAMEHA["damage"]+chargeTime                  # Increase kamehameha's damage according to the time it was being charged
		kImg = pygame.image.load("Data/Image/Hero/kamehameha.png")
		while self.KAMEHAMEHA["rect"].right < WINW+200:                             # while Kamehameha's right side is within the 200 pixel additional distance from the window's width
			kamehamehaImg = pygame.transform.scale(kImg, (self.KAMEHAMEHA["rect"].width, self.KAMEHAMEHA["rect"].height))   # set kamehameha's image to current KAMEHAMEHA["rect'}'s width and height
			Background().animate()                # keep animating the background
			if time%25 == 0:                # add objects on the screen when time is a multiple of 25
				Object().add(time)
			time += 1
			Object().move()                                   # keep moving the objects
			Energy().move()                                    # keep moving the energy blasts on the screen
			displayScore()                                  # keep displaying the score
			drawHealthBar(char)                      # draw health bar
			drawEnergyBar(char, 0)                            # draw no energy while Kamehameha is progressing to the right side
			self.KAMEHAMEHA["rect"].width += Energy().ENERGYSPEED+5           # increase Kamehameha's length a little bit faster than that of ordinary energy's speed
			windowSurface.blit(char.Img, char.rect)                       # draw player's image on the screen
			windowSurface.blit(kamehamehaImg, self.KAMEHAMEHA["rect"])       # draw kamehameha in its current position on the screen
			if char.isDead():                        # check if player got hit
				dead = True
				if score > topScore:            # if score is higher than top score
					topScore = score            # make the score top score
				break                           # break the while loop and go to end of the code
			for o in Object().objects[:]:
				windowSurface.blit(o["image"], o["rect"])                       # draw objects again on the screen so that they appear over kamehameha
				if self.KAMEHAMEHA["rect"].colliderect(o["rect"]):               # check if the current object collided with kamehameha
					o["life"][0] -= self.KAMEHAMEHA["damage"]                    # subtract life is yes
					prevScore = score
					if o["life"][0] <= 0:                                                       # check if objects life is zero or less
						score += o["life"][1]                                   # increase score
						if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and self.ENERGYDMG <= self.MAXENERGYDMG:
							self.ENERGYDMG += 1          # increase energy damage if less than max energy damage
						Object().objects.remove(o)                                                       # then remove the object
			pygame.display.update()                                                     # update the changes made in the above While loop
			mainClock.tick(FPS)
		if self.KAMEHAMEHA["rect"].right >= WINW+200:                         # stop the releasing sound after kamehameha is over
			SOUND.releasing.stop()
		self.KAMEHAMEHA["damage"] = self.KAMEHAMEHADMG                    # reset the kamehameha's damage value to default value

	def explosiveWave(self, char):
		global score, time, chargeTime, topScore, dead
		MAXRADIUS = 40
		wave = [dict(center=(random.randint(0, WINW), random.randint(0, WINH)), radius = random.randint(0, 10)) for x in range((chargeTime+1)*40)]
		if char.superSayan: x = 2       # x is the damaga multiplier i.e double damage if in SS mode
		else: x = 1
		if char.isDead():                        # check if player got hit
			dead = True
			if score > topScore:            # if score is higher than top score
				topScore = score            # make the score top score
			return                           # get out of this function
		while wave != []:
			transparentSurface.fill((0, 0, 0, 0))
			windowSurface.fill(BGCOLOR)
			for s in Background().stars:
				windowSurface.blit(s["image"], s["rect"])
			for o in Object().objects[:]:
				windowSurface.blit(o["image"], o["rect"])
				o["life"][0] -= x*(self.EXPLOSIVEWAVEDMG*(chargeTime/2.5+0.1))
				prevScore = score
				if o["life"][0] < 0:
					score += o["life"][1]                                   # increase score
					if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and self.ENERGYDMG <= self.MAXENERGYDMG:
						Energy().ENERGYDMG += 1          # increase energy damage if less than max energy damage
					Object().objects.remove(o)
			for e in Energy().energy:
				windowSurface.blit(e["image"], e["rect"])
			for w in wave[:]:
				w["radius"] += 1
				if char.superSayan:
					pygame.draw.circle(transparentSurface, (w["radius"]*5, w["radius"]*5, 0, w["radius"]*2), w["center"], w["radius"])    # draw a yellow transparent circle
				else:
					pygame.draw.circle(transparentSurface, (w["radius"]*5, 0, 0, w["radius"]*2), w["center"], w["radius"])           # draw a red transparent circle
				if w["radius"] > MAXRADIUS:
					wave.remove(w)
			displayScore()                                  # keep displaying the score
			drawHealthBar(char)
			drawEnergyBar(char, 0)                            # draw no energy while explosive wave is progressing to the right side
			if char.isDead():                        # check if got hit
				dead = True
				if score > topScore:            # if score is higher than top score
					topScore = score            # make the score top score
				break                           # break the while loop and go to end of the code
			windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))                         # draw the transparent over the windowSurface
			windowSurface.blit(char.Img, char.rect)
			pygame.display.update()
			mainClock.tick(FPS/1.5)
		SOUND.releasing.stop()

class Character:
	size = (35, 80)
	BLINKDISTANCE = size[1]+40

	def __init__(self, health, energy, superSayan, charging, abilities, type):
		self.health = health
		self.energy = energy
		self.superSayan = superSayan
		self.charging = charging
		self.abilities = abilities
		self.type = type
		if self.type == "hero":
			self.energyImgs = [pygame.image.load("Data/Image/Hero/SS_Energy_1.png"), pygame.image.load("Data/Image/Hero/SS_Energy_2.png")]
		elif self.type == "e_buu":
			self.energyImgs = [pygame.image.load("Data/Image/Buu/SS_Energy_1.png"), pygame.image.load("Data/Image/Buu/SS_Energy_2.png")]

	def isDead(self):               # check if player got hit by any object
		for o in Object().objects[:]:
			if self.rect.colliderect(o["rect"]):           # if got hit
				if self.superSayan:
					self.health -= o["life"][1]/10        # take half the damage in superSayan mode
				else:
					self.health -= o["life"][1]/5          # take full damage in normal mode
				Object().objects.remove(o)
				if self.health <= 0:
					return True                                     # return True
		return False                # else return False

	def blink(self, dir):             # makes the player blink up or down
		if self.superSayan:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/Hero/SS_Blink.png"), self.size)
		else:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/Hero/Blink.png"), self.size)
		if dir == "down":                           # if blink down
			move = self.BLINKDISTANCE
		elif dir == "up":                           # if blink up
			move = -self.BLINKDISTANCE
		windowSurface.blit(blinkImg, self.rect)                               # make the blink image in initial position
		self.rect.move_ip(0, move)            # move the player rect to final position
		if self.rect.bottom > WINH:                         # if final position below the bottom of window
			self.rect.bottom = WINH
		if self.rect.top < 0:                                   # if final position above the top of window
			self.rect.top = 0
		pygame.mouse.set_pos(self.rect.center)          # move mouse to final position
		windowSurface.blit(blinkImg, self.rect)                                   # make the blink image in final position
		if self.charging[0]:
			self.drawEnergySphere()
		pygame.display.update()                                                             # update the change
		pygame.time.wait(150)                                                               # make the screen freeeze while blinking

	def playerImage(self, task, firstRun):                  # return player's image according to the current task it is doing
		# choose among the Super Sayan's images is super sayan mode on
		if self.superSayan:
			if self.type == "hero":
				energyImg = pygame.transform.scale(random.choice(self.energyImgs), (self.size[0]+10, self.size[1]+10))
				if task == "None":
					img = pygame.image.load("Data/Image/Hero/SS_Normal.png")
				elif task == "Shoot":
					img = pygame.image.load("Data/Image/Hero/SS_Shooting.png")
				elif task == "Charge":
					img = pygame.image.load("Data/Image/Hero/SS_Charging.png")
				elif task == "Release":
					img = pygame.image.load("Data/Image/Hero/SS_Releasing.png")
				elif task == "Release Wave":
					img = pygame.image.load("Data/Image/Hero/SS_Releasing_e.png")
		# choose among the normal images if super sayan mode off
		else:
			if self.type == "hero":
				if task == "None":
					img = pygame.image.load("Data/Image/Hero/Normal.png")
				elif task == "Shoot":
					img = pygame.image.load("Data/Image/Hero/Shooting.png")
				elif task == "Charge":
					img = pygame.image.load("Data/Image/Hero/Charging.png")
				elif task == "Release":
					img = pygame.image.load("Data/Image/Hero/Releasing.png")
				elif task == "Release Wave":
					img = pygame.image.load("Data/Image/Hero/Releasing_e.png")
		self.Img = pygame.transform.scale(img, self.size)
		if self.superSayan:
			windowSurface.blit(energyImg, (self.rect.left-5, self.rect.top-10, 0, 0))
		if firstRun: # tell to get player rect at first run
			self.rect = self.Img.get_rect()         # get rectangle of current player image
		windowSurface.blit(self.Img, self.rect)

	def drawEnergySphere(self):
		# add a circular energy field while charging
		CENTER = (self.rect.centerx-10, self.rect.centery+15)     # set the circular energy field's circle
		radius = (5-chargeTime)*10                                                  # set the radius of the fiels which decreses with chargetime
		transparentSurface.fill((0, 0, 0, 0))                                       #  fill transparentSurface with an invisible colour
		if self.superSayan:
			pygame.draw.circle(transparentSurface, (chargeTime*50, chargeTime*50, 0, chargeTime*40), CENTER, radius)    # draw a yellow transparent circle
		else:
			pygame.draw.circle(transparentSurface, (chargeTime*50, 0, 0, chargeTime*40), CENTER, radius)           # draw a red transparent circle
		windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))                         # draw the transparent over the windowSurface

	def levelUp(self, score):           # level up hero and unlock new attacks according to the score
		global mouseDown
		upgraded = False        # tell if any ability was added
		if score > 25000:
			if "SS" not in self.abilities:
				pygame.event.clear()        # clear all events in queue to prevent the paused screen to be resumed accidently
				self.abilities.append("SS")
				upgraded = True
				pause("Press 'A' to activate Super Sayan!", False, -1, -1)
		elif score > 10000:
			if "explosive wave" not in self.abilities:
				pygame.event.clear()
				self.abilities.append("explosive wave")
				upgraded = True
				pause("Press 'D' to use Explosive Wave! (Drains half energy)", False, -1, -1)
		elif score > 2500:
			if "kamehameha" not in self.abilities:
				pygame.event.clear()
				self.abilities.append("kamehameha")
				upgraded = True
				pause("Press 'Space' to use Kamehameha! (Drains half energy)", False, -1, -1)
		if upgraded:            # if any of the ability was added
			if mouseDown:       # if the user was shooting while the player levelup-ed, stop the shooting after resuming
				mouseDown = False

def terminate():            # save the current top score and close the game
	topScoreFile("save")
	pygame.quit()
	sys.exit()

def writeText(text, color, size, x, y, returnTextInfo):           # writes text on the surface
	font = pygame.font.SysFont("Comic Sans MS", size, True)
	textObj = font.render(text, True, color)
	textRect = textObj.get_rect()
	textRect.topleft = (x, y)
	if returnTextInfo:              # if rectangle data requested, return textObj and textRect
		return textObj, textRect
	windowSurface.blit(textObj, textRect)

def topScoreFile(mode):           # save topScore in a file and load it later
	if mode == "load":                      # to load score
		if not os.path.isfile("Data/topScore.txt"):               # if topScore.txt file not found
			return 0                                                                        # return 0 for top score
		else:                                                                                   # if file present
			with open("Data/topScore.txt") as file:
				data = file.read().lower()
			score = ""
			for i in data:
				# If someone messes with the topScore file
				if (ord(i)-ord("a")) > 9:
					windowSurface.fill(BGCOLOR)
					writeText("Nice try messing with the top score file.", WHITE, 24, 150, 135, False)
					writeText("But you are busted!! Top score is resetted to 0.", WHITE, 24, 100, 165, False)
					with open("Data/topScore.txt", "w") as file:
						file.write("a")
					pause("Press a key loser!", False, -1, -1)
					return 0
				score += str(ord(i)-ord("a"))                                   # convert the score from alphabet to number
			return int(score)                                                       # return the integer value of the score
	if mode == "save":          # to save score
		eScore = ""         # encrypt score before storing i.e convert number to alphabet
		for i in str(topScore): eScore += str(chr(ord("a")+int(i)))         # convert number to alphabet
		with open("Data/topScore.txt", "w") as file:
			file.write(eScore)

def displayScore():          # Displays the score and top score on the screen
	global score, topScore
	score1Text, score1Rect = writeText("Score:", WHITE, 24, 10, 10, True)
	score2Text, score2Rect = writeText(str(score), WHITE, 24, score1Rect.right+5, 10, True)
	topScore1Text, topScore1Rect = writeText("Top Score:", WHITE, 24, 10, score1Rect.bottom+3, True)
	topScore2Text, topScore2Rect = writeText(str(topScore), YELLOW, 24, topScore1Rect.right+5, score1Rect.bottom+3, True)
	windowSurface.blit(score1Text, score1Rect)
	windowSurface.blit(score2Text, score2Rect)
	windowSurface.blit(topScore1Text, topScore1Rect)
	windowSurface.blit(topScore2Text, topScore2Rect)

def drawHealthBar(char):      #  health bar with current health left
	barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (ENERGYBARW, ENERGYBARH))
	if char.type == "hero":
		pygame.draw.rect(windowSurface, GREEN, (12, WINH - ENERGYBARH - 23, char.health, ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(10, WINH - ENERGYBARH - 25, ENERGYBARW, ENERGYBARH))
	else:
		pygame.draw.rect(windowSurface, GREEN, (WINW-char.health-12, WINH - ENERGYBARH - 23, char.health, ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(WINW-char.health-10, WINH - ENERGYBARH - 25, ENERGYBARW, ENERGYBARH))

def drawEnergyBar(char, manualDrain):                     # draw energy bar with current amount of energy left in it
	barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (ENERGYBARW, ENERGYBARH))
	pygame.draw.rect(windowSurface, RED, (12, WINH - 18, char.energy, ENERGYBARH-2))
	windowSurface.blit(barImg, pygame.Rect(10, WINH - 20, ENERGYBARW, ENERGYBARH))
	if char.charging[0]:                    # if kamehameha is charging
		char.energy -= manualDrain        # decrease the energyBar with value given for manualDrain
	else:                           # if kamehameha not charging
		if char.superSayan:         # if SS mode on
			if char.energy > 0:       # if energy not zero
				char.energy -= Energy().ENERGYPERSECOND        # drain energy in SS mode
		else:                       # is SS mode off
			if char.energy < MAXBARVALUE:           # if energy not full
				char.energy += Energy().ENERGYPERSECOND            # increase the energy
		if char.energy < 0:
			char.energy = 0

def pause(text, drawRect, x, y):                # pause the game
	global mouseDown
	pygame.mouse.set_visible(True)              # make mouse visible while paused
	while True:
		try:
			if not dead:
				for o in Object().objects[:]:
					windowSurface.blit(o["image"], o["rect"])
		except NameError: pass
		textObj, textRect = writeText(text, WHITE, 26, x, y, True)
		writeText("Press any key. . .", WHITE, 24, WINW-250, WINH-50, False)
		if (x, y) == (-1, -1):              # if (x, y) == (-1, -1), put the text at the center of the screen
			textRect.centerx = windowSurface.get_rect().centerx
			textRect.centery = windowSurface.get_rect().centery
		if drawRect:                       # if drawRect == True
			pygame.draw.rect(windowSurface, BGCOLOR, (textRect.left-2, textRect.top-5, textRect.width+4, textRect.height+10))       # Make a rectangle below the text
		windowSurface.blit(textObj, textRect)               # make the text on the screen
		event = pygame.event.wait()
		if event.type == QUIT:
			terminate()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				terminate()
			pygame.mouse.set_visible(False)         # make mouse invisible again if resumed
			mouseDown = False
			return
		pygame.display.update()

def stopAllSounds():
	SOUND.goSS.stop()
	SOUND.releasing.stop()
	SOUND.charging.stop()
	SOUND.blink.stop()
	SOUND.charging_e.stop()
	SOUND.shoot.stop()

def main():
	global time, score, chargeTime, mouseDown, dead, topScore, t1, t2
	# Start of the game
	while True:
		pygame.mouse.set_visible(False)
		time = score = 0                # set initial time and score to 0
		chargeTime = 1                  # charge time
		Energy().energy.clear()                         # make initial energy empty
		Object().objects.clear()                        # make initial object empty
		topScore = topScoreFile("load")             # load top score from the 'topScore.txt' file
		mouseDown = False       # set supersayan and mouse chicked status to false
		dead = False
		# startingTexts holds texts to be displayed turn by turn on the screen
		startingTexts = ["Dragon Ball", "Move mouse cursor to move character and hold left click to attack.", "Destroy the objects and score more.", "Press 'W' and 'S' to blink up and down respectively.", "After unlocking, press 'A' to become Super Sayan.", "After unlocking, hold 'Space', then release it to use Kamehameha.", "After unlocking, hold 'D', then release it to use Explosive wave.", "Press 'P' to pause and 'Esc' to close the game."]
		wallpaper = pygame.transform.scale(pygame.image.load("Data/Image/Welcome.jpg"), (WINW, WINH))
		for t in range(len(startingTexts)):             # write the texts inside the startingTexts turn by turn
			windowSurface.blit(wallpaper, pygame.Rect(0, 0, WINW, WINH))
			if t == 0:
				tempText, textRect = writeText(startingTexts[t], WHITE, 50, 0, 0, True)
			else:
				tempText, textRect = writeText(startingTexts[t], TEAL, 24, 0, 0, True)
			textRect.centerx = windowSurface.get_rect().centerx
			textRect.centery = windowSurface.get_rect().centery-50
			windowSurface.blit(tempText, textRect)
			pygame.display.update()
			if t == len(startingTexts)-1:               # For last text, draw the text on the center of the string
				pause("Press any key to start the game.", False, -1, -1)
			else:                                                   # else draw the text on the bottomright of the window
				pause("", False, -1, -1)
		hero = Character(MAXBARVALUE, MAXBARVALUE, False, [False, "n"], [], "hero")
		hero.playerImage("None", True)
		hero.rect.centerx = 30
		pygame.mouse.set_pos(hero.rect.center)    # move mouse to player's center
		t1 = t2 = 8     # controls the time delay between the energies releases continously
		c1 = c2 = 2*FPS   # use to measure the charge time value
		while not dead:
			time += 1                   # increase time by 1 per frame
			if hero.energy <= 0 and not hero.charging[0]:          # if energy bar empty
				hero.superSayan = False          # turn off SS mode
			if not hero.superSayan:
				pygame.mixer.music.stop()   # if SS is off, stop the SS on music
			Background().animate()
			displayScore()
			drawEnergyBar(hero, 0)
			drawHealthBar(hero)
			hero.levelUp(score)     # levelup the hero according to the score
			Energy().move()
			if time%25 == 0:                # add objects on the screen when time is a multiple of 25
				Object().add(time)
			Object().move()
			if hero.isDead():                        # check if got hit
				dead = True
				if score > topScore:            # if score is higher than top score
					topScore = score            # make the score top score
				break                           # break the while loop and go to end of the code
			# event handling
			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				if not hero.charging[0]:
					if event.type == MOUSEBUTTONDOWN:
						# allowing shooting only if not charging
						mouseDown = True
					if event.type == MOUSEBUTTONUP:
						# stop shootin if mouse button released
						mouseDown = False
					if event.type == KEYDOWN:
						# Only allow pausing the game while not charging
						if event.key == ord("p"):
							pause("Paused", False, -1, -1)
				if event.type == KEYDOWN:
					if event.key == ord("w"):
						SOUND.blink.play()
						hero.blink("up")
					elif event.key == ord("s"):
						SOUND.blink.play()
						hero.blink("down")
					elif event.key == ord("a") and "SS" in hero.abilities:
						hero.superSayan = not hero.superSayan
						if hero.superSayan:
							SOUND.goSS.play()
							pygame.mixer.music.play(-1, 0.0)
						hero.playerImage("None", False)
					elif event.key == K_SPACE and "kamehameha" in hero.abilities:
						if hero.energy >= 0.5*MAXBARVALUE:             # if energy is atleast 50
							hero.charging = [True, "k"]             # charging kamehameha
							stopAllSounds()
							SOUND.charging.play()
							drawEnergyBar(hero, 0.5*MAXBARVALUE)       # drain energy by 50
					elif event.key == ord("d") and "explosive wave" in hero.abilities:
						if hero.energy >= 0.5*MAXBARVALUE:             # if energy is full
							hero.charging = [True, "e"]             # charging
							stopAllSounds()
							SOUND.charging_e.play()
							drawEnergyBar(hero, 0.5*MAXBARVALUE)       # drain all the energy
					elif event.key == K_ESCAPE:
						terminate()
				if event.type == KEYUP:
					if hero.charging[0]:                # if charging
						if event.key == K_SPACE and hero.charging[1] == "k":    # if chargin Kamehameha
							SOUND.charging.stop()       # stop the charging sound
							hero.playerImage("Release", False)
							SOUND.releasing.play()      # play the kamehameha releasing sound
							Energy().kamehameha(hero)       # draw kamehameha image animation
							hero.charging = [False, "n"]                # stop charging
							hero.playerImage("None", False)
							c1 = 2*FPS
							chargeTime = 1
						elif event.key == ord("d") and hero.charging[1] == "e":
							SOUND.charging_e.stop()       # stop the charging sound
							hero.playerImage("Release Wave", False)
							SOUND.releasing.play()      # play the explosive wave releasing sound
							Energy().explosiveWave(hero)       # draw explosive image animation
							hero.charging = [False, "n"]                # stop charging
							hero.playerImage("None", False)
							c1 = 2*FPS
							chargeTime = 1
				if event.type == MOUSEMOTION:
					hero.rect.centery = event.pos[1]   # move player Rect to current mouse position
			pygame.mouse.set_pos(hero.rect.center)
			if mouseDown:               # if mouse button pressed
				Energy().add(hero)            # add new energy in the screen
				hero.playerImage("Shoot", False)
			elif not mouseDown and not hero.charging[0]:                    # if mouse not pressed and not charging
				t1 = 8                                                              # reset t1's value to 8
				hero.playerImage("None", False)
			if hero.charging[0]:                                                            # if charging
				c1 += 1
				if c1%c2 == 0 and chargeTime != 4:
					chargeTime += 1
				mouseDown = False                                           # prevent shooting energy
				hero.playerImage("Charge", False)
				hero.drawEnergySphere()
			if hero.health <= MAXBARVALUE:
				hero.health += 0.02           # slowly increase health with time
			pygame.display.update()
			mainClock.tick(FPS)
		# Stop all currently playing sounds
		stopAllSounds()
		pygame.mixer.music.stop()
		writeText("Game Over!", WHITE, 30, (WINW/2)-85, (WINH/2)-30, False)
		pygame.display.update()
		pygame.time.wait(900)
		if score == topScore:
			text, rect = writeText("New Top Score: %s" % str(score), YELLOW, 30, 0, 0, True)
			topScoreFile("save")
		else:
			text, rect = writeText("Your Score: %s" % str(score), WHITE, 30, 0, 0, True)
		rect.centerx = windowSurface.get_rect().centerx
		rect.centery = windowSurface.get_rect().centery
		pygame.draw.rect(windowSurface, BGCOLOR, rect)
		windowSurface.blit(text, rect)
		pygame.display.update()
		pygame.time.wait(1800)
		pause("Press any key to play again.", True, -1, -1)

if __name__ == "__main__":
	main()