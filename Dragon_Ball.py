from sys import exit
from random import randint, choice, shuffle
from os import path, listdir
from math import sin, pi, cos

import pygame
from pygame.locals import *

pygame.init()

# Set up window and clock
WINW = 900
WINH = 500
windowSurface = pygame.display.set_mode((WINW, WINH))
transparentSurface = pygame.Surface((WINW, WINW))
transparentSurface = windowSurface.convert_alpha()
pygame.display.set_caption("Dragon Ball")
mainClock = pygame.time.Clock()
FPS = 55

WALLPAPER = pygame.transform.scale(pygame.image.load("Data/Image/Welcome.jpg"), (WINW, WINH))
GAMEOVER = pygame.transform.scale(pygame.image.load("Data/Image/Game_Over.png"), (250, 75))
B_SPACING = 20  # Spacing of buttons

# Set up colors
BGCOLOR = (80, 80, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
D_SILVER = (100, 100, 100)
YELLOW = (255, 255, 0)
RED = (200, 10, 10)
GREEN = (10, 150, 10)

# set up game constants
DEF_BARVALUE = 200
ENERGYBARW = WINW
ENERGYBARH = 10
BAR_IMG = dict(BLUE=pygame.image.load("Data/Image/Blue_bar.png"), RED=pygame.image.load("Data/Image/Red_bar.png"),
               GREEN=pygame.image.load("Data/Image/Green_bar.png"), YELLOW=pygame.image.load("Data/Image/Yellow_bar.png"))
DEFAULTATTACKPERIOD = 13  # this determines the interval (in terms of frames) between the release of energies
BUTTONW = 75
BUTTONH = 50


class Button:

	def __init__(self, image, ratio=1):
		self.default_img = pygame.image.load(image)
		self.img = pygame.transform.scale(self.default_img, (int(BUTTONW*ratio), int(BUTTONH*ratio)))
		self.rect = self.img.get_rect()

	def update_rect(self, ratio=None):
		# change the size of the button if new size ratio given
		if ratio is not None:
			self.img = pygame.transform.scale(self.default_img, (int(BUTTONW*ratio), int(BUTTONH*ratio)))
		self.rect = self.img.get_rect()

	def draw(self):
		windowSurface.blit(self.img, self.rect)

# default Buttons
START_B = Button("Data/Image/Button/Start.png")
OPTION_B = Button("Data/Image/Button/Option.png")
BACK_B = Button("Data/Image/Button/Back.png")
CLOSE_B = Button("Data/Image/Button/Close.png", 2/3)
CANCEL_B = Button("Data/Image/Button/Cancel.png", 2/3)

class Background:  # holds background components
	STARSIZE = (2, 8)
	STARSPEED = (2, 5)              # the 1st value is the ordinary star speed. The 2nd value is the star speed while fighting a boss
	img = pygame.image.load("Data/Image/Objects\star.jpg")
	stars = []

	def animate(self):  # Makes a background with stars moving left
		if not self.stars:
			self.stars += [{"rect": pygame.Rect(w, randint(0, WINH), 0, 0), "image": pygame.transform.scale(self.img, (randint(self.STARSIZE[0], self.STARSIZE[1]),)*2)} for w in range(0, WINW, 2)]

		if not Boss.boss: i = 0
		else: i = 1
		windowSurface.fill(BGCOLOR)
		self.stars.append({"rect": pygame.Rect(WINW, randint(0, WINH), 0, 0), "image": pygame.transform.scale(self.img, (randint(self.STARSIZE[0], self.STARSIZE[1]),)*2)})  # append the star's rect info and image in the 'stars' list
		for s in self.stars[:]:
			windowSurface.blit(s["image"], s["rect"])  # loops over every star info in the 'stars' list and draw them on the screen according to the rect and image value they hold
			s["rect"].move_ip(-self.STARSPEED[i], 0)  # move the current star to left
			if s["rect"].right < 0:  # check if the star's right edge has gone past the left edge of the screen
				self.stars.remove(s)  # remove the star if it has


class Object:  # manages game objects like meteor, comet and planets
	OBJMINSIZE = 25
	OBJMAXSIZE = 50
	OBJMINSPEED = 3
	OBJMAXSPEED = 7
	OBJECTRATE = 3
	objects = []  # Stores the rectangle info, speed, life and image data of all the objects (asteroids, comets and planets)
	PLANETRADIUS = 280
	PLANETSPEED = 1
	PLANETLIFE = 250
	asteroidImgs = [pygame.image.load("Data/Image/Objects/asteroid1.png"), pygame.image.load("Data/Image/Objects/asteroid2.png"),
                          pygame.image.load("Data/Image/Objects/asteroid3.png")]
	cometImg = pygame.image.load("Data/Image/Objects/comet.png")
	planetImg = pygame.image.load("Data/Image/Objects/Planet.png")

	def add(self, time):  # adds new object on the screen according to the time.
		if Boss.boss:  # if boss present
			# add no new object on the screen when fighting boss
			return
		else:  # if boss not present
			if time % 2000 == 0 and time != 0:  # add new boss at given time interval
				Boss(CHARACTERS[choice(["kid buu", "goku"])]).addBoss()  # add boss in the game
				return
		if time % 27 == 0:  # makes new asteoids on the screen in every 25 frames
			objectSize = randint(self.OBJMINSIZE, self.OBJMAXSIZE)
			# randomly chooose the asteroid image among the three asteroids
			objectImg = pygame.transform.scale(choice(self.asteroidImgs),
			                                   (objectSize, objectSize))
			self.objects.append(
				{"rect": pygame.Rect(WINW, randint(0, WINH - objectSize), objectSize, objectSize),
				 "speed": randint(self.OBJMINSPEED, self.OBJMAXSPEED),
				 "life": [objectSize + level * 30, objectSize + level * 30], "image": objectImg})
		if time % 100 == 0:  # makes new comets on the screen in every 100 frames
			n = int((time / 100) / 10)
			if n > 5:  # limit max number of comets made once to 5
				n = 5
			for i in range(n):  # Adds more comets simultaneously on the screen with time
				objectSize = randint(self.OBJMINSIZE, self.OBJMAXSIZE)
				objectImg = pygame.transform.scale(self.cometImg,
				                                   (objectSize, objectSize))
				self.objects.append(
					{"rect": pygame.Rect(WINW, randint(0, WINH - objectSize), objectSize, objectSize),
					 "speed": randint(self.OBJMINSPEED, self.OBJMAXSPEED),
					 "life": [objectSize + level * 50, objectSize + level * 50], "image": objectImg})
		if time % 1500 == 0:  # makes planets on the screen in every 1000 frames
			if (time / 1500) <= 3:  # the first three planets have relatively smaller radius and less life i.e easier to destroy
				self.objects.append({"rect": pygame.Rect(WINW, randint(int(WINH / 4), int(WINH / 3)), self.PLANETRADIUS + (5 * level), self.PLANETRADIUS + (5 * level)),
				"speed": self.PLANETSPEED, "life": [self.PLANETLIFE + level * 60, self.PLANETLIFE + level * 60],
				"image": pygame.transform.scale(self.planetImg, ((5 * level) + self.PLANETRADIUS, (5 * level) + self.PLANETRADIUS))})
			else:  # After the third planet, planets have large radius and more life i.e harder to destroy
				self.objects.append({"rect": pygame.Rect(WINW, randint(int(WINH / 4), int(WINH / 3)), self.PLANETRADIUS + (5 * level),
				                                         self.PLANETRADIUS + (5 * level)), "speed": self.PLANETSPEED, "life": [2 * self.PLANETLIFE + level * 60, 2 * self.PLANETLIFE + level * 60],
				"image": pygame.transform.scale(self.planetImg, (self.PLANETRADIUS + (5 * level), self.PLANETRADIUS + (5 * level)))})

	def move(self, char):  # Moves the objects (asteroids, comets and planets) to left
		if len(self.objects) == 0: return 	# get out of this function (method) as got no object to move
		for o in self.objects[:]:
			o["rect"].move_ip(-o["speed"], 0)  # move object to left

			if char.type == "hero":  # for hero, check if he collided with any object and if yes, check if his hp <= 0
				if char.rect.colliderect(o["rect"]):  # if got hit
					if char.blocking[0]: char.health[0] -= o["life"][1]*char.blocking[1]  # take % of the damage while blocking
					else: char.health[0] -= o["life"][1]  # take full damage in normal mode
					self.objects.remove(o)
			if char.health[0] <= 0: char.health[0] = 0
			windowSurface.blit(o["image"], o["rect"])


class Energy:  # manages all sort of energy moves in the game
	ENERGYPERSECOND = 1
	ENERGYSPEED = 13 # horizontal speed and vertical speed
	cps = 3

	def add(self, char, task):  # Adds new energy dictionary to the list energy
		if char.attackRate[0] % char.attackRate[1] == 0:  # if char.attackRate[0] is multiple of char.attackRate[0]
			# choose energy blast's image when transformed mode is on
			if char.transform:
				energyImg = pygame.transform.scale(char.eImgs[1], char.eSize)
				x = 2  # x holds the integer value that will increase energy damage i.e make damage double if supersayan
			# choose energy blast's image when super sayan mode is off
			else:
				energyImg = pygame.transform.scale(char.eImgs[0], char.eSize)
				x = 1  # make no change in energy's dame value if super sayan mode is off
			energyRect = energyImg.get_rect()  # get rect around the energy image
			energyRect.centery = char.rect.top + char.rect.width*char.ePos[0]
			if char.type == "hero":
				energyRect.left = char.rect.right - 10  # set energy's left side to hero's right side
			else:
				energyRect.right = char.rect.left + 10 # set energy's right side to boss' left side

			SOUND.shoot.play()  # play shoot sound
			char.energies.append({"rect": energyRect, "image": pygame.transform.flip(energyImg, char.type != "hero", False), "damage": x * char.eDamage, "pos" : 0, "amp" : choice([-1, 1])*4})  # add new energy
			if task[1] == 1: task[1] = 2
			else: task[1] = 1
		char.attackRate[0] += 1  # increase char.attackRate[0]'s value

	def move(self, char):  # move the energies forward
		global score, dead
		for e in char.energies[:]:
			# move energy like a sine wave
			e["pos"] = int(e["amp"]*sin(self.cps*2*pi*e["rect"].left/WINW))       # update the displacement of the energy according to the horizontal position of the energy in the screen
			if char.type == "hero":  # move hero's energy
				e["rect"].move_ip(self.ENERGYSPEED, e["pos"])        # move energy horizontally as well as vertically
				if e["rect"].left >= WINW:
					char.energies.remove(e)  # remove the energy that went past the right side of the window
					continue  # go back to check another energy
				for o in Object.objects[:]:
					if not e: continue  # if the current energy is already removed, don't continue below
					if e["rect"].colliderect(o["rect"]):  # check if the current object collides with any energy blast on the screen
						o["life"][0] -= e["damage"]  # reduce object's health
						try:
							char.energies.remove(e)  # remove the energy blast that collided
						except ValueError:
							pass  # Sometime ValueError occurs when e is not found in char.energies asit might already be deleted
						if o["life"][0] <= 0:  # if the life of the object is zero or less
							score += o["life"][1]  # increase the score by the value of life of the object
							Object.objects.remove(o)  # then remove the object which was destroyed by the energy blast
				for boss in Boss.boss:
					try:
						if e["rect"].colliderect(boss.rect):
							if boss.charging[0]:
								boss.charging[0] = False
								boss.sMove["sound"][0].stop()
							if boss.blocking[0]: boss.health[0] -= e["damage"]*boss.blocking[1] # character takes % of full damage while blocking
							else: boss.health[0] -= e["damage"]
							if boss.health[0] < 0: boss.health[0] = 0
							try:
								char.energies.remove(e)  # remove the energy blast that collided
							except ValueError:
								pass
					except AttributeError:
						pass  # Attribute error occurs when the boss is created but the boss.rect isn't installized yet
			else:  # move boss' energies
				for o in Object.objects[:]:
					if not e: continue  # if the current energy is already removed, don't continue below
					if e["rect"].colliderect(o["rect"]):  # check if the current object collides with any energy blast on the screen
						o["life"][0] -= e["damage"]
						try:
							char.energies.remove(e)  # remove the energy blast that collided
						except ValueError:
							pass  # Sometime ValueError occurs when e is not found in char.energies asit might already be deleted
						if o["life"][0] <= 0:  # if the life of the object is zero or less
							Object.objects.remove(o)  # then remove the object which was destroyed by the energy blast
				e["rect"].move_ip(-(self.ENERGYSPEED), e["pos"])
				if self.collides(e, hero.energies):
					if e in char.energies: char.energies.remove(e)
					continue  # go for another energy
				if e["rect"].colliderect(hero.rect):
					if hero.blocking[0]: hero.health[0] -= e["damage"]*hero.blocking[1]
					else: hero.health[0] -= e["damage"]
					if hero.charging[0]:
						hero.charging[0] = False
						hero.sMove["sound"][0].stop()
					if hero.health[0] < 0:
						hero.health[0] = 0
						dead = True
					if e:
						char.energies.remove(e)  # remove the energy blast that collided if aleardy not removed
						continue
				if e["rect"].right <= 0:
					try:
						char.energies.remove(e)
					except:
						continue
			# if the current energy isn't removed, draw it
			if e: windowSurface.blit(e["image"], e["rect"])

	def collides(self, e1, energies, dmg = 0):  # checks if energy e1 collides with other energies
		for e in energies[:]:
			if e1["rect"].colliderect(e["rect"]):
				if "hp" in list(e1.keys()):
					e1["hp"] -= dmg
				energies.remove(e)
				return True
		return False

	def circularCollision(self, skill1, skill2):
		# If both are circles, check if their rect collide.
		# If both rects collide, check if the distance between the centers of the rectangles
		# is less or equal to the sum of their radius. If less or equal, the circles collide, else not.
		if skill1["type"][1] == skill2["type"][1] == "ball":
			if skill1["rect"].colliderect(skill2["rect"]):
				# d = sq.rt((x2-x1)^2 + (y2-y1)^2)
				distance = ((skill1["rect"].centerx - skill2["rect"].centerx)**2 + (skill1["rect"].centery - skill2["rect"].centery)**2)**(1/2)
				if distance <= sum([(skill1["rect"].width + skill2["rect"].width)/2]): return True
			return False
		# if only one skill is a circle
		elif skill1["type"][1] == "ball" and skill2["type"][1] != "ball":
			r = skill1["rect"].width/2 # radius of the circle
			# calculates 16 points at the circumference of the circle. Check if any of the points intercept with the rectangular skill
			# 16 points at circle's circumference and its center
			points = [(p[0]*d[0], p[1]*d[1]) for d in [(1, 1), (-1, 1), (-1, -1), (1, -1)]
			          for p in [(round(r*cos(x*pi/180)), round(r*sin(x*pi/180))) for x in (0, 30, 45, 60)]] + [(0, 0)]
			actual_points = [(skill1["rect"].centerx + p[0], skill1["rect"].centery + p[1]) for p in points]
			if any(skill2["rect"].collidepoint(p) for p in actual_points): return True   # if any point of the circle collides with the other's rectangle
			return False
		# if both are rectangles not circles
		elif "ball" not in [skill1["type"][1], skill1["type"][1]]:
			if skill1["rect"].colliderect(skill2["rect"]): return True
			return False

	def trackingSystem(self, rect1, rect2, speed):
		# tracks the vertical position of rect1 and moves the rect2 vertically to keep it straight to rect1
		if rect2.centery < rect1.centery:  # if the energyball is above the boss
			rect2.centery += round(speed)  # bring it down
		elif rect2.centery > rect1.centery:  # if the energy ball is below the boss
			rect2.centery -= round(speed)  # bring it up
		return rect2

	def beam(self, char):  # shoots Kamehameha that does huge damage in the line of release
		global score
		if char.type == "hero":
			# set the beam's left side equal to the player's right side so that it sees to come out from the hand and moves right
			char.sMove["rect"].left = char.rect.right
		else:
			# set the beam's right side equal to the player's left side so that it sees to come out from the hand and moves left
			char.sMove["rect"].right = char.rect.left

		char.sMove["rect"].height = char.rect.height + char.chargeTime[0]*18  # set its thickness aaccording to the charge time
		char.sMove["rect"].centery = char.rect.centery  # align the beam beam so that it emerges from the mid of the player
		beamImg = pygame.transform.scale(char.sMove["img"], (char.sMove["rect"].width, char.sMove["rect"].height))  # set beam's image to current KAMEHAMEHA["rect'}'s width and height

		if not char.sMove["collide"]: char.sMove["rect"].width += self.ENERGYSPEED * 3  # increase Kamehameha's length
		windowSurface.blit(beamImg, char.sMove["rect"])  # draw beam in its current position on the screen

		if char.type == "hero":
			for o in Object.objects[:]:
				if char.sMove["rect"].colliderect(o["rect"]):  # check if the current object collided with beam
					o["life"][0] -= char.sMove["damage"]  # subtract life is yes
					if o["life"][0] <= 0:  # check if objects life is zero or less
						score += o["life"][1]  # increase score
						Object.objects.remove(o)  # then remove the object
			for boss in Boss.boss:  # loops over all bosses
				if boss:  # if boss present
					if self.collides(char.sMove, boss.energies, boss.eDamage):  # this will check if beam collides with any enemy energies and deletes them
						pass
					try:
						if char.sMove["rect"].colliderect(boss.rect) and not char.sMove["collide"]:  # if current boss collides with beam,
							if boss.blocking[0]: boss.health[0] -= char.sMove["damage"]*boss.blocking[1]
							else: boss.health[0] -= char.sMove["damage"]
							if boss.charging[0]:
								boss.charging[0] = False
								boss.sMove["sound"][0].stop()
							if boss.health[0] <= 0: boss.health[0] = 0
					except AttributeError:
						pass  # Attribute error arise if the boss is added but its rectangle isn't instalized yet
			if char.sMove["rect"].right >= WINW + FPS*self.ENERGYSPEED*1.5 or char.sMove["hp"] <= 0:
				if Boss.boss: char.sMove["collide"] = Boss.boss[0].sMove["collide"] = False
				# stop the releasing sound after beam is over
				char.sMove["sound"][1].stop()
				# set these values back to default
				char.charging = [False, False, "n"]
				char.chargeTime[1] = char.chargeTime[2]
				char.chargeTime[0] = 1
				char.sMove["rect"] = pygame.Rect(-50, 0, 0, 0)  # reset the rectangle
				return "None"
			else:
				return "Release"

		else: # if boss
			if self.collides(char.sMove, hero.energies, hero.eDamage): pass
			if hero.charging[1]:
				if self.circularCollision(hero.sMove, char.sMove):
					hero.sMove["hp"] -= char.sMove["damage"]
					char.sMove["hp"] -= hero.sMove["damage"]
					char.sMove["collide"] = hero.sMove["collide"] = True
			if char.sMove["rect"].colliderect(hero.rect) and not char.sMove["collide"]:
				if hero.blocking[0]: hero.health[0] -= char.sMove["damage"]
				else: hero.health[0] -= char.sMove["damage"]
				if hero.charging[0]:
					hero.charging[0] = False
					hero.sMove["sound"][0].stop()
				if hero.health[0] < 0: hero.health[0] = 0
			if char.sMove["rect"].left < -FPS*self.ENERGYSPEED*1.5 or char.sMove["hp"] <= 0:
				char.sMove["collide"] = hero.sMove["collide"] = False
				# stop the releasing sound after beam is over
				char.sMove["sound"][1].stop()
				char.charging = [False, False, "n"]
				char.chargeTime[1] = char.chargeTime[2]
				char.chargeTime[0] = 1
				char.sMove["rect"] = pygame.Rect(WINW+50, 0, 0, 0)  # reset the rectangle

	def explosiveWave(self, char):  # shoots an explosive wave that damages (relatively small) everything on the screen
		global score, time, topScore, dead
		MAXRADIUS = 40
		wave = [dict(center=(randint(0, WINW), randint(0, WINH)), radius=randint(0, 15)) for x in range((char.chargeTime[0] + 1) * 40)]
		if char.isDead():  # check if player is dead
			dead = True
			if score > topScore:  # if score is higher than top score
				topScore = score  # make the score top score
			return  # get out of this function
		while wave != []:
			transparentSurface.fill((0, 0, 0, 0))
			windowSurface.fill(BGCOLOR)
			for s in Background().stars:
				windowSurface.blit(s["image"], s["rect"])
			if char.type == "hero":
				for o in Object.objects[:]:
					windowSurface.blit(o["image"], o["rect"])
					o["life"][0] -= char.sMove["damage"]
					if o["life"][0] < 0:
						score += o["life"][1]  # increase score
						Object.objects.remove(o)
				# draw all the energies of all bosses
				for boss in Boss.boss:
					if boss:  # if boss present
						try:
							# draw current boss on the screen
							windowSurface.blit(boss.Img, boss.rect)
						except AttributeError:
							pass  # if boss is added but its rect isn't instalized yet
						# draw the boss' health and energy bars
						draw_bar(boss)
						if boss.energies: boss.energies.clear()  # if there is any boss' energy, remove all the energies to show that they were destroyed by the explosive wave
						# reduce boss' health
						if boss.blocking[0]: boss.health[0] -= char.sMove["damage"]*boss.blocking[1]
						else: boss.health[0] -= char.sMove["damage"]
						if boss.health[0] < 0: boss.health[0] = 0
			else:  # if the char is boss,
				for o in Object.objects[:]:
					windowSurface.blit(o["image"], o["rect"])
				# draw hero on the screen
				windowSurface.blit(hero.Img, hero.rect)
				# draw the hero's health and energy bars
				draw_bar(hero)
				if hero.energies: hero.energies.clear()  # if any hero's energy present, remove all of them
				# reduce hero's health
				if hero.blocking[0]: hero.health[0] -= char.sMove["damage"]*hero.blocking[1]
				else: hero.health[0] -= char.sMove["damage"]
				if hero.health[0] < 0: hero.health[0] = 0
			for e in char.energies: windowSurface.blit(e["image"], e["rect"])
			for w in wave[:]:
				w["radius"] += 1
				if char.transform:
					pygame.draw.circle(transparentSurface, (w["radius"] * 5, w["radius"] * 5, 0, w["radius"] * 2),
					                   w["center"], w["radius"])  # draw a yellow transparent circle
				else:
					pygame.draw.circle(transparentSurface, (w["radius"] * 5, 0, 0, w["radius"] * 2), w["center"], w["radius"])  # draw a red transparent circle
				if w["radius"] > MAXRADIUS:
					wave.remove(w)
			char.playerImage(["Release Wave", char.charging[2]])
			display_score()  # keep displaying the score
			draw_bar(char)  # draw no energy while explosive wave is progressing to the right side
			windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))  # draw the transparent over the windowSurface
			windowSurface.blit(char.Img, char.rect)
			pygame.display.update()
			mainClock.tick(FPS-20)
		char.sMove["sound"][1].stop()
		char.charging = [False, False, "n"]

	def energyBallAnimate(self, char):  # animates the grow of energyBall as it gets charged
		global score
		char.sMove["rect"].width = char.sMove["rect"].height = 100*(char.chargeTime[0])**(2/3) # increase energyball's radius with charge time
		char.sMove["rect"].bottom = char.rect.top  # place the energyball above the player
		char.sMove["rect"].centerx = char.rect.centerx
		windowSurface.blit(pygame.transform.scale(char.sMove["img"], char.sMove["rect"].size), char.sMove["rect"])

	def energyBall(self, char):  # throws a tracking and devastating energy ball that damages everything in its path
		global score
		speed = (self.ENERGYSPEED  - char.chargeTime[0])
		if char.type == "hero":
			if Boss.boss:
				boss = Boss.boss[0]
				if not char.sMove["collide"]:
					char.sMove["rect"] = self.trackingSystem(boss.rect, char.sMove["rect"], speed-3)
			else:
				char.sMove["rect"] = self.trackingSystem(char.rect, char.sMove["rect"], speed-3)
			# for hero, move the energyball to right
			if not char.sMove["collide"]: char.sMove["rect"].left += speed # more charge time = bigger energy ball = slower speed

			if char.sMove["rect"].left > WINW + 50 or char.sMove["hp"] <= 0:
				# set false to energy releasing status if the ebenrgyball went past the right side
				if Boss.boss: char.sMove["collide"] = Boss.boss[0].sMove["collide"] = False
				char.charging = [False, False, "n"]
				char.sMove["rect"] = pygame.Rect(WINW, 2*WINH, 0, 0)
				char.sMove["sound"][1].stop()
		else:  # if the char is a boss

			# for boss, move the energyball to left if the energy isn't colliding with another energy
			if not char.sMove["collide"]:
				char.sMove["rect"] = self.trackingSystem(hero.rect, char.sMove["rect"], speed-3)
				char.sMove["rect"].right -= speed

			if char.sMove["rect"].right < -50 or char.sMove["hp"] <= 0:
				# set false to energy releasing status if the ebenrgyball went past the left side
				char.sMove["collide"] = hero.sMove["collide"] = False
				char.charging = [False, False, "n"]
				char.sMove["rect"] = pygame.Rect(WINW, -WINH, 0, 0)
				char.sMove["sound"][1].stop()
		# damage anything that comes in contact
		for o in Object.objects[:]:
			if o["rect"].colliderect(char.sMove["rect"]):
				o["life"][0] -= char.sMove["damage"]
				if o["life"][0] <= 0:
					if char.type == "hero":
						score += o["life"][1]
					Object.objects.remove(o)
		# collide and destroy opponent's energies
		if char.type == "hero":
			for boss in Boss.boss:
				if self.collides(char.sMove, boss.energies, boss.eDamage): pass  # if energy ball collides with any energy, it will remove them
				if char.sMove["rect"].colliderect(boss.rect) and not char.sMove["collide"]:
					if boss.blocking[0]: boss.health[0] -= char.sMove["damage"]*boss.blocking[1]
					else: boss.health[0] -= char.sMove["damage"]
					if boss.charging[0]:
						boss.charging[0] = False
						boss.sMove["sound"][0].stop()
				if boss.health[0] < 0: boss.health[0] = 0
		else:
			if self.collides(char.sMove, hero.energies, hero.eDamage): pass
			if hero.charging[1]:
				if self.circularCollision(char.sMove, hero.sMove):
					hero.sMove["hp"] -= char.sMove["damage"]
					char.sMove["hp"] -= hero.sMove["damage"]
					char.sMove["collide"] = hero.sMove["collide"] = True
			if char.sMove["rect"].colliderect(hero.rect) and not char.sMove["collide"]:
				if hero.blocking[0]: hero.health[0] -= char.sMove["damage"]*hero.blocking[1]
				else: hero.health[0] -= char.sMove["damage"]
				if hero.charging[0]:
					hero.charging[0] = False
					hero.sMove["sound"][0].stop()
			if hero.health[0] < 0: hero.health[0] = 0
		windowSurface.blit(pygame.transform.scale(char.sMove["img"], char.sMove["rect"].size), char.sMove["rect"])


