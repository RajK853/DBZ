import pygame, sys, random, os
from pygame.locals import *

pygame.init()
# Set up window, BGmusic and clock
WINW = 800
WINH = 500
windowSurface = pygame.display.set_mode((WINW, WINH))
pygame.display.set_caption("Dragon Ball")
mainClock = pygame.time.Clock()
FPS = 40
pygame.mixer.music.load("Data/Sound/SS_mode_on.wav")

# Set up color
BGCOLOR = (103, 141, 159)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)
YELLOW = (255, 255, 0)

# set up game constants
STARMINSIZE = 2
STARMAXSIZE = 8
STARSPEED = 2
stars = []
PLAYERIMGW = 35
PLAYERIMGH = 80
BLINKDISTANCE = PLAYERIMGH+40
KAMEHAMEHA = {"rect" : pygame.Rect(0, 0, 0, 0), "damage" : 100}
MAXENERGY = 100
ENERGYBARW = 100
ENERGYBARH = 50
ENERGYPERSECOND = 0.5
ENERGYSPEED = 5
ENERGYW = 55
ENERGYH = 25
ENERGYDMG = 10
energy = []     # stores the rectangle information and the image data of each energy as a dictionary in this list
OBJMINSIZE = 25
OBJMAXSIZE = 50
OBJMINSPEED = 1
OBJMAXSPEED = 5
OBJECTRATE = 3
objects = []
PLANETRADIUS = 400
PLANETSPEED = 1
PLANETLIFE = 200

class SOUND:    # Holds all the sound files' locations and names
	goSS = pygame.mixer.Sound("Data/Sound/Go_SS.wav")
	charging = pygame.mixer.Sound("Data/Sound/Charging.wav")
	releasing = pygame.mixer.Sound("Data/Sound/Releasing.wav")
	blink = pygame.mixer.Sound("Data/Sound/Blink.wav")
	shoot = pygame.mixer.Sound("Data/Sound/Shoot.wav")

def makeAnimatedBackground():
	windowSurface.fill(BGCOLOR)
	starSize = random.randint(STARMINSIZE, STARMAXSIZE)
	starImg = pygame.transform.scale(pygame.image.load("Data/Image/star.png"), (starSize, starSize))
	stars.append({"rect": pygame.Rect(WINW, random.randint(0, WINH), 0, 0), "image" : starImg})
	for s in stars[:]:
		windowSurface.blit(s["image"], s["rect"])
		s["rect"].move_ip(-STARSPEED, 0)
		if s["rect"].right < 0:
			stars.remove(s)

def makeNewObjects(time):       # adds new object on the screen according to the time.
	if time%25 == 0:
		objectSize = random.randint(OBJMINSIZE, OBJMAXSIZE)
		objectImg = pygame.transform.scale(random.choice([pygame.image.load("Data/Image/asteroid1.png"), pygame.image.load("Data/Image/asteroid2.png"), pygame.image.load("Data/Image/asteroid3.png")]), (objectSize, objectSize))
		objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(OBJMINSPEED, OBJMAXSPEED), "life" : [objectSize, objectSize], "image" : objectImg})
	if time%100 == 0:
		n = int((time/100)/5)
		if n > 5:
			n = 5
		for i in range(n):              # Adds more comets in the screen as the time passes by
			objectSize = random.randint(OBJMINSIZE, OBJMAXSIZE)
			objectImg = pygame.transform.scale(pygame.image.load("Data/Image/comet.png"), (objectSize, objectSize))
			objects.append({"rect" : pygame.Rect(WINW, random.randint(0, WINH-objectSize), objectSize, objectSize), "speed" : random.randint(OBJMINSPEED, OBJMAXSPEED), "life" : [objectSize, objectSize], "image" : objectImg})
	if time%1000 == 0:
		if (time/1000) < 3:
			objects.append({"rect" : pygame.Rect(WINW, 0, PLANETRADIUS, PLANETRADIUS), "speed" : PLANETSPEED, "life" : [PLANETLIFE, PLANETLIFE], "image" : pygame.transform.scale(pygame.image.load("Data/Image/Planet.png"), (PLANETRADIUS, PLANETRADIUS))})
		else:
			objects.append({"rect" : pygame.Rect(WINW, 0, PLANETRADIUS, PLANETRADIUS), "speed" : PLANETSPEED, "life" : [2*PLANETLIFE, 2*PLANETLIFE], "image" : pygame.transform.scale(pygame.image.load("Data/Image/Planet.png"), (PLANETRADIUS+100, PLANETRADIUS+100))})

def moveObjects():      # Moves the objects to left
	global score
	for o in objects[:]:
		o["rect"].move_ip(-o["speed"], 0)
		windowSurface.blit(o["image"], o["rect"])
		for e in energy[:]:
			if e["rect"].colliderect(o["rect"]):
				o["life"][0] -= e["damage"]
				energy.remove(e)
				if o["life"][0] <= 0:
					score += o["life"][1]
					objects.remove(o)

