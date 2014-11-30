import pygame, sys, random, os
from pygame.locals import *

pygame.init()
# Set up window, BGmusic and clock
WINW = 800
WINH = 500
windowSurface = pygame.display.set_mode((WINW, WINH))
transparentSurface = windowSurface.convert_alpha()
pygame.display.set_caption("Dragon Ball")
mainClock = pygame.time.Clock()
FPS = 50
pygame.mixer.music.load("Data/Sound/SS_mode_on.ogg")        # Background music when Super Sayan mode is on

# Set up color
BGCOLOR = (103, 141, 159)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)
YELLOW = (255, 255, 0)

# set up game constants
SCORETHRESHOLD = 3000       # energy damage will be increased by 1 in every 3000 scores earned
STARMINSIZE = 2
STARMAXSIZE = 8
STARSPEED = 2
stars = []
PLAYERIMGW = 35
PLAYERIMGH = 80
BLINKDISTANCE = PLAYERIMGH+40
KAMEHAMEHADMG = 3
EXPLOSIVEWAVEDMG = 1
KAMEHAMEHA = {"rect" : pygame.Rect(0, 0, 0, 0), "damage" : KAMEHAMEHADMG}
EXPLOSIVEWAVE = {"rect" : pygame.Rect(0, 0, 0, 0), "damage" : EXPLOSIVEWAVEDMG}
MAXENERGY = 100
ENERGYBARW = 100
ENERGYBARH = 50
ENERGYPERSECOND = 0.5
ENERGYSPEED = 5
ENERGYW = 55
ENERGYH = 25
ENERGYDMG = 10
MAXENERGYDMG = 20
energy = []     # stores the rectangle information and the image data of each energy as a dictionary in this list
OBJMINSIZE = 25
OBJMAXSIZE = 50
OBJMINSPEED = 1
OBJMAXSPEED = 5
OBJECTRATE = 3
objects = []           # Stores the rectangle info, speed, life and image data of all the objects (asteroids, comets and planets) in the screen
PLANETRADIUS = 400
PLANETSPEED = 1
PLANETLIFE = 250

class SOUND:    # Holds all the sound files' locations and names
	goSS = pygame.mixer.Sound("Data/Sound/Go_SS.ogg")           # Sound when going to Super Sayan mode
	charging = pygame.mixer.Sound("Data/Sound/Charging.ogg")        # Sound when charging Kamehameha
	releasing = pygame.mixer.Sound("Data/Sound/Releasing.ogg")      # Sound when releasing Kamehameha
	blink = pygame.mixer.Sound("Data/Sound/Blink.ogg")                  # Sound when character blinks
	shoot = pygame.mixer.Sound("Data/Sound/Shoot.ogg")                  # Sound for normal energy shooting
	charging_e = pygame.mixer.Sound("Data/Sound/Charging_e.ogg")        # Sound when charging explosive wave

def makeAnimatedBackground():               # Makes a background with stars going to left
	windowSurface.fill(BGCOLOR)
	starSize = random.randint(STARMINSIZE, STARMAXSIZE)         # randomly selects a size for a star
	starImg = pygame.transform.scale(pygame.image.load("Data/Image/star.png"), (starSize, starSize))        # make the star image of the randomly chosen size
	stars.append({"rect": pygame.Rect(WINW, random.randint(0, WINH), 0, 0), "image" : starImg})             # append the star's rect info and image in the 'stars' list
	for s in stars[:]:
		windowSurface.blit(s["image"], s["rect"])           # loops over every star info in the 'stars' list and draw them on the screen according to the rect and image value they hold
		s["rect"].move_ip(-STARSPEED, 0)                       # move the current star to left according to the value of STARSPEED
		if s["rect"].right < 0:                                             # check if the star's right edge has gone past the left edge of the screen
			stars.remove(s)                                                 # remove the star if it has