class Character:

	def __init__(self, char):
		self.name = char["name"]
		self.type = char["type"]  # type of character
		self.size = char["size"][:]
		self.health = char["health"][:]
		self.eDamage = char["eDamage"]
		self.skills = [self.convertSkill(skill) for skill in char["skills"]]  # a list where they have their skills stored
		self.hpRegen = char["hpRegen"]  # hp regeneration value
		self.energy = char["energy"][:]  # energy to use special moves
		self.eRegen = char["eRegen"]
		self.eImgs = char["eImgs"]
		self.eSize = char["eSize"]
		self.energies = []  # stores the rectangle information and the image data of each energy as a dictionary in this list
		self.transform = False  # super sayan mode
		self.charging = [False, False, "n"]  # tells if charging some special moves
		self.abilities = char["abilities"][:]  # available abilities for character
		self.chargeTime = [1, FPS, FPS]  # chargeTime[0] (defaults to 1) holds the time for which energy was charged. chargeTime[1] and chargeTime[2] are used to deduce the chargeTime[0]
		self.attackRate = [0, DEFAULTATTACKPERIOD]  # rate at which ordinary energies release
		self.sMove = {"rect": pygame.Rect(0, 0, 0, 0), "damage": 0, "img": None, "hp" : 0, "sound" : [], "collide": False, "type" : []}  # holds empty slot to later use for special moves (attacks)
		self.rect = pygame.Rect((0, 0), self.size)  # get rectangle of current player
		self.rect.left = WINW - self.rect.width
		self.rect.centery = randint(round(self.rect.width / 2), round(WINH - self.rect.width / 2))  # place the player at random vertical position
		self.blocking = char["blocking"][:]
		self.ePos = char["ePos"][:]

	def isDead(self):  # check if player got hit by any object
		if self.health[0] <= 0:
			self.health[0] = 0
			return True  # return True
		return False  # else return False

	def blink(self, dir):  # makes the player blink up or down
		BLINKDISTANCE = self.size[1] * 2
		SOUND.blink.play()  # play the blink sound
		if self.transform:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/SS_Blink.png".format(self.name)), self.size)
		else:
			blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/{}/Blink.png".format(self.name)), self.size)
		if dir == "down":  # if blink down
			move = BLINKDISTANCE
		elif dir == "up":  # if blink up
			move = -BLINKDISTANCE
		windowSurface.blit(blinkImg, self.rect)  # make the blink image in initial position
		finalRect = self.rect.move(0, move)  # move the player rect to final position
		if finalRect.bottom > WINH:  # if final position below the bottom of window
			finalRect.bottom = WINH
		if finalRect.top < 0:  # if final position above the top of window
			finalRect.top = 0
		if self.type == "hero":
			pygame.mouse.set_pos(finalRect.center)  # move mouse to hero's final position's center
			if self.charging[0]:  # if hero is charging an attack while blinking, draw the energy sphere
				self.drawEnergySphere()
		self.rect = finalRect  # set player rect value to final rect
		windowSurface.blit(blinkImg, finalRect)  # make the blink image in final position
		pygame.display.update()  # update the change
		pygame.time.wait(40)  # make the screen freeze for short time while blinking

	def convertSkill(self, skill):
		# converts the skill = [skill 1 name, . . . . . ,skill n name] into skill = [skill 1 dict, . . . . . , skill n dict]
		# each skill dict contains all the data about that skill
		VALID_SKILLS = list(SKILLS.keys())

		if skill.lower() in VALID_SKILLS:
			return SKILLS[skill.lower()].copy()
		else:
			pause("Char : %s, Invalid Skill: %s"% (self.name, skill))
			terminate()

	def playerImage(self, task=["None", None]):  # return player's image according to the current task it is doing
		# choose among the transformed form's images is super sayan mode on
		if self.transform:
			if task[0] == "None":
				img = pygame.image.load("Data/Image/{}/SS_Normal.png".format(self.name))
			elif task[0] == "Shoot" and task[1] in [1, 2]:
				img = pygame.image.load("Data/Image/{}/SS_Shooting{}.png".format(self.name, str(task[1])))
			elif task[0] == "Charge":
				img = pygame.image.load("Data/Image/{}/SS_Charging.png".format(self.name))
			elif task[0] == "Block":
				img = pygame.image.load("Data/Image/{}/SS_Blocking.png".format(self.name))
			elif task[0] == "Release":
				img = pygame.image.load("Data/Image/{}/SS_Releasing.png".format(self.name))
			elif task[0] == "Release Wave":
				img = pygame.image.load("Data/Image/{}/SS_Releasing_e.png".format(self.name))
		# choose among the normal images if super sayan mode off
		else:
			if task[0] == "None":
				img = pygame.image.load("Data/Image/{}/Normal.png".format(self.name))
			elif task[0] == "Shoot" and task[1] in [1, 2]:
				img = pygame.image.load("Data/Image/{}/Shooting{}.png".format(self.name, str(task[1])))
			elif task == ["Shoot", 0]:
				img = pygame.image.load("Data/Image/{}/Normal.png".format(self.name))
			elif task[0] == "Charge":
				img = pygame.image.load("Data/Image/{}/Charging.png".format(self.name))
			elif task[0] == "Block":
				img = pygame.image.load("Data/Image/{}/Blocking.png".format(self.name))
			elif task[0] == "Release":
				img = pygame.image.load("Data/Image/{}/Releasing.png".format(self.name))
			elif task[0] == "Release Wave":
				img = pygame.image.load("Data/Image/{}/Releasing_e.png".format(self.name))
		self.Img = pygame.transform.flip(pygame.transform.scale(img, self.size), self.type != "hero", False)
		windowSurface.blit(self.Img, self.rect)

	def drawEnergySphere(self):
		# add a circular energy field while charging
		if self.type == "hero":
			CENTER = (round(self.rect.left + self.rect.width * self.ePos[1][0]), round(self.rect.top + self.rect.height * self.ePos[1][1]))  # set the circular energy field's center

		else:
			CENTER = (round(self.rect.left + self.rect.width * (1-self.ePos[1][0])), round(self.rect.top + self.rect.height * self.ePos[1][1]))
		radius = (5 - self.chargeTime[0]) * 10  # set the radius of the fiels which decreses with chargetime
		transparentSurface.fill((0, 0, 0, 0))  # fill transparentSurface with an invisible colour
		if self.transform:
			pygame.draw.circle(transparentSurface, (255, 255, 0, self.chargeTime[0]*20), CENTER, radius)  # draw a yellow transparent circle
		else:
			pygame.draw.circle(transparentSurface, (255, 255, 255, self.chargeTime[0]*20), CENTER, radius)  # draw a red transparent circle
		windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))  # draw the transparent over the windowSurface

	def performTask(self, task):  # performs given task
		if task[0] == "None":
			pass
		elif task[0] == "Shoot":
			Energy().add(self, task)
		elif task[0] == "Blink":
			if self.dir[0] == "none": self.dir[0] = choice(["up", "down"])
			self.blink(self.dir[0])
		elif task[0] == "Release":
			self.sMove["sound"][0].stop()
			self.sMove["sound"][1].play()
			if self.charging[2] == "explosive wave":
				Energy().explosiveWave(self)
			elif self.charging[2] in [s["name"] for s in SKILLS.values() if s["type"] == ("Active", "beam")]:
				Energy().beam(self)
			elif self.charging[2] in [s["name"] for s in SKILLS.values() if s["type"] == ("Active", "ball")]:
				Energy().energyBall(self)
			if not self.charging[1] and self.type != "hero":
				self.sMove["sound"][1].stop()
				self.task = [["None", None], 1]  # End the task for Boss

	def prepSkill(self, i, keyType):
		# prepSkill if not same as performTask. prepSkill is used only to prepare Skill 1, Skill 2 and Skill 3 of player
		# whereas performTask later performs the skill prepared by prepSkill
		if keyType == "down":  # when key is pressed
			if self.skills[i]["type"][0] == "Active": # if the skill is not a passive skill i.e activates only when clicked
				if self.energy[0] >= self.skills[i]["eUsage"]:  # if energy is enough
					self.energy[0] -= self.skills[i]["eUsage"]  # drain energy
					self.sMove["img"] = self.skills[i]["image"]  # load skill image
					self.sMove["sound"] = self.skills[i]["sound"][self.name] # load skill sounds
					self.sMove["type"] = self.skills[i]["type"] # load skill type
					self.sMove["hp"] = self.skills[i]["hp"][self.skills[i]["level"]] # load skill's hp
					self.sMove["collide"] = False # set skill's collision status to False (default)

					if self.skills[i]["chargable"]: # if the skill is a chargable skill
						self.charging = [True, False, self.skills[i]["name"]]  # charge skill
						self.chargeTime = [1, self.chargeTime[2], self.chargeTime[2]]
						stopAllSounds()
						# play the charging sound of the skill
						self.sMove["sound"][0].play()
					else: # if the skill is not chargable, perform it immediately
						self.sMove["damage"] = self.skills[i]["damage"][self.skills[i]["level"]] # set skill's damage according to the skill's current level
						self.performTask(hero.skills[i]["name"]) # perform the skill
		elif keyType == "up": # when pressed key is released
			# Increase skill's's damage according to the time it was being charged
			self.sMove["damage"] = self.skills[i]["damage"][self.skills[i]["level"]] + self.chargeTime[0]/4
			self.charging = [False, True, self.skills[i]["name"]]  # stop charging
			self.sMove["sound"][0].stop() # stop charging sound
			self.sMove["sound"][1].play() # play releasing sound

			if self.charging[2] in ["explosive wave"]: return "Release Wave" # explosive wave skill works differently than other chargable skills
			else: return ["Release", self.charging[2]]