def kamehameha(playerImg):
	global score, superSayan
	KAMEHAMEHA["rect"].width = 0
	KAMEHAMEHA["rect"].height = PLAYERIMGH+40
	KAMEHAMEHA["rect"].left = playerRect.right
	KAMEHAMEHA["rect"].centery = playerRect.centery
	if superSayan:
		KAMEHAMEHA["damage"] = 200
	else:
		KAMEHAMEHA["damage"] = 100
	while KAMEHAMEHA["rect"].right < WINW+50:
		kamehamehaImg = pygame.transform.scale(pygame.image.load("Data/Image/kamehameha.png"), (KAMEHAMEHA["rect"].width, KAMEHAMEHA["rect"].height))
		makeAnimatedBackground()
		moveObjects()
		moveEnergy()
		displayScore()
		superSayan = False
		drawEnergyBar(0)
		KAMEHAMEHA["rect"].width += ENERGYSPEED
		windowSurface.blit(playerImg, playerRect)
		windowSurface.blit(kamehamehaImg, KAMEHAMEHA["rect"])
		for o in objects[:]:
			windowSurface.blit(o["image"], o["rect"])
			if KAMEHAMEHA["rect"].colliderect(o["rect"]):
				o["life"][0] -= KAMEHAMEHA["damage"]
				if o["life"][0] <= 0:
					score += o["life"][1]
					objects.remove(o)
		pygame.display.update()
		mainClock.tick(FPS)
	if KAMEHAMEHA["rect"].right > WINW:
		SOUND.releasing.stop()
	if KAMEHAMEHA["damage"] == 200:
		superSayan = True

def addNewEnergy(superSayan):       # Adds new energy dictionary to the list energy
	global t1, t2
	if superSayan:
		energyImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Energy.png"), (ENERGYW, ENERGYH))
		x = 2
	else:
		energyImg = pygame.transform.scale(pygame.image.load("Data/Image/Energy.png"), (ENERGYW, ENERGYH))
		x = 1
	energyRect = energyImg.get_rect()
	energyRect.centery = playerRect.centery
	energyRect.left = playerRect.right + 5
	t1 += 1
	if t1%t2 == 0 or t1 == 9:
		SOUND.shoot.play()
		energy.append({"rect" : energyRect, "image" : energyImg, "damage" : x*ENERGYDMG})

def moveEnergy():
	# move the energies forward
	for e in energy[:]:
		e["rect"].move_ip(ENERGYSPEED, 0)
		windowSurface.blit(e["image"], e["rect"])
		if e["rect"].left > WINW:
			energy.remove(e)

def gotHit():
	for o in objects:
		if playerRect.colliderect(o["rect"]):
			return True
	return False

def blink(dir, superSayan):
	global playerRect
	finalRect = pygame.Rect(0, 0, PLAYERIMGW, PLAYERIMGH)
	if superSayan:
		playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Blink.png"), (PLAYERIMGW, PLAYERIMGH))
	elif not superSayan:
		playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Blink.png"), (PLAYERIMGW, PLAYERIMGH))
	if dir == "down":
		move = BLINKDISTANCE
	elif dir == "up":
		move = -BLINKDISTANCE
	finalRect = playerRect.move(0, move)
	if finalRect.bottom > WINH:
		finalRect.bottom = WINH
	if finalRect.top < 0:
		finalRect.top = 0
	pygame.mouse.set_pos(finalRect.centerx, finalRect.centery)
	windowSurface.blit(playerImg, playerRect)
	windowSurface.blit(playerImg, finalRect)
	pygame.display.update()
	pygame.time.wait(150)
	playerRect = finalRect

def playerImage(task, superSayan):
	if superSayan:
		if task == "None":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Normal.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Shoot":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Shooting.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Charge":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Charging.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/SS_Releasing.png"), (PLAYERIMGW, PLAYERIMGH))
	else:
		if task == "None":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Normal.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Shoot":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Shooting.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Charge":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Charging.png"), (PLAYERIMGW, PLAYERIMGH))
		elif task == "Release":
			playerImg = pygame.transform.scale(pygame.image.load("Data/Image/Releasing.png"), (PLAYERIMGW, PLAYERIMGH))
	return playerImg

def terminate():
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
	if mode == "load":          # Load score
		if not os.path.isfile("Data/Image/topScore.txt"):
			return 0
		else:
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
					pause("Press a key loser!")
					return 0
				score += str(ord(i)-ord("a"))
			return int(score)
	if mode == "save":          # Save score
		eScore = ""         # encrypt score before storing
		for i in str(topScore): eScore += str(chr(ord("a")+int(i)))
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

def drawEnergyBar(manualDrain):
	global energyBar, superSayan, charging
	barImg = pygame.transform.scale(pygame.image.load("Data/Image/Energy_bar.png"), (ENERGYW+50, ENERGYH))
	pygame.draw.rect(windowSurface, YELLOW, (12, WINH - 48, energyBar, ENERGYH-2))
	windowSurface.blit(barImg, pygame.Rect(10, WINH - 50, ENERGYW, ENERGYH))
	if charging:
		if manualDrain == 50 or manualDrain == 0:
			energyBar -= manualDrain
			if energyBar < 0:
				energyBar = 0
	else:
		if superSayan:
			if energyBar > 0:
				energyBar -= ENERGYPERSECOND
		else:
			if energyBar < MAXENERGY:
				energyBar += ENERGYPERSECOND
		if energyBar == 0	or energyBar == MAXENERGY:
			energyBar += 0

