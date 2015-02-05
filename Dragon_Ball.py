import pygame
from sys import exit
import random
import os
import copy
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
MAXBARVALUE = 100
ENERGYBARW = MAXBARVALUE+4
ENERGYBARH = 10
DEFAULTATTACKPERIOD = 8         # this determines the interval (in terms of frames) between the release of energies
energyUsage = {"kamehameha" : 50, "explosive wave" : 50, "energy ball" : 90}

# game characters
buu = dict(health = [MAXBARVALUE]*2, hpRegen = "0.0001*self.health[1]", specialAttacks = [], abilities = ["Shoot", "None"], type = "buu", attackRate = [0, DEFAULTATTACKPERIOD-3])
goku = dict(health = [MAXBARVALUE]*2, hpRegen = "0.0003*hero.health[1]", abilities = [], type = "hero", attackRate = [0, DEFAULTATTACKPERIOD])

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

class Object:       # manages game objects like meteor, comet and planets. (adds boss too)
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
		if Boss.boss:       # if boss present
			# add no new object on the screen when fighting boss
			return
		else:             # if boss not present
			if time%2000 == 0:           # add new boss at given time interval
				Boss(buu).addBoss()        # add boss in the game
				return
		if time%27 == 0:                        # makes new asteoids on the screen in every 25 frames
			objectSize = random.randint(self.OBJMINSIZE, self.OBJMAXSIZE)
			# randomly chooose the asteroid image among the three asteroids
			objectImg = pygame.transform.scale(random.choice([pygame.image.load("Data/Image/Objects/asteroid1.png"),
			                                                  pygame.image.load("Data/Image/Objects/asteroid2.png"), pygame.image.load("Data/Image/Objects/asteroid3.png")]), (objectSize, objectSize))
			self.objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize),
			                     "speed" : random.randint(self.OBJMINSPEED, self.OBJMAXSPEED), "life" : [objectSize+level*5, objectSize+level*5], "image" : objectImg})
		if time%100 == 0:                       # makes new comets on the screen in every 100 frames
			n = int((time/100)/10)
			if n > 5:               # limit max number of comets made once to 5
				n = 5
			for i in range(n):              # Adds more comets simultaneously on the screen with time
				objectSize = random.randint(self.OBJMINSIZE, self.OBJMAXSIZE)
				objectImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/comet.png"), (objectSize, objectSize))
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize),
				                     "speed" : random.randint(self.OBJMINSPEED, self.OBJMAXSPEED), "life" : [objectSize+level*20, objectSize+level*20], "image" : objectImg})
		if time%1500 == 0:              # makes planets on the screen in every 1000 frames
			if (time/1500) <= 3:         # the first three planets have relatively smaller radius and less life i.e easier to destroy
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(int(WINH/4), int(WINH/3)), self.PLANETRADIUS+(5*level), self.PLANETRADIUS+(5*level)),
				                     "speed" : self.PLANETSPEED, "life" : [self.PLANETLIFE+level*10, self.PLANETLIFE+level*10],
				                     "image" : pygame.transform.scale(pygame.image.load("Data/Image/Objects/Planet.png"), ((5*level)+self.PLANETRADIUS, (5*level)+self.PLANETRADIUS))})
			else:                               # After the third planet, planets have large radius and more life i.e harder to destroy
				self.objects.append({"rect" : pygame.Rect(WINW, random.randint(int(WINH/4), int(WINH/3)), self.PLANETRADIUS+(5*level), self.PLANETRADIUS+(5*level)),
				                     "speed" : self.PLANETSPEED, "life" : [2*self.PLANETLIFE+level*10, 2*self.PLANETLIFE+level*10],
				                     "image" : pygame.transform.scale(pygame.image.load("Data/Image/Objects/Planet.png"), (self.PLANETRADIUS+(5*level), self.PLANETRADIUS+(5*level)))})

	def move(self):      # Moves the objects (asteroids, comets and planets) to left
		if len(self.objects) == 0:
		# get out of this function (method) as got no object to move
			return
		for o in self.objects[:]:
			o["rect"].move_ip(-o["speed"], 0)               # move object to left
			windowSurface.blit(o["image"], o["rect"])