class Boss(Character):  # creates and manages Boss
	boss = []  # holds info about current boss
	moveSpeed = 2.5
	direction = dict(up=-moveSpeed, down=moveSpeed, none=0)
	dir = ["none", randint(1, 2) * FPS]  # the dir list holds the direction of motion and the time period in that direction
	task = [["None", None], randint(1, 3) * FPS]  # the task holds the current boss' task, type of task and the time period to execute that task

	def addBoss(self):  # add a boss
		global level
		self.boss.append(self)
		# every time a boss is added, the moveSpeed is increased a little bit
		if self.moveSpeed < 5:
			self.moveSpeed += round((level - 1) / 50, 2)

	def BossAI(self, playerTask, hero):  # AI for boss
		global score, time, level
		# draw health and energy bars
		draw_bar(self)
		# if boss is dead
		if self.isDead():
			# stop boss' music if dead
			for skill in self.skills:
				for sound in skill["sound"][self.name]:
					sound.stop()
			if self.energies:  # if any energy is still present on the screen
				Energy().move(self)  # move boss' energies till they pass across the screen
			else:  # if no energy present on the screen
				score += int(0.5 * self.health[1])  # increase the score by half value of the boss' total hp
				level += 1  # increase the level
				# increase hero's hp and energy by adding dying boss' health and energy
				hero.health = [h + self.health[1] for h in hero.health]
				hero.energy = [e + self.energy[1] for e in hero.energy]
				self.boss.remove(self)  # remove the dead boss
			time += 1
		else:  # if boss alive
			Energy().move(self)  # move boss' energies
			# if charging status is fasle but current task is still Charge, it means charging was canceled by hero's attack
			# so set it back to none
			if not self.charging[0] and self.task[0][0] == "Charge":
				self.task = [["None", None], 0]
			# if the player is in approximately same height to boss and the boss is not moving while the player shoots,
			# then get new direction instruction. and move away the boss Note: new dir might be "none" again in which case the boss will not move and get hit by energy
			if self.rect.top < hero.rect.centery < self.rect.bottom and playerTask[0] == "Shoot" and self.dir[0] == "none":
				self.dir = [choice(["up", "down", "none"]), randint(1, 3) * FPS]
			# choose new task if timer for current task is out and boss is neither charing nor releasing any special energy
			if self.task[1] == 0 and self.task[0][0] != "Release" and not self.charging[0]:
				if self.task[0][0] == "Block": self.blocking[0] = False # if blocking ends, set it's status to False

				while True:
					self.task = [[choice(self.abilities), None], randint(1, 2) * FPS]  # perform each task for only 1 or 2 seconds
					if self.task[0][0] == "Charge":
						self.chargeTime[0], self.chargeTime[1] = randint(1, 4),  self.chargeTime[2]
						self.task[1] = 5+(self.chargeTime[0]-1) * FPS  # if the current task is charge, charge the special attack in the time range 1-4
						self.charging = [True, False, choice(self.skills)]
						# if the choosen skill is a passive skill, choose again until active skill is chosen
						while self.charging[2]["type"] == "Passive" : self.charging[2] = choice(self.skills)

						if self.energy[0] >= self.charging[2]["eUsage"]:  # if energy is sufficient for the current special attack
							self.energy[0] -= self.charging[2]["eUsage"]  # drain required energy
							self.sMove["img"] = self.charging[2]["image"]
							self.sMove["sound"] = self.charging[2]["sound"][self.name]
							self.sMove["type"] = self.charging[2]["type"]
							self.sMove["hp"] = self.charging[2]["hp"][self.charging[2]["level"]]
							self.sMove["collide"] = False
							self.sMove["damage"] = self.charging[2]["damage"][self.charging[2]["level"]] + (self.chargeTime[0]/4)
							self.charging[2] = self.task[0][1] = self.charging[2]["name"]
							self.chargeTime[0] = 1
							# play sound for charging an energy and set required image and damage for them
							self.sMove["sound"][0].play()
							if self.transform:  # if Super Sayan mode is on, double the damage
								self.sMove["damage"] *= 2
							break  # break the while loop
						else:
							self.charging = [False, False, "n"]  # change the charging status to default if energy not sufficient
					else:  # if other tasks chosen other than Charge
						if self.task[0][0] == "Shoot": self.task[0][1] = 1
						elif self.task[0][0] == "Block": self.blocking[0] = True
						elif self.task[0][0] == "Blink": self.task[1] = 1  # blink only once in one frame
						break

			if self.charging[0]:
				self.chargeTime[1] += 1
				if self.chargeTime[1] % self.chargeTime[2] == 0 and self.chargeTime[0] != 4: self.chargeTime[0] += 1
				if self.charging[2] in [s["name"] for s in SKILLS.values() if s["type"] == ("Active", "ball")]:
					# play the animation if energyball is charging
					Energy().energyBallAnimate(self)

			if self.charging[0] and self.charging[2] in ["kamehameha", "explosive wave"]: self.drawEnergySphere()  # draw energy sphere

			if self.task[0][0] == "Charge" and self.task[1] == 1:
				self.task[0][0] = "Release"
				self.charging[0], self.charging[1] = False, True  # when releasing, set charging to False and Releasing to True
			# perform current the task
			self.performTask(self.task[0])
			self.task[1] -= 1  # reduce the task period by one frame
			# move the boss up, down or none only if the player isn't releasing energy
			if not (self.charging[1] or self.blocking[0]):
				self.rect.move_ip(0, self.direction[self.dir[0]])
			self.dir[1] -= 1  # reduce the direction period by one frame
			if self.rect.top <= 0:
				self.rect.top = 0
				self.dir[1] = 0  # if the Boss reaches top, renew the direction time period
			if self.rect.bottom >= WINH:
				self.rect.bottom = WINH
				self.dir[1] = 0  # if the Boss reaches bottom, renew the direction time period
			if self.dir[1] == 0: self.dir = [choice(["up", "down", "none", "up", "down"]), randint(1, 3) * FPS]  # select new direction and perform it for 1-3 seconds

			# display player image for current task
			if self.task[0][0] != "Blink":
				self.playerImage(self.task[0])  # if player isn't blinking