def makeNewObjects(time):       # adds new object on the screen according to the time.
	if time%25 == 0:                        # makes new asteoids on the screen in every 25 frames
		objectSize = random.randint(OBJMINSIZE, OBJMAXSIZE)
		# randomly chooose the asteroid image among the three asteroids
		objectImg = pygame.transform.scale(random.choice([pygame.image.load("Data/Image/asteroid1.png"), pygame.image.load("Data/Image/asteroid2.png"), pygame.image.load("Data/Image/asteroid3.png")]), (objectSize, objectSize))
		objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(OBJMINSPEED, OBJMAXSPEED), "life" : [objectSize, objectSize], "image" : objectImg})
	if time%100 == 0:                       # makes new comets on the screen in every 100 frames
		n = int((time/100)/5)
		if n > 5:
			n = 5
		for i in range(n):              # Adds more comets simultaneously on the screen with time
			objectSize = random.randint(OBJMINSIZE, OBJMAXSIZE)
			objectImg = pygame.transform.scale(pygame.image.load("Data/Image/comet.png"), (objectSize, objectSize))
			objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(OBJMINSPEED, OBJMAXSPEED), "life" : [objectSize, objectSize], "image" : objectImg})
	if time%1000 == 0:              # makes planets on the screen in every 1000 frames
		if (time/1000) <= 3:         # the first three planets have relatively smaller radius and less life i.e easier to destroy
			objects.append({"rect" : pygame.Rect(WINW, 0, PLANETRADIUS, PLANETRADIUS), "speed" : PLANETSPEED, "life" : [PLANETLIFE+int(time/1000)*25, PLANETLIFE+int(time/1000)*25], "image" : pygame.transform.scale(pygame.transform.rotate(pygame.image.load("Data/Image/Planet.png"), 20), ((5*int(time/1000))+PLANETRADIUS, (5*int(time/1000))+PLANETRADIUS))})
		else:                               # After the third planet, planets have large radius and more life i.e harder to destroy
			objects.append({"rect" : pygame.Rect(WINW, 0, PLANETRADIUS, PLANETRADIUS), "speed" : PLANETSPEED, "life" : [2*PLANETLIFE+int(time/1000)*10, 2*PLANETLIFE+int(time/1000)*10], "image" : pygame.transform.scale(pygame.transform.rotate(pygame.image.load("Data/Image/Planet.png"), 20), (PLANETRADIUS+(5*int(time/1000)), PLANETRADIUS+(5*int(time/1000))))})

def moveObjects():      # Moves the objects (asteroids, comets and planets) to left
	global score
	for o in objects[:]:
		o["rect"].move_ip(-o["speed"], 0)               # move object to left
		windowSurface.blit(o["image"], o["rect"])       # draw it on the screen
		for e in energy[:]:                                     # loop over every energy blasts on the screen
			if e["rect"].colliderect(o["rect"]):          # check if the current object collides with any energy blast on the screen
				o["life"][0] -= e["damage"]                 # if it collides, reduce the life of the object according to the damage of the enegy
				energy.remove(e)                                # remove the energy blast that collided
				prevScore = score
				if o["life"][0] <= 0:                              # if the life of the object is zero or less
					score += o["life"][1]                       # increase the score by the value of life of the object
					if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and ENERGYDMG <= MAXENERGYDMG:
						ENERGYDMG += 1
					objects.remove(o)                           # then remove the object which was destroyed by the energy blast