class Energy:           # manages all sort of energy moves in the game
	ENERGYPERSECOND = 0.2
	ENERGYSPEED = 7
	ENERGYW = 55
	ENERGYH = 25
	ENERGYDMG = 10
	MAXENERGYDMG = 2*ENERGYDMG
	KAMEHAMEHADMG = 3.8
	EXPLOSIVEWAVEDMG = 1
	ENERGYBALLDMG = 5

	def add(self, char):       # Adds new energy dictionary to the list energy
		# choose energy blast's image when super sayan mode is on
		if char.superSayan:
			energyImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/SS_Energy.png".format(char.type)), (self.ENERGYW, self.ENERGYH))
			x = 2               # x holds the integer value that will increase energy damage i.e make damage double if supersayan
		# choose energy blast's image when super sayan mode is off
		else:
			energyImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/Energy.png".format(char.type)), (self.ENERGYW, self.ENERGYH))
			x = 1               # make no change in energy's dame value if super sayan mode is off
		energyRect = energyImg.get_rect()               # get rect around the energy image
		if char.type == "hero":
			energyRect.centery = char.rect.centery        # set its centery to player's centery
			energyRect.left = char.rect.right                  # set energy's left side to hero's right side
		else:
			energyRect.centery = char.rect.centery-10
			energyRect.right = char.rect.left+5                  # set energy's right side to boss' left side
		if char.attackRate[0]%char.attackRate[1] == 0:               # if char.attackRate[0] is multiple of char.attackRate[0]
			SOUND.shoot.play()                  # play shoot sound
			char.energies.append({"rect" : energyRect, "image" : energyImg, "damage" : x*char.eDamage})           # add new energy
		char.attackRate[0] += 1                     # increase char.attackRate[0]'s value

	def move(self, char):           # move the energies forward
		global score, dead
		for e in char.energies[:]:
			if char.type == "hero": # move hero's energy
				e["rect"].move_ip(self.ENERGYSPEED, 0)
				if e["rect"].left >= WINW:
					char.energies.remove(e)                         # remove the energy that went past the right side of the window
					continue        # go back to check another energy
				for o in Object.objects[:]:
					if not e: continue                  # if the current energy is already removed, don't continue below
					if e["rect"].colliderect(o["rect"]):          # check if the current object collides with any energy blast on the screen
						o["life"][0] -= e["damage"]                 # if it collides, reduce the life of the object according to the damage of the enegy
						try: char.energies.remove(e)                                # remove the energy blast that collided
						except ValueError: pass         # Sometime ValueError occurs when e is not found in char.energies asit might already be deleted
						if o["life"][0] <= 0:                              # if the life of the object is zero or less
							score += o["life"][1]                       # increase the score by the value of life of the object
							if char.eDamage <= self.ENERGYDMG + level*7:
								char.eDamage += 0.1          # increase the damage of energy as you destroy more objects but upto the MAXENERGYDMG
							Object.objects.remove(o)                           # then remove the object which was destroyed by the energy blast
				for boss in Boss.boss:
					try:
						if e["rect"].colliderect(boss.rect):
							boss.health[0] -= e["damage"]
							if boss.health[0] < 0: boss.health[0] = 0
							try:
								char.energies.remove(e)                                # remove the energy blast that collided
							except ValueError: pass
					except AttributeError: pass             # Attribute error occurs when the boss is created but the boss.rect isn't installized yet
			else: # move boss' energies
				for o in Object.objects[:]:
					if not e: continue                  # if the current energy is already removed, don't continue below
					if e["rect"].colliderect(o["rect"]):          # check if the current object collides with any energy blast on the screen
						o["life"][0] -= e["damage"]                 # if it collides, reduce the life of the object according to the damage of the enegy
						try: char.energies.remove(e)                                # remove the energy blast that collided
						except ValueError: pass         # Sometime ValueError occurs when e is not found in char.energies asit might already be deleted
						if o["life"][0] <= 0:                              # if the life of the object is zero or less
							Object.objects.remove(o)                           # then remove the object which was destroyed by the energy blast
				e["rect"].move_ip(-(self.ENERGYSPEED*1.5), 0)         # boss' energies move abit faster
				if self.collides(self, e, hero.energies):
					char.energies.remove(e)
					continue        # go for another energy
				if e["rect"].colliderect(hero.rect):
					hero.health[0] -= e["damage"]/5
					if hero.health[0] < 0:
						hero.health[0] = 0
						dead = True
					if e:
						char.energies.remove(e)                                # remove the energy blast that collided if aleardy not removed
						continue
				if e["rect"].right <= 0:
					try: char.energies.remove(e)
					except: continue
			# if the current energy isn't removed, draw it
			if e: windowSurface.blit(e["image"], e["rect"])

	def collides(self, e1, energies):           # checks if a energy collides with other energies
		for e in energies[:]:
			if e1["rect"].colliderect(e["rect"]):
				energies.remove(e)
				return True
		return False

	def kamehameha(self, char):                              # shoots Kamehameha that does huge damage in the line of release
		global score
		char.sMove["rect"].height = char.rect.height+40           # set its height a little bit greater than player's height
		if char.type == "hero":
			# set the kamehameha's left side equal to the player's right side so that it sees to come out from the hand and moves right
			char.sMove["rect"].left = char.rect.right
		else:
			# set the kamehameha's right side equal to the player's left side so that it sees to come out from the hand and moves left
			char.sMove["rect"].right = char.rect.left
		char.sMove["rect"].centery = char.rect.centery        # align the kamehameha beam so that it emerges from the mid of the player
		kamehamehaImg = pygame.transform.scale(char.sMove["img"], (char.sMove["rect"].width, char.sMove["rect"].height))   # set kamehameha's image to current KAMEHAMEHA["rect'}'s width and height
		char.sMove["rect"].width += self.ENERGYSPEED*2           # increase Kamehameha's length
		windowSurface.blit(kamehamehaImg, char.sMove["rect"])       # draw kamehameha in its current position on the screen
		if char.type == "hero":
			for o in Object.objects[:]:
				if char.sMove["rect"].colliderect(o["rect"]):               # check if the current object collided with kamehameha
					o["life"][0] -= char.sMove["damage"]                    # subtract life is yes
					if o["life"][0] <= 0:                                                       # check if objects life is zero or less
						score += o["life"][1]                                   # increase score
						if char.eDamage <= self.ENERGYDMG + level*7:
							char.eDamage += 0.1          # increase energy damage if less than max energy damage
						Object.objects.remove(o)                                                       # then remove the object
			for boss in Boss.boss:                  # loops over all bosses
				if boss:        # if boss present
					if self.collides(char.sMove, boss.energies):            # this will check if kamehameha collides with any enemy energies and deletes them
						pass
					try:
						if char.sMove["rect"].colliderect(boss.rect):           # if current boss collides with kamehameha,
							boss.health[0] -= char.sMove["damage"]*1.5              # reduce boss' life as necessary
					except AttributeError: pass                   # Attribute error arise if the boss is added but its rectangle isn't instalized yet
			if char.sMove["rect"].right >= WINW+500:
				# stop the releasing sound after kamehameha is over
				SOUND.releasing.stop()
				char.charging = [False, False, "n"]                # stop charging
				char.chargeTime[1] = 2*FPS
				char.chargeTime[0] = 1
				char.sMove["rect"].width = 0                    # set initial width of kamehameha to zero so that it isn't visible on the screen
				return "None"
			else:
				return "Release"
		else:
			if self.collides(self, char.sMove, hero.energies):
				pass
			if char.sMove["rect"].colliderect(hero.rect):
				hero.health[0] -= char.sMove["damage"]/90
				if hero.health[0] < 0: hero.health[0] = 0
			if char.sMove["rect"].left < -500:
				# stop the releasing sound after kamehameha is over
				SOUND.releasing.stop()
				char.charging = [False, False, "n"]                # stop charging
				char.chargeTime[1] = 2*FPS
				char.chargeTime[0] = 1
				char.sMove["rect"] = pygame.Rect(0, 0, 0, 0)                    # reset the rectangle
				char.sMove["damage"] = 0
				char.sMove["img"] = None

	def explosiveWave(self, char):                  #shoots an explosive wave that damages (relatively small) everything on the screen
		global score, time, topScore, dead
		MAXRADIUS = 40
		wave = [dict(center=(random.randint(0, WINW), random.randint(0, WINH)), radius = random.randint(0, 15)) for x in range((char.chargeTime[0]+1)*40)]
		if char.superSayan: x = 2       # x is the damaga multiplier i.e double damage if in SS mode
		else: x = 1
		if char.isDead():                        # check if player is dead
			dead = True
			if score > topScore:            # if score is higher than top score
				topScore = score            # make the score top score
			return                           # get out of this function
		while wave != []:
			transparentSurface.fill((0, 0, 0, 0))
			windowSurface.fill(BGCOLOR)
			for s in Background().stars:
				windowSurface.blit(s["image"], s["rect"])
			if char.type == "hero":
				for o in Object.objects[:]:
					windowSurface.blit(o["image"], o["rect"])
					o["life"][0] -= x*(self.EXPLOSIVEWAVEDMG*(char.chargeTime[0]/1.5+0.1+level))
					if o["life"][0] < 0:
						score += o["life"][1]                                   # increase score
						if char.eDamage <= self.ENERGYDMG+level*7:
							char.eDamage += 0.1          # increase energy damage if less than max energy damage
						Object.objects.remove(o)
				# draw all the energies of all bosses
				for boss in Boss.boss:
					if boss:        # if boss present
						try:
							# draw current boss on the screen
							windowSurface.blit(boss.Img, boss.rect)
						except AttributeError: pass     # if boss is added but its rect isn't instalized yet
						# draw the boss' health and energy bars
						drawHealthBar(boss)
						drawEnergyBar(boss)
						if boss.energies: boss.energies.clear()       # if there is any boss' energy, remove all the energies to show that they were destroyed by the explosive wave
						# reduce boss' health
						boss.health[0] -= x*(self.EXPLOSIVEWAVEDMG*(char.chargeTime[0]/1.5+0.1+level))
						if boss.health[0] < 0: boss.health[0] = 0
			else:           # if the char is boss,
				for o in Object.objects[:]:
					windowSurface.blit(o["image"], o["rect"])
				# draw hero on the screen
				windowSurface.blit(hero.Img, hero.rect)
				# draw the hero's health and energy bars
				drawHealthBar(hero)
				drawEnergyBar(hero)
				if hero.energies: hero.energies.clear()          # if any hero's energy present, remove all of them
				# reduce hero's health
				hero.health[0] -= x*(self.EXPLOSIVEWAVEDMG*(char.chargeTime[0]/2))/80
				if hero.health[0] < 0: hero.health[0] = 0
			for e in char.energies: windowSurface.blit(e["image"], e["rect"])
			for w in wave[:]:
				w["radius"] += 1
				if char.superSayan:
					pygame.draw.circle(transparentSurface, (w["radius"]*5, w["radius"]*5, 0, w["radius"]*2), w["center"], w["radius"])    # draw a yellow transparent circle
				else:
					pygame.draw.circle(transparentSurface, (w["radius"]*5, 0, 0, w["radius"]*2), w["center"], w["radius"])           # draw a red transparent circle
				if w["radius"] > MAXRADIUS:
					wave.remove(w)
			char.playerImage("Release Wave")
			displayScore()                                  # keep displaying the score
			drawHealthBar(char)
			drawEnergyBar(char)                            # draw no energy while explosive wave is progressing to the right side
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
		char.charging = [False, False, "n"]

	def energyBallAnimate(self, char, timer = 0):                  # animates the grow of energyBall as it gets charged
		global score
		char.sMove["rect"].width = char.sMove["rect"].height = (15 + (char.chargeTime[0]-timer)*1.2)        # increase energyball's radius with charge time
		char.sMove["rect"].bottom = char.rect.top               # place the energyball above the player
		char.sMove["rect"].centerx = char.rect.centerx
		windowSurface.blit(pygame.transform.scale(char.sMove["img"], char.sMove["rect"].size), char.sMove["rect"])

	def energyBall(self, char): # throws a tracking and devastating energy ball that damages everything in its path
		global score
		if char.type == "hero":
			d = 10000
			for boss in Boss.boss:
				if abs(boss.rect.centery-char.sMove["rect"].centery) < d:
					i = Boss.boss.index(boss)
					d = abs(boss.rect.centery-char.sMove["rect"].centery)
			boss = Boss.boss[i]     # nearest boss
			if char.sMove["rect"].centery < boss.rect.centery:         # if the energyball is above the boss
				char.sMove["rect"].centery += 6+(level/10)             # bring it down
			elif char.sMove["rect"].centery > boss.rect.centery:        # if the energy ball is below the boss
				char.sMove["rect"].centery -= 6+(level/10)             # bring it up
			# for hero, move the energyball to right
			char.sMove["rect"].left += 2*self.ENERGYSPEED
			if char.sMove["rect"].left > WINW+50:
				# set false to energy releasing status if the ebenrgyball went past the right side
				char.charging = [False, False, "n"]
		else:       # if the char is a boss
			if char.sMove["rect"].centery < hero.rect.centery:         # if the energyball is above the hero
				char.sMove["rect"].centery += 6+(level/10)             # bring it down
			elif char.sMove["rect"].centery > hero.rect.centery:        # if the energy ball is below the hero
				char.sMove["rect"].centery -= 6+(level/10)             # bring it up
			# for boss, move the energyball to left
			char.sMove["rect"].right -= 2*self.ENERGYSPEED
			if char.sMove["rect"].right < -50:
				# set false to energy releasing status if the ebenrgyball went past the left side
				char.charging = [False, False, "n"]
		# damage anything that comes in contact
		for o in Object.objects[:]:
			if o["rect"].colliderect(char.sMove["rect"]):
				o["life"][0] -= char.sMove["damage"]
				if o["life"][0] <= 0:
					if char.type == "hero":
						score += o["life"][1]
					Object.objects.remove(o)
		if char.type == "hero":
			for boss in Boss.boss:
				if self.collides(self, char.sMove, boss.energies): pass					# if energy ball collides with any energy, it will remove them
				if char.sMove["rect"].colliderect(boss.rect):
					boss.health[0] -= char.sMove["damage"]
					if boss.health[0] < 0: boss.health[0] = 0
		else:
			if self.collides(self, char.sMove, hero.energies): pass
			if char.sMove["rect"].colliderect(hero.rect):
				hero.health[0] -= char.sMove["damage"]/30
			if hero.health[0] < 0: hero.health[0] = 0
		windowSurface.blit(pygame.transform.scale(char.sMove["img"], char.sMove["rect"].size), char.sMove["rect"])