class SOUND:  # Holds all the sound files' locations and names
	goSS = pygame.mixer.Sound("Data/Sound/Go_SS.ogg")  # Sound when going to Super Sayan mode
	blink = pygame.mixer.Sound("Data/Sound/Blink.ogg")  # Sound when character blinks
	shoot = pygame.mixer.Sound("Data/Sound/Shoot.ogg")  # Sound for normal energy shooting
	error = pygame.mixer.Sound("Data/Sound/Error.ogg") # Error sound


class Text:  # monitors all the text objects of the game

	def __init__(self, text=" ", color=WHITE, size=20, style = "", x=0, y=0):
		self.text = pygame.font.SysFont("Kristen ITC", size, "b" in style.lower(), "i" in style.lower()).render(text, True, color)
		self.rect = self.text.get_rect()
		if x == -1:
			self.rect.centerx = WINW/2
		else:
			self.rect.left = x
		if y == -1:
			self.rect.centery = WINH/2
		else:
			self.rect.top = y

	def write(self, surface = windowSurface):  # writes the text object in the screen
		surface.blit(self.text, self.rect)
		if surface != windowSurface: windowSurface.blit(surface, (0, 0, WINW, WINH))


class Effect:

	def dissolve(rect, img, tilesize = 20, color = (120, 120, 120)):
		# divides the given rectangle into small tiles
		tiles = [(x, y, tilesize, tilesize) for y in range(rect.top, rect.bottom, tilesize) for x in range(rect.left, rect.right, tilesize)]
		windowSurface.blit(img, rect)  # draws the image
		tempSurface = windowSurface.copy()
		while tiles:
			rTiles = [tiles.pop(randint(0, len(tiles)-1)) for i in range(randint(1, 2)) if i <= len(tiles)-1]
			for t in rTiles:
				pygame.draw.rect(windowSurface, color, t, 1)
			pygame.display.update(rTiles) # update the image tile by tile
			mainClock.tick(FPS)  # control the speed of the dissolve effect
		pygame.time.wait(50)


	def shake(rect, img, h = True, v = False, cycle = 2, distance = 2, fps = 20):
		# o = origin, u = up, d = down, r = right, l = left
		dir = {"o" : (0, 0), "u" : (0, -1), "d" : (0, 1), "r" : (1, 0), "l" : (-1, 0)}

		if h and v: rule = "uorodolo" # up-origin-right-origin-down-origin-left-origin
		elif h: rule = "rolo" #right-origin-left-origin
		elif v: rule = "uodo" #up-origin-down-origin
		else: rule = "o" #origin

		transparentSurface.fill((0, 0, 0, 0))
		transparentSurface.blit(img, rect)

		for i in range(cycle):
			for d in rule:
				transparentSurface.scroll(distance*dir[d][0], distance*dir[d][1])  # shift the surface
				windowSurface.blit(transparentSurface, (0, 0, WINW, WINH))
				pygame.display.update([rect])
				mainClock.tick(fps)