def kamehameha(playerImg):                              # shoots Kamehameha
	global score, superSayan, time, chargeTime, topScore
	KAMEHAMEHA["rect"].width = 0                    # set initial width of kamehameha to zero so that it isn't visible on the screen
	KAMEHAMEHA["rect"].height = PLAYERIMGH+40           # set its height a little bit greater than player's height
	KAMEHAMEHA["rect"].left = playerRect.right                 # set the kamehameha's left side equal to the player's right side so that it sees to come out from the hand
	KAMEHAMEHA["rect"].centery = playerRect.centery        # align the kamehameha beam so that it emerges from the mid of the player
	if superSayan:                              # if Super Sayan mode is on
		KAMEHAMEHA["damage"] = 2*(KAMEHAMEHA["damage"]+chargeTime)           # Double the kamehameha's damage value in SS mode
	else:
		KAMEHAMEHA["damage"] = KAMEHAMEHA["damage"]+chargeTime                  # Increase kamehameha's damage according to the time it was being charged
	while KAMEHAMEHA["rect"].right < WINW+200:                             # while Kamehameha's right side is within the 200 pixel additional distance from the window's width
		kamehamehaImg = pygame.transform.scale(pygame.image.load("Data/Image/kamehameha.png"), (KAMEHAMEHA["rect"].width, KAMEHAMEHA["rect"].height))   # set kamehameha's image to current KAMEHAMEHA["rect'}'s width and height
		makeAnimatedBackground()                # keep animating the background
		if time%25 == 0:                # add objects on the screen when time is a multiple of 25
			makeNewObjects(time)
		time += 1
		moveObjects()                                   # keep moving the objects
		moveEnergy()                                    # keep moving the energy blasts on the screen
		displayScore()                                  # keep displaying the score
		superSayan = False
		drawEnergyBar(0)                            # draw no energy while Kamehameha is progressing to the right side
		KAMEHAMEHA["rect"].width += ENERGYSPEED+5           # increase Kamehameha's lenght (width) a little bit faster than that of ordinary energy's speed
		windowSurface.blit(playerImg, playerRect)                       # draw player's image on the screen
		windowSurface.blit(kamehamehaImg, KAMEHAMEHA["rect"])       # draw kamehameha in its current position on the screen
		if gotHit():                        # check if got hit
			if score > topScore:            # if score is higher than top score
				topScore = score            # make the score top score
			break                           # break the while loop and go to end of the code
		for o in objects[:]:
			windowSurface.blit(o["image"], o["rect"])                       # draw objects again on the screen so that they appear over kamehameha
			if KAMEHAMEHA["rect"].colliderect(o["rect"]):               # check if the current object collided with kamehameha
				o["life"][0] -= KAMEHAMEHA["damage"]                    # subtract life is yes
				prevScore = score
				if o["life"][0] <= 0:                                                       # check if objects life is zero or less
					score += o["life"][1]                                                   # provide socre is yes
					if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and ENERGYDMG <= MAXENERGYDMG:
						ENERGYDMG += 1
					objects.remove(o)                                                       # then remove the object
		pygame.display.update()                                                     # update the changes made in the above While loop
		mainClock.tick(FPS)
	if KAMEHAMEHA["rect"].right >= WINW+200:                         # stop the releasing sound after kamehameha is over
		SOUND.releasing.stop()
	if KAMEHAMEHA["damage"] == 2*(KAMEHAMEHADMG+chargeTime):         # check if super sayan mode was on or not
		superSayan = True                                                               # set value to True if yes
	KAMEHAMEHA["damage"] = KAMEHAMEHADMG                    # reset the kamehameha's damage value to default value