class Character:
	size = (35, 80)         # size for character
	BLINKDISTANCE = size[1]*2

	def __init__(self, char):
		self.type = char["type"]        # type of character
		if self.type == "hero":
			self.health = copy.deepcopy(char["health"])         # hp for hero
			self.eDamage = Energy.ENERGYDMG                     # energy damage for hero
		else:
			self.health = [(level)*5*h for h in char["health"]]     # hp for boss
			self.eDamage = Energy.ENERGYDMG + level             # energy damage for boss
			if self.eDamage > Energy.MAXENERGYDMG: self.eDamage = Energy.MAXENERGYDMG       # set limit to boss' energy damage
			self.specialAttacks = char["specialAttacks"]        # every boss has a list where they have their special abilities stored later
		self.hpRegen = char["hpRegen"]          # hp regeneration value
		self.energy = [MAXBARVALUE]*2         # energy to use special moves
		self.energies = []          # stores the rectangle information and the image data of each energy as a dictionary in this list
		self.superSayan = False            # super sayan mode
		self.charging = [False, False, "n"]  # tells if charging some special moves
		self.abilities = copy.deepcopy(char["abilities"])      # available abilities for character
		self.chargeTime = [1, 2*FPS, 2*FPS]            # chargeTime[0] holds the time for which energy was charged. chargeTime[1] and chargeTime[2] are used to deduce the chargeTime[0]
		self.attackRate = char["attackRate"]                # rate at which ordinary energies release
		# Images showing energy around the character
		self.energyImgs = [pygame.image.load("Data/Image/{}/SS_Energy_1.png".format(self.type)), pygame.image.load("Data/Image/{}/SS_Energy_2.png".format(self.type))]
		self.sMove = {"rect" : pygame.Rect(0, 0, 0, 0), "damage" : 0, "img" : None, "energyUsage" : 0}         # holds empty slot to later use for special moves (attacks)

	def isDead(self):               # check if player got hit by any object
		if self.type == "hero":     # for hero, check if he collided with any object and if yes, check if his hp <= 0
			for o in Object.objects[:]:
				if self.rect.colliderect(o["rect"]):           # if got hit
					if self.superSayan:
						self.health[0] -= o["life"][1]/10        # take half the damage in superSayan mode
					else:
						self.health[0] -= o["life"][1]/5          # take full damage in normal mode
					Object.objects.remove(o)
				if self.health[0] <= 0:
					return True                                     # return True
			return False                # else return False
		else:           # for boss, only check if his hp <=0
			if self.health[0] <= 0:
				return True                                     # return True
			return False                # else return False

	def blink(self, dir):             # makes the player blink up or down
		SOUND.blink.play()          # play the blink sound
		if self.superSayan:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/SS_Blink.png".format(self.type)), self.size)
		else:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/Blink.png".format(self.type)), self.size)
		if dir == "down":                           # if blink down
			move = self.BLINKDISTANCE
		elif dir == "up":                           # if blink up
			move = -self.BLINKDISTANCE
		windowSurface.blit(blinkImg, self.rect)                               # make the blink image in initial position
		finalRect = self.rect.move(0, move)            # move the player rect to final position
		if finalRect.bottom > WINH:                         # if final position below the bottom of window
			finalRect.bottom = WINH
		if finalRect.top < 0:                                   # if final position above the top of window
			finalRect.top = 0
		if self.type == "hero":
			pygame.mouse.set_pos(finalRect.center)          # move mouse to hero's final position's center
			if self.charging[0]:                    # if hero is charging an attack while blinking, draw the energy sphere
				self.drawEnergySphere()
		self.rect = finalRect       # set player rect value to final rect
		windowSurface.blit(blinkImg, finalRect)                                   # make the blink image in final position
		pygame.display.update()                                                             # update the change
		pygame.time.wait(50)                                                               # make the screen freeze for short time while blinking

	def playerImage(self, task = "None"):                  # return player's image according to the current task it is doing
		# choose among the Super Sayan's images is super sayan mode on
		if self.superSayan:
			if task == "None":
				img = pygame.image.load("Data/Image/{}/SS_Normal.png".format(self.type))
			elif task == "Shoot":
				img = pygame.image.load("Data/Image/{}/SS_Shooting.png".format(self.type))
			elif task == "Charge":
				img = pygame.image.load("Data/Image/{}/SS_Charging.png".format(self.type))
			elif task == "Release":
				img = pygame.image.load("Data/Image/{}/SS_Releasing.png".format(self.type))
			elif task == "Release Wave":
				img = pygame.image.load("Data/Image/{}/SS_Releasing_e.png".format(self.type))
		# choose among the normal images if super sayan mode off
		else:
			if task == "None":
				img = pygame.image.load("Data/Image/{}/Normal.png".format(self.type))
			elif task == "Shoot":
				img = pygame.image.load("Data/Image/{}/Shooting.png".format(self.type))
			elif task == "Charge":
				img = pygame.image.load("Data/Image/{}/Charging.png".format(self.type))
			elif task == "Release":
				img = pygame.image.load("Data/Image/{}/Releasing.png".format(self.type))
			elif task == "Release Wave":
				img = pygame.image.load("Data/Image/{}/Releasing_e.png".format(self.type))
		if self.type == "hero":
			self.Img = pygame.transform.scale(img, self.size)
		else:
			self.Img = pygame.transform.scale(img, (round(self.size[0]), round(self.size[1])))
		if self.superSayan or (self.type != "hero" and task == "Charge"):       # create energy field in SS mode for hero and for boss, create energy field while charging
			energyImg = pygame.transform.scale(random.choice(self.energyImgs), (self.size[0]+15, self.size[1]+10))
			if self.type == "hero":
				windowSurface.blit(energyImg, (self.rect.left-11, self.rect.top-10, 0, 0))
			else:
				windowSurface.blit(energyImg, (self.rect.left-5, self.rect.top-10, 0, 0))
		try:
			if self.rect:       # if self.rect exists, do nothing
				pass
		except AttributeError:  # if self.rect doesn't exist, make it
			self.rect = self.Img.get_rect()         # get rectangle of current player image
			if self.type == "hero":
				self.rect.centerx = 30                      # set hero's center-x constant
			else:
				self.rect.centerx = WINW-40         # set boss' center-x constant
			self.rect.centery = random.randint(round(self.rect.width/2), round(WINH - self.rect.width/2))     # place the player at random vertical position
		windowSurface.blit(self.Img, self.rect)

	def drawEnergySphere(self):
		# add a circular energy field while charging
		CENTER = (self.rect.centerx-10, self.rect.centery+15)     # set the circular energy field's circle
		radius = (5-self.chargeTime[0])*10                                                  # set the radius of the fiels which decreses with chargetime
		transparentSurface.fill((0, 0, 0, 0))                                       #  fill transparentSurface with an invisible colour
		if self.superSayan:
			pygame.draw.circle(transparentSurface, (self.chargeTime[0]*50, self.chargeTime[0]*50, 0, self.chargeTime[0]*40), CENTER, radius)    # draw a yellow transparent circle
		else:
			pygame.draw.circle(transparentSurface, (self.chargeTime[0]*50, 0, 0, self.chargeTime[0]*40), CENTER, radius)           # draw a red transparent circle
		windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))                         # draw the transparent over the windowSurface

	def levelUp(self, score):           # level up hero and unlock new attacks according to the score
		global mouseDown, level
		upgraded = False        # tell if any ability was added
		if level == 5:
			if "SS" not in self.abilities:
				pygame.event.clear()        # clear all events in queue to prevent the paused screen to be resumed accidently
				self.abilities.append("SS")
				upgraded = True
				pause("Press 'A' to activate Super Sayan! (Drains energy gradually)", False, -1, -1)
		elif level == 3:
			if "explosive wave" not in self.abilities:
				pygame.event.clear()
				self.abilities.append("explosive wave")
				upgraded = True
				pause("Hold 'D' to use Explosive Wave! (Drains half energy)", False, -1, -1)
		elif level == 2:
			if "kamehameha" not in self.abilities:
				pygame.event.clear()
				self.abilities.append("kamehameha")
				upgraded = True
				pause("Hold 'Space' to use Kamehameha! (Drains half energy)", False, -1, -1)
		if upgraded:            # if any of the ability was added
			if mouseDown:       # if the user was shooting while the player levelup-ed, stop the shooting after resuming
				mouseDown = False