class Textfield:

	BORDER = 2

	def __init__(self, text = " ", center = (30, 30), text_color = WHITE, label = None, font_size = 16, selected = False):
		self.default_text = self.text = text
		self.selected = selected
		self.font_size = font_size
		self.text_color = text_color
		self.label = label
		self.textObj = Text(self.text.capitalize(), self.text_color, self.font_size, "b")
		self.rect = self.textObj.rect
		self.rect.center = center

	def update_rect(self):
		# the rectangle of the textbox should be updated as the text changes
		# updates the dimension of rectangle according to the current text object
		# keeps the center of new rectangle same as that of old rectangle
		old_center = self.rect.center
		self.textObj = Text(self.text.capitalize(), self.text_color, self.font_size, "b")
		self.rect = self.textObj.rect
		self.rect.center = old_center
		self.textObj.rect = self.rect # update the textObj rect too. This rect is used by class Text to write the text

	def write(self, surface = windowSurface):
		# update Rect dimensions
		self.update_rect()
		# draw line if selected
		if self.selected: pygame.draw.line(surface, BLACK, (self.rect.bottomleft), (self.rect.bottomright), 2)
		# write the Rect
		self.textObj.write(surface)
		if surface != windowSurface: windowSurface.blit(surface, (0, 0, WINW, WINH))


class Control:
	global CONTROLS
	# manages the keys for the control of the game
	DEFAULT_CNTRLS = {"skill 1" : "e", "skill 2" : "d", "skill 3" : "c", "blink up" : "w", "blink down" : "s", "block" : "a", "pause" : "p"}
	CNTRL_RECTS = []
	CNTRL_SIZE = 45
	CNTRL_SPACING = 5
	CNTRL_REGION = pygame.Rect(300, 120, 300, 5*(CNTRL_SIZE+CNTRL_SPACING))
	CNTRL_TEXTS = []
	CNTRL_TEXTFIELDS = []
	KEY_IMG = pygame.image.load("Data/Image/Key/key1.png")
	SCROLL_IMG = pygame.image.load("Data/Image/Scroll_paper.png")
	SCROLL_BAR_IMG = pygame.transform.scale(pygame.image.load("Data/Image/Scroll_bar2.png"), (CNTRL_REGION.width, 20))

	def reset(self):
		return self.DEFAULT_CNTRLS

	def save(self, cntrl):
		with open("Data/Config.ini", "w") as file:
			file.write("Controls\n"+"\n".join(dict2list(cntrl, " = ")))  # convert dict into list then into string and write it
			print("Controls saved!")

	def load(self):
		if not path.isfile("Data/Config.ini"): return self.reset()
		else:
			with open("Data/Config.ini") as file:
				data = file.readlines()
			cntrl = list2dict(data, "=")
			if self.hasError(cntrl):
				print("Error found in controls. Controls set to defaults.")
				self.save(self.DEFAULT_CNTRLS)
				return self.reset()  # if error in controls in file, reset it
			print("Controls loaded!")
			return cntrl  # else return the loaded controls

	def hasError(self, cntrl):
		if cntrl.keys() != self.DEFAULT_CNTRLS.keys():   # check if the keys in file don't match the keys needed
			print("Error: Invalid key found!")
			return True
		else:
			if not all(i.isalpha() and len(i) == 1 for i in cntrl.values()): # check whether atleast one of the keys is not a single-digit alphabet
				print("Error: Invalid value found!")
				return True
		return False

	def prepRects(self):
		# this function simply prepares the rectangles which will be used to draw controls on the info screen
		if len(CONTROLS.keys()) != len(self.CNTRL_RECTS):
			CONTROL_KEYS = list(CONTROLS.keys())
			CONTROL_KEYS.sort() # arrange it alphabetically to keep skill1, skill2 . . . skill 4 in series
			for i in range(len(CONTROL_KEYS)):
				self.CNTRL_RECTS.append(pygame.Rect(self.CNTRL_REGION.left + (3/4)*self.CNTRL_REGION.width - (self.CNTRL_SIZE/2),
			                          self.CNTRL_REGION.top + i*(self.CNTRL_SIZE + self.CNTRL_SPACING), self.CNTRL_SIZE, self.CNTRL_SIZE))

				cntrl_text = Text(CONTROL_KEYS[i].capitalize(), BLACK, 19, "b")
				# centerx = (1/4)th of the region, centery = centery of the control
				cntrl_text.rect.center = (self.CNTRL_REGION.left + (self.CNTRL_REGION.width/4), self.CNTRL_RECTS[i].centery)
				self.CNTRL_TEXTS.append(cntrl_text)

				self.CNTRL_TEXTFIELDS.append(Textfield(CONTROLS[CONTROL_KEYS[i]].capitalize(), self.CNTRL_RECTS[i].center, BLACK, CONTROL_KEYS[i]))

			self.SCROLL_IMG = pygame.transform.scale(self.SCROLL_IMG, (self.CNTRL_REGION.width, max([r.bottom for r in self.CNTRL_RECTS]) - self.CNTRL_REGION.top))

	def drawControls(self, y):
		transparentSurface.fill((0, 0, 0, 0))
		if not self.CNTRL_RECTS: self.prepRects()  # if CNTRL_RECTS are not present, prepare them

		transparentSurface.blit(self.SCROLL_IMG, (self.CNTRL_REGION.left, self.CNTRL_REGION.top - self.CNTRL_SPACING, self.CNTRL_REGION.width, self.CNTRL_REGION.height))
		for i in range(len(list(CONTROLS.keys()))):
			self.CNTRL_TEXTS[i].write(transparentSurface)

			transparentSurface.blit(pygame.transform.scale(self.KEY_IMG, (self.CNTRL_SIZE, )*2), self.CNTRL_RECTS[i])

			self.CNTRL_TEXTFIELDS[i].write(transparentSurface)

			windowSurface.blit(transparentSurface, (0, y, WINW, WINH))