def pause(text, drawRect, x, y):
	pygame.mouse.set_visible(True)
	while True:
		textObj, textRect = writeText(text, WHITE, 30, x, y, True)
		if (x, y) == (-1, -1):
			textRect.centerx = windowSurface.get_rect().centerx
			textRect.centery = windowSurface.get_rect().centery
		if drawRect:
			pygame.draw.rect(windowSurface, BGCOLOR, (textRect.left-2, textRect.top-5, textRect.width+4, textRect.height+10))
		windowSurface.blit(textObj, textRect)
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				pygame.mouse.set_visible(False)
				return
		pygame.display.update()

# Start of the game
while True:
	pygame.mouse.set_visible(False)
	time = score = 0
	energy = []
	objects = []
	topScore = topScoreFile("load")
	energyBar = MAXENERGY
	superSayan = charging = mouseDown = False
	startingTexts = ["Dragon Ball", "Move mouse cursor to move character and hold left click to attack.", "Destroy the objects and score more.", "Press 'W' and 'S' to blink up and down respectively.", "Press 'A' to go to SuperSayan Mode (2xDamage).", "Hold 'Space', then release it to use Kamehameha.", "Press 'P' to pause and 'Esc' to close the game."]
	wallpaper = pygame.transform.scale(pygame.image.load("Data/Image/Welcome.jpg"), (WINW, WINH))
	for t in range(len(startingTexts)):
		windowSurface.blit(wallpaper, pygame.Rect(0, 0, WINW, WINH))
		if t == 0:
			tempText, textRect = writeText(startingTexts[t], WHITE, 50, 0, 0, True)
		else:
			tempText, textRect = writeText(startingTexts[t], TEAL, 24, 0, 0, True)
		textRect.centerx = windowSurface.get_rect().centerx
		textRect.centery = windowSurface.get_rect().centery-50
		windowSurface.blit(tempText, textRect)
		pygame.display.update()
		if t == len(startingTexts)-1:
			pause("Press any key to start the game.", False, -1, -1)
		else:
			pause("Press any key. . ", False, WINW-250, WINH-50)
	playerImg = playerImage("None", superSayan)
	playerRect = playerImg.get_rect()
	playerRect.centerx = 30
	t1 = t2 = 8     # controls the time delay between the energies releases continously
	while True:
		time += 1
		if energyBar == 0:
			superSayan = False
			playerImg = playerImage("None", superSayan)
		if not superSayan:
			pygame.mixer.music.stop()
		makeAnimatedBackground()
		displayScore()
		drawEnergyBar(1)
		windowSurface.blit(playerImg, playerRect)
		moveEnergy()
		if time%25 == 0:
			makeNewObjects(time)
		moveObjects()
		if gotHit():
			if score > topScore:
				topScore = score
			break
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if not charging:
				if event.type == MOUSEBUTTONDOWN:
					mouseDown = True
				if event.type == MOUSEBUTTONUP:
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
					if energyBar >= 50:
						charging = True
						SOUND.charging.play()
						drawEnergyBar(0)
				elif event.key == K_ESCAPE:
					terminate()
			if event.type == KEYUP:
				if charging:
					if event.key == K_SPACE:
						SOUND.charging.stop()
						playerImg = playerImage("Release", superSayan)
						drawEnergyBar(50)
						SOUND.releasing.play()
						kamehameha(playerImg)
						charging = False
						playerImg = playerImage("None", superSayan)
			if event.type == MOUSEMOTION:
				playerRect.move_ip(0, event.pos[1] - playerRect.centery)
		if mouseDown:
			addNewEnergy(superSayan)
			playerImg = playerImage("Shoot", superSayan)
		elif not mouseDown and not charging:
			t1 = 8
			playerImg = playerImage("None", superSayan)
		if charging:
			mouseDown = False
			playerImg = playerImage("Charge", superSayan)
		pygame.mouse.set_pos(playerRect.centerx, playerRect.centery)
		pygame.display.update()
		mainClock.tick(FPS)
	# Stop all currently playing sounds
	SOUND.charging.stop()
	SOUND.releasing.stop()
	SOUND.goSS.stop()
	pygame.mixer.music.stop()
	writeText("Game Over!", WHITE, 30, (WINW/2)-85, (WINH/2)-30, False)
	pygame.display.update()
	pygame.time.wait(900)
	if score == topScore:
		text, rect = writeText("New Top Score: %s" % str(score), YELLOW, 30, 0, 0, True)
	else:
		text, rect = writeText("Your Score: %s" % str(score), WHITE, 30, 0, 0, True)
	rect.centerx = windowSurface.get_rect().centerx
	rect.centery = windowSurface.get_rect().centery
	pygame.draw.rect(windowSurface, BGCOLOR, rect)
	windowSurface.blit(text, rect)
	pygame.display.update()
	pygame.time.wait(3000)
	pause("Press any key to play again.", True, -1, -1)
	topScoreFile("save")