class Boss(Character):          # creates and manages Boss
	boss = []       # holds info about current boss
	moveSpeed = 2.5
	direction = dict(up = -moveSpeed, down = moveSpeed, none = 0)
	dir = ["none", random.randint(1, 2)*FPS]        # the dir list holds the direction of motion and the time period in that direction
	task = ["None", random.randint(1, 3)*FPS]       # the task holds the current boss' task and the time period to execute that task

	def addBoss(self):           # add a boss
		global level
		self.boss.append(self)
		# every time a boss is added, the moveSpeed is increased a little bit
		if self.moveSpeed < 5:
			self.moveSpeed += round((level-1)/50, 2)

	def BossAI(self, playerTask, hero):          # AI for using boss according to the player's current task
		global score, time, level
		# draw health and energy bars
		drawHealthBar(self)
		drawEnergyBar(self)
		# display player image for current task
		if self.task[0] != "Blink": self.playerImage(self.task[0])     # blinking task draw it's player image separately
		# if boss is dead
		if self.isDead():
			# stop boss' music if dead
			SOUND.boss_releasing.stop()
			SOUND.boss_charging.stop()
			if self.energies:
				Energy.move(Energy, self)       # move boss' energies
			else:
				score += int(0.5*self.health[1])     # increase the score by half value of the boss' total hp
				self.boss.remove(self)          # remove the dead boss
			if not self.boss:
				level += 1      # once the boss is removed, increase the level
				# increase hero's hp with every level
				hero.health[0] += 100
				hero.health[1] += 100
			time += 1
		else:           # if alive
			if self.health[0] < self.health[1]: self.health[0] += eval(self.hpRegen)      # regenerate health with time
			if level > 1:       # Use this feature in levels other than level 1
				# if the player is in approximately same height to boss and the boss is not moving while the player shoots,
				# then get new direction instruction. Note: new dir might be "none" again in which case the boss will not move and get hit by energy
				if self.rect.top < hero.rect.centery < self.rect.bottom and playerTask == "Shoot" and self.dir[0] == "none":
					self.dir = [random.choice(["up",  "down",  "none"]), random.randint(1, 3)*FPS]
				# at level 2 and 3, give the boss the Blink and Charge ability and increase Shooting chances
				if level in [2, 3] and self.abilities.count("Blink") < level-1:
					self.abilities.append("Blink")
					buu["abilities"].append("Blink")
					if "Charge" not in self.abilities:
						self.abilities.append("Charge")          # add the charge ability if not present
						buu["abilities"].append("Charge")
					random.shuffle(self.abilities)  # shuffle the ablilties
					#add explosive wave
				if level >= 2 and "explosive wave" not in self.specialAttacks:
					self.specialAttacks.append("explosive wave")
					buu["specialAttacks"].append("explosive wave")
				if level >= 2 and "kamehameha" not in self.specialAttacks:
					self.specialAttacks.append("kamehameha")
					buu["specialAttacks"].append("kamehameha")
				if level >= 3 and self.specialAttacks.count("energy ball") <=2:     # add two energy ball so that it's chance of being chosen is greater
					self.specialAttacks.append("energy ball")
					buu["specialAttacks"].append("energy ball")
					random.shuffle(self.specialAttacks)
			# choose new task if timer for current task is out and boss is neither charing nor releasing any special energy
			if self.task[1] == 0 and self.task[0] != "Release" and not self.charging[0]:
				while True:
					self.task = [random.choice(self.abilities), random.randint(1, 2)*FPS]        # perform each task for only 1 or 2 seconds
					if self.task[0] == "Charge":
						self.task[1] = self.chargeTime[0] = random.randint(1, 4)*FPS        # if the current task is charge, charge the special attack in the time range 1-4
						self.charging = [True, False, random.choice(self.specialAttacks)]
						if self.energy[0] >= energyUsage[self.charging[2]]:     # if energy is sufficient for the current special attack
							self.energy[0] -= energyUsage[self.charging[2]]        # drain required energy
							# play sound for charging an energy and set required image and damage for them
							if self.charging[2] == "kamehameha":
								SOUND.boss_charging.play()
								self.sMove["img"] = pygame.image.load("Data/Image/Hero/kamehameha.png")
								if self.superSayan:                              # if Super Sayan mode is on
									# Double the kamehameha's damage value in SS mode
									self.sMove["damage"] = 2*(Energy.KAMEHAMEHADMG+self.chargeTime[0]+int(level/3))
								else:
									# Increase kamehameha's damage according to the time it was being charged
									self.sMove["damage"] = Energy.KAMEHAMEHADMG+self.chargeTime[0]+int(level/3)
							elif self.charging[2] == "explosive wave":
								SOUND.charging_e.play()
								# no need to assign image and damage as explosive wave doesn't use self.sMove
							elif self.charging[2] == "energy ball":
								self.sMove["img"] = pygame.image.load("Data/Image/Buu/Energy_ball.png")
								if self.superSayan:                              # if Super Sayan mode is on
									self.sMove["damage"] = 2*(Energy.ENERGYBALLDMG+self.chargeTime[0]/2+int(level/5))
								else:
									self.sMove["damage"] = Energy.ENERGYBALLDMG+self.chargeTime[0]/2+int(level/5)
							break       # break the while loop
						else:
							self.charging = [False, False, "n"]       # change the charging status to default if energy not sufficient
					else:           # if other tasks chosen other than Charge
						if self.task[0] == "Blink": self.task[1] = 1            # blink only once in one frame
						break
			if self.charging == [True, False, "energy ball"]:
				# play the animation if energyball is charging
				Energy.energyBallAnimate(Energy, self, self.task[1])
			if self.task == ["Charge", 1]:
				self.task[0] = "Release"
				self.charging[0], self.charging[1] = False, True            # when releasing, set charging to False and Releasing to True
			# perform current the task
			self.performTask(self.task[0])
			self.task[1] -= 1
			# move the boss up, down or none only if the player isn't releasing energy
			if not self.charging[1]:
				self.rect.move_ip(0, self.direction[self.dir[0]])
			self.dir[1] -= 1
			if self.rect.top <= 0:
				self.rect.top = 0
				self.dir[1] = 0     # if the Boss reaches top, renew the direction next time
			if self.rect.bottom >= WINH:
				self.rect.bottom = WINH
				self.dir[1] = 0     # if the Boss reaches bottom, renew the direction next time
			if self.dir[1] == 0: self.dir = [random.choice(["up",  "down",  "none", "down", "up"]), random.randint(1, 3)*FPS]        # select new direction and perform it for 1-3 seconds

	def performTask(self, task):            # performs given task
		Energy.move(Energy, self)       # move boss' energies
		if task == "None":
			pass
		elif task == "Shoot":
			Energy.add(Energy, self)
		elif task == "Blink":
			if self.dir[0] == "none": self.dir[0] = random.choice(["up", "down"])
			self.blink(self.dir[0])
		elif task == "Release":
			if self.charging[2] == "explosive wave":
				SOUND.charging_e.stop()
				SOUND.boss_releasing.play()
				Energy.explosiveWave(Energy, self)
			elif self.charging[2] == "kamehameha":
				SOUND.boss_charging.stop()
				SOUND.boss_releasing.play()
				Energy.kamehameha(Energy, self)
			elif self.charging[2] == "energy ball":
				SOUND.boss_releasing.play()
				Energy.energyBall(Energy, self)
			if not self.charging[1]:
				SOUND.boss_releasing.stop()
				self.task = ["None", 1]