def terminate():  # save the current top score and close the game
	load_score("save")
	progressBar("Closing the game. . .", WALLPAPER.copy(), 1)
	pygame.quit()
	exit()


def load_score(mode):  # save topScore in a file and load it later
	if mode == "load":  # to load score
		if not path.isfile("Data/topScore.sav"):  # if topScore.txt file not found
			return 0  # return 0 for top score
		else:  # if file present
			with open("Data/topScore.sav") as file:
				data = file.read().lower()
				if not data:
					return 0
			score = ""
			for i in data:
				# Encryption System
				if (ord(i) - ord("a")) > 9:
					windowSurface.fill(BGCOLOR)
					Text("Nice try messing with the top score file.", WHITE, 24, "b", 200, 90).write()
					Text("But you are busted!! Top score is resetted to 0.", WHITE, 24, "b", 150, 120).write()
					with open("Data/topScore.txt", "w") as file:
						file.write("a")     # overwrite the save file with score of 0
					pause("Click below loser!")
					return 0
				#
				score += str(ord(i) - ord("a"))  # convert the score from alphabet to number
			return int(score)  # return the integer value of the score
	if mode == "save":  # to save score
		eScore = ""  # encrypt score before storing i.e convert number to alphabet
		for i in str(topScore): eScore += str(chr(ord("a") + int(i)))  # convert number to alphabet
		with open("Data/topScore.sav", "w") as file:
			file.write(eScore)


def format_score(score):
	# puts comma's at evey 3 digits of the score
	tempScore = str(int(score/5))       # actual score of game = score in code / 5
	if len(tempScore) < 4:
		return tempScore
	for i in range(len(tempScore)-4, -1, -3):
		tempScore = tempScore[:i+1]+","+tempScore[i+1:]
	return tempScore


def display_score():  # Displays the score, top score and level on the screen
	global score, topScore, level
	if level > 7:
		levelColor = RED
	elif level > 3:
		levelColor = YELLOW
	else:
		levelColor = GREEN
	if score == topScore:
		scoreColor = YELLOW
	else:
		scoreColor = WHITE
	scoreField = Text("Score:", WHITE, 20, "b", 10, 10)
	scoreText = Text(format_score(score), scoreColor, 20, "", scoreField.rect.right + 5, 10).write()
	topScoreField = Text("Top Score:", WHITE, 20, "b", 10, scoreField.rect.bottom + 3)
	topScoreText = Text(format_score(topScore), YELLOW, 20, "", topScoreField.rect.right + 5, scoreField.rect.bottom + 3).write()
	levelField = Text("Level:", WHITE, 20, "b", 10, topScoreField.rect.bottom + 3)
	levelText = Text(str(level), levelColor, 28, "", levelField.rect.right + 5, topScoreField.rect.bottom + 3)
	levelText.rect.centery = levelField.rect.centery
	levelText.write()
	levelField.write()
	scoreField.write()
	topScoreField.write()


def draw_bar(char):  # draw health and energy bars
	BARS = ["Energy", "Health"]
	for bar_type in BARS:
		i = BARS.index(bar_type)

		if bar_type == "Energy":
			bar_state = char.energy
		elif bar_type == "Health":
			bar_state = char.health

		# show the energy/health left in different position and size according to the character's type
		if bar_type == "Health":
			if bar_state[0] <= 0.25*bar_state[1]:
				bar_img = BAR_IMG["RED"]
			else:
				bar_img = BAR_IMG["GREEN"]
		else:
			bar_img = BAR_IMG["BLUE"]
		if char.type == "hero":
			bar_rect = pygame.Rect(0, WINH - (i+1)*ENERGYBARH, ENERGYBARW, ENERGYBARH)
			windowSurface.blit(pygame.transform.scale(bar_img, (round(bar_state[0]*ENERGYBARW / bar_state[1]), ENERGYBARH)), bar_rect)
		else:
			bar_rect = pygame.Rect((bar_state[1] - bar_state[0]) * (ENERGYBARW/bar_state[1]), i*ENERGYBARH, ENERGYBARW, ENERGYBARH)
			windowSurface.blit(pygame.transform.scale(bar_img, (round(bar_state[0]*ENERGYBARW / bar_state[1]), ENERGYBARH)), bar_rect)

		bar_text = Text("%s/%s" % (round(bar_state[0]), bar_state[1]), WHITE, 10)
		bar_text.rect.center = (WINW/2, bar_rect.centery)
		bar_text.write()

		if bar_type == "Energy":
			if not char.charging[0]:  # if energy not charging
				if char.transform:  # if transform mode on
					if char.energy[0] > 0:  # if energy not zero
						char.energy[0] -= Energy.ENERGYPERSECOND/FPS  # drain energy in transform mode
				else:  # is transform mode off
					if char.energy[0] < char.energy[1] and not char.charging[1]:
					# if energy not full and the character isn't charging a special attack, restore energy slowly
						char.energy[0] += char.eRegen/FPS
			if char.energy[0] < 0:
				char.energy[0] = 0
			elif char.energy[0] >= char.energy[1]:
				char.energy[0] = char.energy[1]
		elif bar_type == "Health":
			if char.health[0] < char.health[1] and char.health[0] != 0:
				char.health[0] += char.hpRegen/FPS  # regenerate health with time


def progressBar(text, surface, t = 1):
	t_intervals = splitTime(t)

	p_bar_rect = pygame.Rect(0, 0, WINW, 25)
	p_bar_rect.centery = WINH-2*p_bar_rect.height

	default_p_img = pygame.transform.scale(BAR_IMG["RED"], p_bar_rect.size)

	Text(text, WHITE, 26, "b", -1, p_bar_rect.top-50).write(surface)

	for i in range(len(t_intervals)):
		progress = 100*((i+1)/(len(t_intervals)))
		dupe_surface = surface.copy()
		p_bar_img = pygame.transform.scale(BAR_IMG["RED"], (round((p_bar_rect.width*progress)/100), p_bar_rect.height))
		surface.blit(p_bar_img, p_bar_rect)
		progress_text = Text(str(round(progress, 1)).center(3, " ") + "%", WHITE, 18)
		progress_text.rect.center = p_bar_rect.center
		progress_text.write(dupe_surface)

		windowSurface.blit(dupe_surface, (0, 0, WINW, WINH))
		pygame.display.update()
		pygame.time.wait(round(t_intervals[i]))


def splitTime(t):
	MAX_NUM = 20
	x = [0]*MAX_NUM
	MAX_t = t
	while t > 0:
		x.append(randint(1, MAX_t)/20)
		t -= x[-1]
		if t <= MAX_t/20:
			if t >= 0.05: x.append(round(t, 1))
			break
	#print(len([i for i in x if i != 0]))
	#while len(x) > MAX_NUM: x.remove(0)  # remove 0s until there area 100 items in the list
	shuffle(x) # shuffle the list
	return x