def explosiveWave(playerImg):
	global score, superSayan, time, chargeTime, topScore
	EXPLOSIVEWAVE["rect"].width = 0                    # set initial width of explosive wave to zero so that it isn't visible on the screen
	EXPLOSIVEWAVE["rect"].height = 0                   # set initial heigth of explosive wave to zero so that it isn't visible on the screen
	if superSayan:                              # if Super Sayan mode is on
		EXPLOSIVEWAVE["damage"] = 2*(EXPLOSIVEWAVE["damage"]+chargeTime)           # Double the kamehameha's damage value in SS mode
	else:
		EXPLOSIVEWAVE["damage"] = EXPLOSIVEWAVE["damage"]+chargeTime                  # Increase kamehameha's damage according to the time it was being charged
	while EXPLOSIVEWAVE["rect"].right < WINW+200:                             # while Kamehameha's right side is within the 200 pixel additional distance from the window's width
		explosiveWaveImg = pygame.transform.scale(pygame.image.load("Data/Image/Explosive_wave.png"), (EXPLOSIVEWAVE["rect"].width, EXPLOSIVEWAVE["rect"].height))   # set kamehameha's image to current KAMEHAMEHA["rect'}'s width and height
		makeAnimatedBackground()                # keep animating the background
		if time%25 == 0:                # add objects on the screen when time is a multiple of 25
			makeNewObjects(time)
		time += 1
		moveObjects()                                   # keep moving the objects
		moveEnergy()                                    # keep moving the energy blasts on the screen
		superSayan = False
		EXPLOSIVEWAVE["rect"].width += 6*ENERGYSPEED           # increase explosive wave's  width a little bit faster than that of ordinary energy's speed
		EXPLOSIVEWAVE["rect"].height += 6*ENERGYSPEED
		EXPLOSIVEWAVE["rect"].centerx = playerRect.centerx                 # set explosive wave's centerx to player's centerx
		EXPLOSIVEWAVE["rect"].centery = playerRect.centery        # set explosive wave's centery to player's centery
		windowSurface.blit(explosiveWaveImg, EXPLOSIVEWAVE["rect"])       # draw explosive wave in its current position on the screen
		windowSurface.blit(playerImg, playerRect)                       # draw player's image on the screen
		displayScore()                                  # keep displaying the score
		drawEnergyBar(0)                            # draw no energy while explosive wave is progressing to the right side
		if gotHit():                        # check if got hit
			if score > topScore:            # if score is higher than top score
				topScore = score            # make the score top score
			break                           # break the while loop and go to end of the code
		for o in objects[:]:
			windowSurface.blit(o["image"], o["rect"])                       # draw objects again on the screen so that they appear over explosive wave
			if EXPLOSIVEWAVE["rect"].colliderect(o["rect"]):               # check if the current object collided with explosive wave
				o["life"][0] -= EXPLOSIVEWAVE["damage"]                    # subtract life is yeas
				prevScore = score
				if o["life"][0] <= 0:                                                       # check if objects life is zero or less
					score += o["life"][1]                                                   # provide socre is yes
					if (prevScore%SCORETHRESHOLD) > (score%SCORETHRESHOLD) and ENERGYDMG <= MAXENERGYDMG:
						ENERGYDMG += 1
					objects.remove(o)                                                       # then remove the object
		pygame.display.update()                                                     # update the changes made in the above While loop
		mainClock.tick(FPS)
	if EXPLOSIVEWAVE["rect"].right >= WINW+200:                         # stop the releasing sound after explosive wave is over
		SOUND.releasing.stop()
	if EXPLOSIVEWAVE["damage"] == 2*(EXPLOSIVEWAVEDMG+chargeTime):         # check if super sayan mode was on or not
		superSayan = True                                                               # set value to True if yes
	EXPLOSIVEWAVE["damage"] = EXPLOSIVEWAVEDMG                    # reset the explosive wave's damage value to default value

def addNewEnergy(superSayan):       # Adds new energy dictionary to the list energy
	global t1, t2           # t1 and t2 value are used to make some delays in adding new energy on the screen without slowing down the whole game's FPS
	# t2's value is kept constant but t1's value is increased by 1 in every frame. if t1's value if the multiple integer of t2, then new energy is added
	# so in a sense, t2's value kinda acts like the value that determines after how many frame's should one energy be added after another energy
	# choose energy blast's image when super sayan mode is on
	if superSayan:
		energyImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Energy.png"), (ENERGYW, ENERGYH))
		x = 2               # x holds the integer value that will increase energy damage i.e make damage double if supersayan
	# choose energy blast's image when super sayan mode is off
	else:
		energyImg = pygame.transform.scale(pygame.image.load("Data/Image/Energy.png"), (ENERGYW, ENERGYH))
		x = 1               # make no change in energy's dame value if super sayan mode is off
	energyRect = energyImg.get_rect()               # get rect around the energy image
	energyRect.centery = playerRect.centery        # set its centery to player's centery
	energyRect.left = playerRect.right                  # set energy's left side to player's right side value
	t1 += 1                     # increase t1's value
	if t1%t2 == 0 or t1 == 9:               # if t1 is multiple of t2 or if t1 == 9 (which is for the 1st energy released when mouse click for the first time)
		SOUND.shoot.play()                  # play shoot sound
		energy.append({"rect" : energyRect, "image" : energyImg, "damage" : x*ENERGYDMG})           # add new energy