class SOUND:    # Holds all the sound files' locations and names
	goSS = pygame.mixer.Sound("Data/Sound/Go_SS.ogg")           # Sound when going to Super Sayan mode
	charging = pygame.mixer.Sound("Data/Sound/Charging.ogg")        # Sound when charging Special Attack like Kamehameha
	releasing = pygame.mixer.Sound("Data/Sound/Releasing.ogg")      # Sound when releasing Special Attack like Kamehameha
	boss_charging = pygame.mixer.Sound("Data/Sound/boss_Charging.ogg")
	boss_releasing = pygame.mixer.Sound("Data/Sound/boss_Releasing.ogg")
	blink = pygame.mixer.Sound("Data/Sound/Blink.ogg")                                 # Sound when character blinks
	shoot = pygame.mixer.Sound("Data/Sound/Shoot.ogg")                  # Sound for normal energy shooting
	charging_e = pygame.mixer.Sound("Data/Sound/Charging_e.ogg")        # Sound when charging explosive wave

def terminate():            # save the current top score and close the game
	topScoreFile("save")
	pygame.quit()
	exit()

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

def displayScore():          # Displays the score, top score and level on the screen
	global score, topScore, level
	if level > 7: levelColor = RED
	elif level > 3: levelColor = YELLOW
	else: levelColor = GREEN
	score1Text, score1Rect = writeText("Score:", WHITE, 20, 10, 10, True)
	score2Text, score2Rect = writeText(str(score), WHITE, 20, score1Rect.right+5, 10, True)
	topScore1Text, topScore1Rect = writeText("Top Score:", WHITE, 20, 10, score1Rect.bottom+3, True)
	topScore2Text, topScore2Rect = writeText(str(topScore), YELLOW, 20, topScore1Rect.right+5, score1Rect.bottom+3, True)
	levelText1, levelRect1 = writeText("Level:", WHITE, 20, 10, topScore2Rect.bottom+3, True)
	levelText2, levelRect2 = writeText(str(level), levelColor, 28, levelRect1.right+5, topScore2Rect.bottom+3, True)
	levelRect2.centery = levelRect1.centery
	windowSurface.blit(score1Text, score1Rect)
	windowSurface.blit(score2Text, score2Rect)
	windowSurface.blit(topScore1Text, topScore1Rect)
	windowSurface.blit(topScore2Text, topScore2Rect)
	windowSurface.blit(levelText1, levelRect1)
	windowSurface.blit(levelText2, levelRect2)