def pause(text, color = D_SILVER, size = 24):  # pause the game
	global mouseDown, dead, CONTROLS
	pygame.mouse.set_visible(True)  # make mouse visible while paused
	RECTSIZE = (300, 200)
	gameOverRect = GAMEOVER.get_rect()
	gameOverRect.bottom = -4
	gameOverRect.centerx = WINW/2
	blurSurface = transparentSurface.copy()
	blurSurface.fill((0, 0, 0, 100))
	windowSurface.blit(blurSurface, (0, 0, WINW, WINH))

	while True:

		text1 = Text(text, color, size, "b")
		# resize the Box window if text is longer
		if text1.rect.width >= RECTSIZE[0] - 50:
			boxImg = pygame.transform.scale(pygame.image.load("Data/Image/box.png"), (text1.rect.width + 100, RECTSIZE[1]))
		else:
			boxImg = pygame.transform.scale(pygame.image.load("Data/Image/box.png"), RECTSIZE)
		boxRect = boxImg.get_rect()
		boxRect.center = windowSurface.get_rect().center
		text1.rect.center = (boxRect.centerx, boxRect.centery-text1.rect.height)
		windowSurface.blit(boxImg, boxRect)
		text1.write()  # make the text on the screen
		if not dead:
			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						terminate()
					elif chr(event.key) == CONTROLS["pause"]:
						pygame.mouse.set_visible(False)  # make mouse invisible again if resumed
						mouseDown = False
						return "Cancel"
				elif event.type == MOUSEMOTION:
					px, py = event.pos
					if CLOSE_B.rect.colliderect(px, py, 0, 0):
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(BUTTONW+B_SPACING/2), int(BUTTONH+B_SPACING/2)))
					elif CANCEL_B.rect.colliderect(px, py, 0, 0):
						CANCEL_B.img = pygame.transform.scale(CANCEL_B.default_img, (int(BUTTONW+B_SPACING/2), int(BUTTONH+B_SPACING/2)))
					else:
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
						CANCEL_B.img = pygame.transform.scale(CANCEL_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
				elif event.type == MOUSEBUTTONDOWN:
					px, py = event.pos
					if CLOSE_B.rect.colliderect(px, py, 0, 0):
						Effect.shake(CLOSE_B.rect, CLOSE_B.img, False, True)
						pygame.mouse.set_visible(False)
						return "Close"
					elif CANCEL_B.rect.colliderect(px, py, 0, 0):
						pygame.mouse.set_visible(False)  # make mouse invisible again if resumed
						mouseDown = False
						Effect.shake(CANCEL_B.rect, CANCEL_B.img, False, True)
						return "Cancel"
					else:
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
						CANCEL_B.img = pygame.transform.scale(CANCEL_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
			CLOSE_B.update_rect()
			CANCEL_B.update_rect()
			CLOSE_B.rect.center = ((WINW - BUTTONW - B_SPACING)/2, boxRect.bottom - BUTTONH)
			CANCEL_B.rect.center = ((WINW + BUTTONW + B_SPACING)/2, boxRect.bottom - BUTTONH)
			CLOSE_B.draw()
			CANCEL_B.draw()
			pygame.display.update()
			mainClock.tick(FPS)

		else:
			if gameOverRect.top < 0: gameOverRect.top += 2
			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						terminate()
				elif event.type == MOUSEMOTION:
					px, py = event.pos
					if CLOSE_B.rect.colliderect(px, py, 0, 0):
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(BUTTONW+B_SPACING/2), int(BUTTONH+B_SPACING/2)))
					else:
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
				elif event.type == MOUSEBUTTONDOWN:
					px, py = event.pos
					if CLOSE_B.rect.colliderect(px, py, 0, 0):
						Effect.shake(CLOSE_B.rect, CLOSE_B.img, False, True)
						pygame.mouse.set_visible(False)
						return "Close"
					else:
						CLOSE_B.img = pygame.transform.scale(CLOSE_B.default_img, (int(2*BUTTONW/3), int(2*BUTTONH/3)))
			CLOSE_B.update_rect()
			CLOSE_B.rect.center = (WINW/2, boxRect.bottom - BUTTONH)
			CLOSE_B.draw()
			windowSurface.blit(GAMEOVER, gameOverRect)
			pygame.display.update()
			mainClock.tick(FPS)


def stopAllSounds():
	SOUND.goSS.stop()
	SOUND.blink.stop()
	SOUND.shoot.stop()


def reset_game():
	global time, score, mouseDown, dead, hero, level
	level = 1 # set inital level
	time = 1  # set initial time to 1 sec
	score = 0  # set initial score to 0
	Object.objects.clear()  # make initial object empty
	Boss.boss.clear()  # remove any boss from previous game
	mouseDown = False  # set supersayan and mouse chicked status to false
	dead = False  # keep track of if hero is dead
	Boss.moveSpeed = 2  # reset the movement speed of the boss


def home_screen(page):
	pygame.mouse.set_visible(True)

	if page == "Homepage":
		# load and prepare the logo
		logoImg = pygame.transform.scale(pygame.image.load("Data/Image/Logo.png"), (370, 71))
		logoRect = logoImg.get_rect()
		logoRect.center = windowSurface.get_rect().center
		Effect.dissolve(logoRect, logoImg, 15)

		while True:
			windowSurface.blit(WALLPAPER, pygame.Rect(0, 0, WINW, WINH))
			windowSurface.blit(logoImg, logoRect)

			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						terminate()
				elif event.type == MOUSEMOTION:
					px, py = event.pos
					if START_B.rect.colliderect(px, py, 0, 0):
						START_B.img = pygame.transform.scale(START_B.default_img, (BUTTONW+int(B_SPACING/2), BUTTONH+int(B_SPACING/2)))
					elif OPTION_B.rect.colliderect(px, py, 0, 0):
						OPTION_B.img = pygame.transform.scale(OPTION_B.default_img, (BUTTONW+int(B_SPACING/2), BUTTONH+int(B_SPACING/2)))
					else:
						START_B.img = pygame.transform.scale(START_B.default_img, (BUTTONW, BUTTONH))
						OPTION_B.img = pygame.transform.scale(OPTION_B.default_img, (BUTTONW, BUTTONH))
				elif event.type == MOUSEBUTTONDOWN:
					px, py = event.pos
					if START_B.rect.colliderect(px, py, 0, 0):
						Effect.shake(START_B.rect, START_B.img, False, True)
						Effect.shake(logoRect, logoImg, True, False, 5, 4, FPS)
						return "Start"
					elif OPTION_B.rect.colliderect(px, py, 0, 0):
						Effect.shake(OPTION_B.rect, OPTION_B.img, False, True)
						return "Option"
					else:
						START_B.img = pygame.transform.scale(START_B.default_img, (BUTTONW, BUTTONH))
						OPTION_B.img = pygame.transform.scale(OPTION_B.default_img, (BUTTONW, BUTTONH))
			START_B.update_rect()
			OPTION_B.update_rect()
			START_B.rect.center = ((WINW - BUTTONW - B_SPACING)/2, WINH - 2*BUTTONH)
			OPTION_B.rect.center = ((WINW + BUTTONW + B_SPACING)/2, WINH - 2*BUTTONH)
			START_B.draw()
			OPTION_B.draw()
			pygame.display.update()
			mainClock.tick(FPS)

	elif page == "Option":
		# smaller logo for the option page
		logoImg = pygame.transform.scale(pygame.image.load("Data/Image/Logo.png"), (278, 53))
		logoRect = logoImg.get_rect()
		logoRect.center = (WINW/2, 50)

		selected_index = None # holds the data of the control current being selected
		y_shift = -Control.CNTRL_SIZE # vertical position of the controls used for scrolling
		SCROLL = [False, None] # [Scroll status, Scroll direction]
		# prepare scroll up and scroll down rectangles
		up_rect = pygame.Rect(Control.CNTRL_REGION.left, Control.CNTRL_REGION.top-20, Control.CNTRL_REGION.width, 20)
		down_rect = pygame.Rect(Control.CNTRL_REGION.left, Control.CNTRL_REGION.bottom, Control.CNTRL_REGION.width, 20)

		windowSurface.blit(WALLPAPER, pygame.Rect(0, 0, WINW, WINH))
		windowSurface.blit(logoImg, logoRect)
		windowSurface.blit(Control.SCROLL_BAR_IMG, up_rect) # scroll up button
		windowSurface.blit(pygame.transform.rotate(Control.SCROLL_BAR_IMG, 180), down_rect) #scroll down button
		#tempSurface = windowSurface.copy()
		#windowSurface.blit(tempSurface, (0, 0, WINW, WINH))
		BACK_B.rect.center = (WINW/2, WINH - BUTTONH)
		BACK_B.draw()
		pygame.display.update()

		while True:
			if SCROLL[0]: # if scroll button clicked
				if SCROLL[1] == "u": # if scroll up
					# scroll up if the lowest item isn't above the bottom of the Control Region
					if max([r.bottom for r in Control.CNTRL_RECTS]) + y_shift > Control.CNTRL_REGION.bottom - Control.CNTRL_SPACING:
						y_shift -= 5
					else:
						SOUND.error.play()
						SCROLL = [False, None]
				elif SCROLL[1] == "d": # if scroll down
					# scroll down if the top item isn't below the top of the Control Region
					if min([r.top for r in Control.CNTRL_RECTS]) + y_shift < Control.CNTRL_REGION.top + Control.CNTRL_SPACING:
						y_shift += 5
					else:
						SOUND.error.play()
						SCROLL = [False, None]

			for event in pygame.event.get():
				if event.type == QUIT:
					terminate()
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						terminate()
					if selected_index != None:
						if event.key == K_BACKSPACE:
							Control.CNTRL_TEXTFIELDS[selected_index].text = Control.CNTRL_TEXTFIELDS[selected_index].text[:-1]
							if Control.CNTRL_TEXTFIELDS[selected_index].text == "":
								Control.CNTRL_TEXTFIELDS[selected_index].text = " "
						else:
							if ord("a") <= event.key <= ord("z"): # support only alphabets
								# if the pressed key is either the same previous key or not already taken
								if chr(event.key) == Control.CNTRL_TEXTFIELDS[selected_index].default_text or chr(event.key) not in list(CONTROLS.values()):
									Control.CNTRL_TEXTFIELDS[selected_index].text = Control.CNTRL_TEXTFIELDS[selected_index].default_text= chr(event.key)
									CONTROLS[Control.CNTRL_TEXTFIELDS[selected_index].label] = chr(event.key)
									Control.CNTRL_TEXTFIELDS[selected_index].selected = False
									selected_index = None
								else: # else if it is taken, play error sound
									SOUND.error.play()
							else: # if invalid key pressed, play error sound
								SOUND.error.play()
				elif event.type == MOUSEBUTTONDOWN:
					px, py = event.pos
					if Control.CNTRL_REGION.colliderect(px, py, 0, 0):
						for r in Control.CNTRL_RECTS:
							if r.colliderect(px, py-y_shift, 0, 0) and Control.CNTRL_REGION.colliderect(r.centerx, r.centery+y_shift, 0, 0):
								selected_index = Control.CNTRL_RECTS.index(r)
								Control.CNTRL_TEXTFIELDS[selected_index].selected = True
								Control.CNTRL_TEXTFIELDS[selected_index].text = " "
								break
							elif selected_index != None:
								Control.CNTRL_TEXTFIELDS[selected_index].selected = False
								if Control.CNTRL_TEXTFIELDS[selected_index].text == " ":
									Control.CNTRL_TEXTFIELDS[selected_index].text = Control.CNTRL_TEXTFIELDS[selected_index].default_text
								selected_index = None
					else:
						if selected_index != None:
							Control.CNTRL_TEXTFIELDS[selected_index].selected = False
							if Control.CNTRL_TEXTFIELDS[selected_index].text == " ":
									Control.CNTRL_TEXTFIELDS[selected_index].text = Control.CNTRL_TEXTFIELDS[selected_index].default_text
							selected_index = None

						if BACK_B.rect.colliderect(px, py, 0, 0):
							Effect.shake(BACK_B.rect, BACK_B.img, False, True)
							Control().save(CONTROLS)
							return "Homepage"
						elif up_rect.colliderect(px, py, 0, 0):
							SCROLL = [True, "u"]
						elif down_rect.colliderect(px, py, 0, 0):
							SCROLL = [True, "d"]
						else:
							SCROLL = [False, None]
				elif event.type == MOUSEBUTTONUP:
					SCROLL = [False, None]

			Control().drawControls(y_shift)

			pygame.display.update([Control.CNTRL_REGION])
			mainClock.tick(FPS)
	else:
		return "Homepage"