def moveEnergy():           # move the energies forward
	for e in energy[:]:
		e["rect"].move_ip(ENERGYSPEED, 0)
		windowSurface.blit(e["image"], e["rect"])
		if e["rect"].left > WINW:
			energy.remove(e)

def gotHit():               # check if player got hit by any object
	for o in objects:
		if playerRect.colliderect(o["rect"]):           # if got hit
			return True                                     # return True
	return False                # else return False

def blink(dir, superSayan):             # makes the player blink up or down
	global playerRect
	if superSayan:
		blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Blink.png"), (PLAYERIMGW, PLAYERIMGH))
	elif not superSayan:
		blinkImg = pygame.transform.scale(pygame.image.load("Data/Image/Blink.png"), (PLAYERIMGW, PLAYERIMGH))
	if dir == "down":                           # if blink down
		move = BLINKDISTANCE
	elif dir == "up":                           # if blink up
		move = -BLINKDISTANCE
	finalRect = playerRect.move(0, move)            # move the playerRect to finalRect without removing the playerRect value
	if finalRect.bottom > WINH:                         # if final position below the bottom of window
		finalRect.bottom = WINH
	if finalRect.top < 0:                                   # if final position above the top of window
		finalRect.top = 0
	pygame.mouse.set_pos(finalRect.centerx, finalRect.centery)          # move mouse to final position
	windowSurface.blit(blinkImg, playerRect)                               # make the blink image in initial position
	windowSurface.blit(blinkImg, finalRect)                                   # make the blink image in final position
	if charging[0]:
		transparentSurface.fill((0, 0, 0, 0))                                       #  fill transparentSurface with an invisible colour
		if superSayan:
			pygame.draw.circle(transparentSurface, (chargeTime*50, chargeTime*50, 0, chargeTime*40), CENTER, radius)    # draw a yellow transparent circle
		else:
			pygame.draw.circle(transparentSurface, (chargeTime*50, 0, 0, chargeTime*40), CENTER, radius)           # draw a red transparent circle
		windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))                         # draw the transparent over the windowSurface
	pygame.display.update()                                                             # update the change
	pygame.time.wait(150)                                                               # make the screen freeeze while blinking
	playerRect = finalRect                                                              # set final rect as player's rect

def playerImage(task, superSayan):                  # return player's image accorind the the current tast it is doing
	# choose among the Super Sayan's images is super sayan mode on
	if superSayan:
		if task == "None":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Normal.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Shoot":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Shooting.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Charge":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Charging.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Releasing.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release Wave":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Releasing_e.png"), (PLAYERIMGW, PLAYERIMGH))
	# choose among the normal images if super sayan mode off
	else:
		if task == "None":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Normal.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Shoot":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Shooting.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Charge":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Charging.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Releasing.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release Wave":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Releasing_e.png"), (PLAYERIMGW, PLAYERIMGH))
	return playerImg

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
		if not os.path.isfile("Data/Image/topScore.txt"):               # if topScore.txt file not found
			return 0                                                                        # return 0 for top score
		else:                                                                                   # if file present
			with open("Data/Image/topScore.txt") as file:
				data = file.read().lower()
			score = ""
			for i in data:
				# If someone messes with the topScore file
				if (ord(i)-ord("a")) > 9:
					windowSurface.fill(BGCOLOR)
					writeText("Nice try messing with the top score file.", WHITE, 24, 150, 135, False)
					writeText("But you are busted!! Top score is resetted to 0.", WHITE, 24, 100, 165, False)
					with open("Data/Image/topScore.txt", "w") as file:
						file.write("a")
					pause("Press a key loser!", False, -1, -1)
					return 0
				score += str(ord(i)-ord("a"))                                   # convert the score from alphabet to number
			return int(score)                                                       # return the integer value of the score
	if mode == "save":          # to save score
		eScore = ""         # encrypt score before storing i.e convert number to alphabet
		for i in str(topScore): eScore += str(chr(ord("a")+int(i)))         # convert number to alphabet
		with open("Data/Image/topScore.txt", "w") as file:
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