def drawHealthBar(char):      #  health bar with current health left
	if char.type == "hero":
		barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (ENERGYBARW, ENERGYBARH))
		pygame.draw.rect(windowSurface, GREEN, (12, WINH - ENERGYBARH - 24, char.health[0]/(char.health[1]/MAXBARVALUE), ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(10, WINH - ENERGYBARH - 25, 0, 0))
	else:
		barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (round(ENERGYBARW+MAXBARVALUE/2), ENERGYBARH))
		pygame.draw.rect(windowSurface, GREEN, (WINW-char.health[0]/(char.health[1]/(1.5*MAXBARVALUE))-10, WINH - ENERGYBARH - 24, char.health[0]/(char.health[1]/(1.5*MAXBARVALUE)), ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(WINW-1.5*MAXBARVALUE-12, WINH - ENERGYBARH - 25, 0, 0))

def drawEnergyBar(char, manualDrain = 0):                     # draw energy bar with current amount of energy left in it
	char.energy[0] -= manualDrain           # drain given amount of energy from the character
	# show the energy left in different position and size according to the character's type
	if char.type == "hero":
		barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (ENERGYBARW, ENERGYBARH))
		pygame.draw.rect(windowSurface, RED, (12, WINH - 19, char.energy[0], ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(10, WINH - 20, 0, 0))
	else:
		barImg = pygame.transform.scale(pygame.image.load("Data/Image/Objects/Energy_bar.png"), (round(ENERGYBARW+MAXBARVALUE/2), ENERGYBARH))
		pygame.draw.rect(windowSurface, RED, (WINW-char.energy[0]/(char.energy[1]/(1.5*MAXBARVALUE))-10, WINH - 19, char.energy[0]/(char.energy[1]/(1.5*MAXBARVALUE)), ENERGYBARH-2))
		windowSurface.blit(barImg, pygame.Rect(WINW-1.5*MAXBARVALUE-12, WINH - 20, 0, 0))

	if not char.charging[0]:        # if kamehameha not charging
		if char.superSayan:         # if SS mode on
			if char.energy[0] > 0:       # if energy not zero
				char.energy[0] -= Energy.ENERGYPERSECOND        # drain energy in SS mode
		else:                       # is SS mode off
			if char.energy[0] < char.energy[1] and not char.charging[1]:           # if energy not full and the character isn't releasing a special attack
				if char.type == "hero":
					char.energy[0] += Energy.ENERGYPERSECOND            # increase the energy
				else:
					char.energy[0] += Energy.ENERGYPERSECOND/2            # increase the energy by slower than that of hero's
		if char.energy[0] < 0:
			char.energy[0] = 0

def pause(text, drawRect, x, y):                # pause the game
	global mouseDown
	pygame.mouse.set_visible(True)              # make mouse visible while paused
	while True:
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
	SOUND.boss_releasing.stop()
	SOUND.boss_charging.stop()
	SOUND.charging.stop()
	SOUND.blink.stop()
	SOUND.charging_e.stop()
	SOUND.shoot.stop()

def main():
	global time, score, mouseDown, dead, topScore, hero, level
	#### Start Page showing game instructions ####
	while True:
		pygame.mouse.set_visible(False)
		level = 1
		time = 1                    # set initial time to 1ssssss
		score = 0                # set initial score to 0
		Object.objects.clear()                        # make initial object empty
		Boss.boss.clear()                       # remove any boss from previous game
		topScore = topScoreFile("load")             # load top score from the 'topScore.txt' file
		mouseDown = False       # set supersayan and mouse chicked status to false
		dead = False            # keep track of if hero is dead
		Boss.moveSpeed = 2          # reset the movement speed of the boss
		playerTask = "None"
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
		hero = Character(goku)
		##### Game Starts Here ######
		while not dead:
			# if the hero's energy is finished and he isn't charging an attack
			if hero.energy[0] <= 0 and not hero.charging[0]:
				hero.superSayan = False          # turn off SS mode
			# turn of the SS music if SS mode is deactivated
			if not hero.superSayan:
				pygame.mixer.music.stop()

			Object().add(time)

			Background().animate()

			if hero.charging[1]:                    # if releasing energy after charging
				if hero.charging[2] == "k":         # if releasing kamehameha
					playerTask = Energy().kamehameha(hero)       # draw kamehameha image animation

			Object().move()
			displayScore()
			drawEnergyBar(hero)
			drawHealthBar(hero)
			hero.playerImage(playerTask)        # update player's image according to the current task
			Energy().move(hero)

			if not Boss.boss:       # if Boss.boss is an emtpy list
				time += 1                   # increase time by 1 per frame
			else:                   # if boss present
				for boss in Boss.boss:
					boss.BossAI(playerTask, hero)

			if hero.isDead():                        # check if hero dead
				dead = True
				if score > topScore:            # if score is higher than top score
					topScore = score            # make the score top score
				# update the health, energy and other status
				Background().animate()
				displayScore()
				drawEnergyBar(hero)
				drawHealthBar(hero)
				hero.playerImage(playerTask)
				if Boss.boss:           # if boss present, update them too
					for boss in Boss.boss:
						boss.playerImage()
						drawEnergyBar(boss)
						drawHealthBar(boss)
				break                           # break the while loop and go to end of the code

			hero.levelUp(score)     # levelup the hero according to the score

			# event handling
			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				if not (hero.charging[0] or hero.charging[1]):          # while hero isn't charging or releasing any attack
					if event.type == MOUSEBUTTONDOWN:
						# allowing shooting only if not charging
						mouseDown = True
					if event.type == MOUSEBUTTONUP:
						# stop shootin if mouse button released
						mouseDown = False
					if event.type == KEYDOWN:
						# Only allow pausing the game while not charging
						if event.key == ord("p"):
							hero.playerImage("None")        # without this, the player image will disapper while game is paused
							pause("Paused", False, -1, -1)
				if not hero.charging[1]:            # while not releasing
					if event.type == KEYDOWN:
						if event.key == ord("w"):
							hero.blink("up")
						elif event.key == ord("s"):
							hero.blink("down")
						elif event.key == ord("a") and "SS" in hero.abilities:
							hero.superSayan = not hero.superSayan
							if hero.superSayan:
								SOUND.goSS.play()
								pygame.mixer.music.play(-1, 0.0)
							playerTask = "None"
						elif event.key == K_SPACE and "kamehameha" in hero.abilities:
							if hero.energy[0] >= energyUsage["kamehameha"]:             # if energy is atleast 50
								hero.charging = [True, False, "k"]             # charging kamehameha
								stopAllSounds()
								SOUND.charging.play()
								drawEnergyBar(hero, energyUsage["kamehameha"])       # drain energy by 50
						elif event.key == ord("d") and "explosive wave" in hero.abilities:
							if hero.energy[0] >= energyUsage["explosive wave"]:             # if energy is full
								hero.charging = [True, False, "e"]             # charging
								stopAllSounds()
								SOUND.charging_e.play()
								drawEnergyBar(hero, energyUsage["explosive wave"])       # drain all the energy
						elif event.key == K_ESCAPE:
							terminate()
					if event.type == KEYUP:
						if hero.charging[0]:                # if charging
							if event.key == K_SPACE and hero.charging[2] == "k":    # if charging Kamehameha
								SOUND.charging.stop()       # stop the charging sound
								playerTask = "Release"
								hero.sMove["img"] = pygame.image.load("Data/Image/Hero/kamehameha.png")
								if hero.superSayan:                              # if Super Sayan mode is on
									# Double the kamehameha's damage value in SS mode
									hero.sMove["damage"] = 2*(Energy.KAMEHAMEHADMG+hero.chargeTime[0]+int(level/3))
								else:
									# Increase kamehameha's damage according to the time it was being charged
									hero.sMove["damage"] = Energy.KAMEHAMEHADMG+hero.chargeTime[0]+int(level/3)
								SOUND.releasing.play()      # play the kamehameha releasing sound
								hero.charging = [False, True, "k"]                # stop charging
							elif event.key == ord("d") and hero.charging[2] == "e":
								SOUND.charging_e.stop()       # stop the charging sound
								playerTask = "Release Wave"
								SOUND.releasing.play()      # play the explosive wave releasing sound
								Energy().explosiveWave(hero)       # draw explosive image animation
								hero.charging = [False, False, "n"]                # stop charging
								playerTask = "None"
								hero.chargeTime[1] = 2*FPS
								hero.chargeTime[0] = 1
					if event.type == MOUSEMOTION:
						hero.rect.centery = event.pos[1]   # move player Rect to current mouse position
			pygame.mouse.set_pos(hero.rect.center)
			if mouseDown:               # if mouse button pressed
				Energy().add(hero)            # add new energy in the screen
				playerTask = "Shoot"
			elif not mouseDown and not (hero.charging[0] and hero.charging[1]):                    # if mouse not pressed and the hero is neither charging nor releasing
				hero.attackRate[0] = 0                                                              # reset hero.attackRate[0]'s value
				playerTask = "None"
			if hero.charging[0]:                                                            # if charging
				hero.chargeTime[1] += 1
				if hero.chargeTime[1]%hero.chargeTime[2] == 0 and hero.chargeTime[0] != 4:
					hero.chargeTime[0] += 1
				mouseDown = False                                           # prevent shooting energy
				playerTask = "Charge"
				hero.drawEnergySphere()
			if hero.health[0] <= MAXBARVALUE:
				hero.health[0] += eval(hero.hpRegen)           # slowly increase health with time
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