def load_gdata(type):
	# loads game data of characters and skills from external files and returns a dictionary with either all skills or all characters
	DATA = {}
	# set data path and the file format according to the type of data being loaded
	if type == "skills": dataPath, dataFormat = "Data/Skills", ".skill"
	elif type == "characters": dataPath, dataFormat = "Data/Characters", ".chr"
	# from the given path, load all files with given extension
	files = [file for file in listdir(dataPath) if file.endswith(dataFormat)]
	for f in files:
		# read each file and save its data in DATA list
		with open("/".join([dataPath, f])) as file:
			data = file.readlines()
			data = list2dict(data, "=")
			DATA.update(dict([[data["name"], data]]))
	#print("Data: %s"%DATA)
	return DATA


def str2dict(text, sign):  # convert string to dictionary
	if sign not in text:
		return {} # if the line is not a valid setting
	else:
		s = text.strip("\n")
		s = [x.strip(" ") for x in s.split(sign)]
		return dict([[s[0], eval(s[1])]])


def list2dict(LIST, sign): # convet list to dictionary
	d = {}
	for l in LIST: d.update(str2dict(l, sign))
	return d


def dict2list(DICT, sign = " "): # convert dictionary into list by adding key and value
	return [d+sign+"'"+DICT[d]+"'" for d in DICT.keys()]


def main():
	#### Start Page showing game instructions ####
	global time, score, mouseDown, dead, topScore, hero, level, CONTROLS, SKILLS, CHARACTERS
	page = "Homepage"
	dead = True
	try:
		CONTROLS = Control().load()
	except:
		print("Error loading controls. . . .")
		print("Default controls loaded. . . .")
		# load default controls if error occurs while loading user's controls
		CONTROLS = Control().reset()
		# save the default controls
		Control().save(CONTROLS)

	topScore = load_score("load")  # load top score from the 'topScore.txt' file
	SKILLS = load_gdata("skills")
	CHARACTERS = load_gdata("characters")
	while True:
		progressBar("Please wait", WALLPAPER.copy(), 1)
		page = home_screen(page)        # draw Homepage or Instruction page at the beginning.

		if page == "Start": # When start button clicked
			pygame.mouse.set_visible(False)
			reset_game()
			playerTask = ["None", None]
			hero = Character(CHARACTERS[choice(["kid buu", "goku"])])
			hero.type = "hero"
			hero.rect.left = 5 # set hero's left co-ordinate

			##### Game Starts Here ######
			while not dead: # while Hero is not dead
				# if the hero's energy is finished and he isn't charging an attack
				if hero.energy[0] <= 0 and not hero.charging[0]:
					hero.transform = False  # turn off transform mode

				# turn off the transform music if transform mode is deactivated either by user or because all energy is drained
				if not hero.transform:
					pygame.mixer.music.stop()

				Background().animate()  # animate background
				Object().add(time)  # add objects
				Object().move(hero)  # move and draw objects
				display_score()  # display score, top score and level
				draw_bar(hero) # draw health and energy bars
				hero.playerImage(playerTask)  # update player's image according to the current task
				Energy().move(hero)  # move and draw hero's energies

				if not Boss.boss:
					time += 1  # increase time by 1 per frame if no boss
				else:  # if boss present
					for boss in Boss.boss:
						boss.BossAI(playerTask, hero) # control Boss' activities

				# event handling
				for event in pygame.event.get():
					if event.type == QUIT:
						terminate()
					if event.type == KEYDOWN and not (hero.charging[1] or hero.blocking[0]): # allow blinking if hero isn't releasing energy or blocking
						if chr(event.key) == CONTROLS["blink up"]: # blink up
								hero.blink("up")
						elif chr(event.key) == CONTROLS["blink down"]: # blink down
							hero.blink("down")
					if not (hero.charging[0] or hero.charging[1] or hero.blocking[0]):  # while hero isn't charging or releasing or blocking any attack
						if event.type == MOUSEBUTTONDOWN:
							# allowing shooting only if not charging/releasing/blocking
							mouseDown = True
						elif event.type == MOUSEBUTTONUP:
							# stop shooting if mouse button released
							mouseDown = False
						elif event.type == KEYDOWN:
							# Only allow pausing the game while not charging
							if chr(event.key) == CONTROLS["pause"]:
								#hero.playerImage(	["None", None])  # without this, the player image will disapper while game is paused
								if pause("Paused") == "Close":
									dead = True
									break
							elif event.key == K_ESCAPE:
								if pause("Close this game?") == "Close":
									dead = True
									break
							elif chr(event.key) == CONTROLS["skill 1"]: # activating 1st skill
								hero.prepSkill(0, "down")
							elif chr(event.key) == CONTROLS["skill 2"]: # activating 2nd skill
								hero.prepSkill(1, "down")
							elif chr(event.key) == CONTROLS["skill 3"]: # activating 3rd skill
								hero.prepSkill(2, "down")
							elif chr(event.key) == CONTROLS["block"]: # block
								hero.blocking[0] = True
								break
					else: # if charging
						if event.type == KEYUP:
							if hero.charging[0]:  # if charging
								if chr(event.key) == CONTROLS["skill 1"] and hero.charging[2] == hero.skills[0]["name"]:  # if charging 1st skill
									playerTask = hero.prepSkill(0, "up")
								elif chr(event.key) == CONTROLS["skill 2"] and hero.charging[2] == hero.skills[1]["name"]:  # if charging 2nd skill
									playerTask = hero.prepSkill(1, "up")
								elif chr(event.key) == CONTROLS["skill 3"] and hero.charging[2] == hero.skills[2]["name"]:  # if charging 3rd skill
									playerTask = hero.prepSkill(2, "up")
							elif chr(event.key) == CONTROLS["block"]: # block
								hero.blocking[0] = False
								break

					if not (hero.charging[1] or hero.blocking[0]): # if not releasing or not blocking, move the player
						if event.type == MOUSEMOTION:
							hero.rect.centery = event.pos[1]  # move player Rect to current mouse position

				pygame.mouse.set_pos(hero.rect.center) # places the cursor at the center of the hero. It also prevents the cursor from going out from the screen

				if hero.blocking[0]:
					if playerTask[0] != "Block": playerTask[0] = "Block"
				elif mouseDown:  # if mouse button pressed
					if playerTask[0] != "Shoot": playerTask = ["Shoot", 1]
					hero.performTask(playerTask)  # add new energy in the screen
				elif not mouseDown and not (hero.charging[0] and hero.charging[1]) and not hero.blocking[0]:  # if mouse not pressed and the hero is neither charging nor releasing
					hero.attackRate[0] = 0  # reset hero.attackRate[0]'s value
					playerTask = ["None", None]

				if hero.charging[0]:  # if charging
					hero.chargeTime[1] += 1
					if hero.chargeTime[1] % hero.chargeTime[2] == 0 and hero.chargeTime[0] != 4:
						hero.chargeTime[0] += 1
					mouseDown = False  # prevent shooting energy
					hero.blocking[0] = False # prevent blocking
					playerTask = ["Charge", hero.charging[2]]
					if hero.charging[2] in [s["name"] for s in SKILLS.values() if s["type"] == ("Active", "ball")]:
						Energy().energyBallAnimate(hero)
					else: hero.drawEnergySphere()

				# Image of skill is drawn after the objects
				if hero.charging[1]:  # if releasing energy after charging
					# other objects don't freeze on the screen while these skills are used
					playerTask = ["Release", hero.charging[2]]
					hero.performTask(playerTask)

				if score > topScore:  # if score is higher than top score
					topScore = score  # make the score top score

				if hero.isDead():  # check if hero dead
					dead = True
					# update the health, energy and other status for the last time on the screen
					Background().animate()
					display_score()
					draw_bar(hero)
					hero.playerImage(playerTask)
					if Boss.boss:  # if boss present, update them too
						for boss in Boss.boss:
							boss.playerImage()
							draw_bar(boss)
					break  # break the while loop and go to end of the code

				pygame.display.update()
				mainClock.tick(FPS)
			# Stop all currently playing sounds
			stopAllSounds()
			pygame.mixer.music.stop()
			if score == topScore:
				pause("New Top Score: %s" % str(round(score/5)), YELLOW)
				load_score("save")
			else:
				pause("Your Score: %s" % str(round(score/5)))
			page = "Homepage"


if __name__ == "__main__":
	pygame.quit()
	# create DBZ.py with which the game starts
	with open("DBZ.py", "w") as file:
		file.write("from Dragon_Ball import *\n\nif __name__ == '__main__':\n    main()")
	print("DBZ.py file created!! Open it.")
	# create Config.ini. It holds controls.
	Control().save(Control().reset())   # reset controls and save
	print("Config.ini file created. Controls set to defaults.")
	input("Press Enter to exit. . . . .")


# Things to change:
# 1) Upgrade lvl up alert (may not be needed), 2) Scoreboard (Like tekken n show combo hits n damages), 3) Health bar with exp bar like DOTA FPS bar (Done), 4) Boss alert,
# 5) New hero image, 6) Hero selection, 7) Dota-style skill (Done), 8) Energy-Collision event(Done) 9) Info screen and controls (Done)
# 10) progress bar (Done), 11) Screen to Lvl up skills after hero selection (3 skills and 6 lvl ups with each max 4 lvl)
# *) Cooldown for skills
# 12) Stage system, 13) Organize skills like Energy Ball n Spirit bomb and so on
# 14) After last stage, unlock new character, 14) After all other changes finish, change the gameplay to ground like in Tekken