def drawEnergyBar(manualDrain):                     # draw's energy bar with current amount of energy left in it
	global energyBar, superSayan, charging
	barImg = pygame.transform.scale(pygame.image.load("Data/Image/Energy_bar.png"), (ENERGYW+50, ENERGYH))
	pygame.draw.rect(windowSurface, YELLOW, (12, WINH - 48, energyBar, ENERGYH-2))
	windowSurface.blit(barImg, pygame.Rect(10, WINH - 50, ENERGYW, ENERGYH))
	if charging[0]:                    # if kamehameha is charging
		energyBar -= manualDrain        # decrease the energyBar with value given for manualDrain
		if energyBar < 0:
			energyBar = 0
	else:                           # if kamehameha not charging
		if superSayan:         # if SS mode on
			if energyBar > 0:       # if energy not zero
				energyBar -= ENERGYPERSECOND        # reduce the energy
		else:                       # is SS mode off
			if energyBar < MAXENERGY:           # if energy not full
				energyBar += ENERGYPERSECOND            # increase the energy
		if energyBar == 0	or energyBar == MAXENERGY:           # if energy zero or full
			energyBar += 0                              # don't  change its value

def pause(text, drawRect, x, y):                # pause the game
	pygame.mouse.set_visible(True)              # make mouse visible while paused
	while True:
		textObj, textRect = writeText(text, WHITE, 30, x, y, True)
		if (x, y) == (-1, -1):              # if (x, y) == (-1, -1), put the text at the center of the screen
			textRect.centerx = windowSurface.get_rect().centerx
			textRect.centery = windowSurface.get_rect().centery
		if drawRect:                       # if drawRect == True
			pygame.draw.rect(windowSurface, BGCOLOR, (textRect.left-2, textRect.top-5, textRect.width+4, textRect.height+10))       # Make a rectangle below the text
		windowSurface.blit(textObj, textRect)               # make the text on the screen
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				pygame.mouse.set_visible(False)         # make mouse invisible again if resumed
				return
		pygame.display.update()

def stopAllSounds():
	SOUND.goSS.stop()
	SOUND.releasing.stop()
	SOUND.charging.stop()
	SOUND.blink.stop()
	SOUND.charging_e.stop()
	SOUND.shoot.stop()

# Start of the game
while True:
	pygame.mouse.set_visible(False)
	time = score = 0                # set initial time and score to 0
	chargeTime = 1                  # charge time
	energy = []                         # make initial energy empty
	objects = []                        # make initial object empty
	topScore = topScoreFile("load")             # load top score from the 'topScore.txt' file
	energyBar = MAXENERGY                       # set the energy bar to full
	superSayan = mouseDown = False       # set supersayan and mouse chicked status to false
	charging = [False, "n"]                     # set charging to false
	# startingTexts holds texts to be displayed turn by turn on the screen
	startingTexts = ["Dragon Ball", "Move mouse cursor to move character and hold left click to attack.", "Destroy the objects and score more.", "Press 'W' and 'S' to blink up and down respectively.", "Press 'A' to go to SuperSayan Mode (2xDamage).", "Hold 'Space', then release it to use Kamehameha.", "Hold 'D', then release it to use Explosive wave.", "Press 'P' to pause and 'Esc' to close the game."]
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
			pause("Press any key. . ", False, WINW-250, WINH-50)
	playerImg = playerImage("None", superSayan)
	playerRect = playerImg.get_rect()
	playerRect.centerx = 30
	t1 = t2 = 8     # controls the time delay between the energies releases continously
	c1 = c2 = 2*FPS   # use to measure the charge time value
	while True:
		time += 1                   # increase time by 1 per frame
		if energyBar == 0 and not charging[0]:          # if energy bar empty
			superSayan = False          # turn off SS mode
			playerImg = playerImage("None", superSayan)
		if not superSayan:
			pygame.mixer.music.stop()   # if SS is off, stop the SS on music
		makeAnimatedBackground()
		displayScore()
		drawEnergyBar(0)
		windowSurface.blit(playerImg, playerRect)
		moveEnergy()
		if time%25 == 0:                # add objects on the screen when time is a multiple of 25
			makeNewObjects(time)
		moveObjects()
		if gotHit():                        # check if got hit
			if score > topScore:            # if score is higher than top score
				topScore = score            # make the score top score
			break                           # break the while loop and go to end of the code
		# event handling
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if not charging[0]:
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
					blink("up", superSayan)
				elif event.key == ord("s"):
					SOUND.blink.play()
					blink("down", superSayan)
				elif event.key == ord("a"):
					superSayan = not superSayan
					if superSayan:
						SOUND.goSS.play()
						pygame.mixer.music.play(-1, 0.0)
					playerImg = playerImage("None", superSayan)
				elif event.key == K_SPACE:
					if energyBar >= 50:             # if energy is atleast 50
						charging = [True, "k"]             # charging
						stopAllSounds()
						SOUND.charging.play()
						drawEnergyBar(50)       # reduce the enegy bar by 50
				elif event.key == ord("d"):
					if energyBar >= MAXENERGY:             # if energy is full
						charging = [True, "e"]             # charging
						stopAllSounds()
						SOUND.charging_e.play()
						drawEnergyBar(MAXENERGY)       # use all the energy
				elif event.key == K_ESCAPE:
					terminate()
			if event.type == KEYUP:
				if charging[0]:                # if charging
					if event.key == K_SPACE and charging[1] == "k":
						SOUND.charging.stop()       # stop the charging sound
						playerImg = playerImage("Release", superSayan)
						SOUND.releasing.play()      # play the kamehameha releasing sound
						kamehameha(playerImg)       # draw kamehameha image animation
						charging = [False, "n"]                # stop charging
						playerImg = playerImage("None", superSayan)
						c1 = 2*FPS
						chargeTime = 1
					elif event.key == ord("d") and charging[1] == "e":
						SOUND.charging_e.stop()       # stop the charging sound
						playerImg = playerImage("Release Wave", superSayan)
						SOUND.releasing.play()      # play the explosive wave releasing sound
						explosiveWave(playerImg)       # draw explosive image animation
						charging = [False, "n"]                # stop charging
						playerImg = playerImage("None", superSayan)
						c1 = 2*FPS
						chargeTime = 1
			if event.type == MOUSEMOTION:
				playerRect.move_ip(0, event.pos[1] - playerRect.centery)        # move playerRect to mouse's position
		if mouseDown:               # if mouse button pressed
			addNewEnergy(superSayan)            # add new energy in the screen
			playerImg = playerImage("Shoot", superSayan)
		elif not mouseDown and not charging[0]:                    # if mouse not pressed and not charging
			t1 = 8                                                              # reset t1's value to 8
			playerImg = playerImage("None", superSayan)
		if charging[0]:                                                            # if charging
			c1 += 1
			if c1%c2 == 0 and chargeTime != 4:
				chargeTime += 1
			mouseDown = False                                           # prevent shooting energy
			playerImg = playerImage("Charge", superSayan)
			# add a circular energy field while charging
			CENTER = (playerRect.centerx-10, playerRect.centery+15)     # set the circular energy field's circle
			radius = (5-chargeTime)*10                                                  # set the radius of the fiels which decreses with chargetime
			transparentSurface.fill((0, 0, 0, 0))                                       #  fill transparentSurface with an invisible colour
			if superSayan:
				pygame.draw.circle(transparentSurface, (chargeTime*50, chargeTime*50, 0, chargeTime*40), CENTER, radius)    # draw a yellow transparent circle
			else:
				pygame.draw.circle(transparentSurface, (chargeTime*50, 0, 0, chargeTime*40), CENTER, radius)           # draw a red transparent circle
			windowSurface.blit(transparentSurface, pygame.Rect(0, 0, WINW, WINH))                         # draw the transparent over the windowSurface
		pygame.mouse.set_pos(playerRect.centerx, playerRect.centery)    # move mouse to player's center
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
