#!/usr/bin/python

import time
import random
import os

class Color:
# ANSI Escape codes: print out code + string to have text display with specified color
	Black = "\033[30m"
	Red = "\033[31m"
	Green = "\033[32m"
	Yellow = "\033[33m"
	Blue = "\033[34m"
	Magenta = "\033[35;1m"
	Cyan = "\033[36m"
	White = "\033[37m"
	Grey = "\033[38;5;245m"
	Reset = "\033[00m"

	bgBlack = "\033[100m"
	bgRed = "\033[41m"
	bgGreen = "\033[42m"
	bgYellow = "\033[43m"
	bgBlue = "\033[44m"
	bgMagenta = "\033[45m"
	bgCyan = "\033[46m"
	bgWhite = "\033[47m"

def parseFish(content):
	fish = []
	fishParams = []
	numFish = int(content[:content.index("\n")])

	# Iterate through each fish animation frames
	for i in range(numFish):
		fish.append([])
		# Starting index of current fish's frames
		fishIdx = content.index("FISH %d" % (i + 1))

		# First two lines provide info on fish:
		# num of animation frames, length of fish, depth of mouth
		# animation frame order (separated by commas)
		paramStr = content[fishIdx + len("FISH %d\n" % (i + 1)):content.index("STAGE 1", fishIdx)].split("\n")
		params = paramStr[0].split(",")	# num stages, length, depth, direction, bubble
		fishParams.append((
			int(params[0]),
			int(params[1]),
			int(params[2]),
			params[3],
			params[4],
			[int(x) for x in paramStr[1].split(",")]
		))
		# Parse each stage, or animation frame and store in list of lists
		for s in range(fishParams[i][0]):
			idx = content.index("STAGE %d" % (s + 1), fishIdx)
			if s + 1 == fishParams[i][0]:	# last frame for this fish
				if i + 1 == numFish:	# last fish
					idx2 = content.index("FLOOR")
				else:			# index of next fish
					idx2 = content.index("FISH %d" % (i + 2), idx)
			else:				# index of next frame
				idx2 = content.index("STAGE %d" % (s + 2), idx)
			fish[i].append(content[idx + len("STAGE X\n"):idx2].split("\n"))
	return fish, fishParams

def colorize(str):
# black, red, green yellow, blue, magenta, cyan, white, reset
	return (str
		.replace("%K", Color.Black)
		.replace("%R", Color.Red)
		.replace("%G", Color.Green)
		.replace("%Y", Color.Yellow)
		.replace("%B", Color.Blue)
		.replace("%M", Color.Magenta)
		.replace("%C", Color.Cyan)
		.replace("%W", Color.White)
		.replace("%g", Color.Grey)
		.replace("%r", Color.Reset)
		)


def printFish(fish, fishLen, pos, dir, cols, bubble, bubbleDepth, bubblePos):
	# Print out each line individually
	for i,layer in enumerate(fish):
		bubTxt = ""

		# Find all color codes in layer and the indices
		colorIdxs = [layer.find("%")]
		if colorIdxs[0] == -1:
			colorCodes = []
		else:
			colorCodes = [layer[colorIdxs[0]:colorIdxs[0]+2]]
		numColorCodes = layer.count("%")
		layerLen = len(layer) - (numColorCodes * 2)

		while len(colorCodes) < numColorCodes:
			colorIdxs.append(layer.index("%", colorIdxs[-1] + 1))
			colorCodes.append(layer[colorIdxs[-1]:colorIdxs[-1] + 2])

	# ---------- FISH MOVING FROM LEFT TO RIGHT ---------- #
		if dir == "R":
			# Check if bubble needs to be printed inline with fish
			if bubble and -(i+1) == bubbleDepth:
				bubTxt = " " * (bubblePos - (pos - fishLen + layerLen)) + Color.Reset + "o"
			# Fish is entering frame from the left
			if pos < fishLen:
				# Print current line sliced to correct number of chars starting from the right
				if fishLen - layerLen < pos:
					cc = ""
					startIdx = -(pos - (fishLen - layerLen))
					for j in range(numColorCodes - 1, -1, -1):
						# Color code is in cutoff length but have no length when printed
						if colorIdxs[j] >= len(layer) + startIdx - 1:
							startIdx -= 2
							continue
						# Color code needs to be printed but is not included in cutoff length
						elif colorIdxs[j] < len(layer) + startIdx:
							cc = colorCodes[j]
							break
					printStr = cc + layer[startIdx:] + bubTxt
					print(colorize(printStr) + Color.Reset)
					#print(layer[startIdx:] + bubTxt)
				else:
					print("")
			# In case fish is out of frame on the right
			elif pos >= cols + fishLen:
				print("")
			# Print out current line sliced to correct number of chars starting from the left
			# (Fish is leaving frame on right)
			elif pos > cols:
				endIdx = -(pos - (cols + fishLen - 1))
				# Adjust for any color codes
				for j in range(numColorCodes):
					if colorIdxs[j] <= endIdx:
						endIdx += 2
				print(" "*(pos - fishLen) + colorize(layer[:endIdx]) + Color.Reset)
			# Otherwise, just print out the current line
			else:
				layer = colorize(layer)
				print(" "*(pos - fishLen) + layer + bubTxt)

	# ---------- FISH MOVING FROM RIGHT TO LEFT ---------- #
		elif dir == "L":
			# Check if bubble needs to be printed inline with fish
                	if bubble and -(i+1) == bubbleDepth:
                	        bubTxt = Color.Reset + "o" #" " * (bubblePos - (pos - fishLen + len(layer))) + "o"
                	# Fish is entering frame from the right
                	if pos < fishLen:
                	        endIdx = pos
				for j in range(numColorCodes):
					if colorIdxs[j] <= endIdx:
						endIdx += 2
				# Print current line sliced to correct number of chars starting from the right
                	        print(" " * (cols - pos - min(1, len(bubTxt))) + bubTxt + colorize(layer[:endIdx])+ Color.Reset)
                	# In case fish is out of frame on the left
                	elif pos >= cols + fishLen:
                	        print("")
                	# Print out current line sliced to correct number of chars starting from the right
                	# (Fish is leaving frame on left)
                	elif pos > cols:
				cc = ""
				startIdx = pos - cols
				for j in range(numColorCodes):
					if colorIdxs[j] <= startIdx:
						startIdx += 2
						cc = colorCodes[j]
                	        print(colorize(cc + layer[startIdx:]) + Color.Reset)
                	        #print(layer[-(pos - (cols + fishLen - 1))])
                	# Otherwise, just print out the current line
                	else:
                	        print(" "*(cols - pos) + bubTxt + colorize(layer))

def printBubble(pos, depth, fishDepth, cols, pop, waveMove):
	# Print wave
	if waveMove:
		print(Color.Blue + "\n\\" + "/\\"*((cols - 1) / 2) + Color.Reset)
	else:
		print(Color.Blue + "\n" + "/\\"*((cols - 1) / 2) + "/" + Color.Reset)
	# Print blank lines between wave and bubble
	print("\n"*(fishDepth - depth - 4)) # subtract 4 as buffer for wave
	if pop:
		print(" "*pos + "*"),
	else:
		print(" "*(pos) + "o"),
	# Print blank lines below bubble
	print("\n"*(depth))

def printFloor(floor, cols, fishDepth, fishHt, rows, animate):
	# Print blank lines above floor
	print("\n"*(rows - fishDepth - len(floor) - fishHt - 1))
	# Print each line individually (each multiple times to span across the terminal window)
	for layer in floor:
		if len(layer) == 0:
			continue
		# Animate by swapping characters in the seaweed
		# Also replace color placeholders (%?) with ANSI escape code
		#layer = colorize(layer)
		numCC = layer.count("%")
		num = float(cols) / (len(layer) - (numCC * 2))
		layerLen = int((num - int(num)) * (len(layer) - numCC * 2)) + numCC * 2
		if 9 <= layerLen <= 13:
			layerLen = 8
		if animate:
			print(colorize(layer
				.replace("(( ","||")
				.replace(" ))","(( ")
				.replace("||"," ))")) * int(num)) + (
			colorize(layer[:layerLen])
				.replace("(( ","||")
				.replace(" ))","(( ")
				.replace("||"," ))")
				.replace("%",""))
		else:
			print(colorize(layer) * int(num)) + colorize(layer[:layerLen])\
				.replace("%","")

def main():
	# Read text file with fish/floor ASCII artwork
	content = ""
	with open("fish_art.txt", 'r') as f:
		content = f.read()
	fish, fishParams = parseFish(content)
	floor = content[content.index("FLOOR")+len("FLOOR\n"):].split("\n")

	pause = 0.1		# Time in seconds to pause between frames
	fishID = 0		# Which fish is displayed
	fishPos = 0		# Fish position x-axis (front of snoot)
	fishExists = False	# Is fish in frame
	fishDepth = 0		# Fish depth y-axis
	bubbleDepth = 0		# starting depth of bubble (0 is the line above the fish)
	bubblePos = 0		# Bubble position (always starts at current fishPos)
	bubble = False		# Bubble exists
	bubblePopped = False	# Bubble pops the next frame
	bubbleJitter = False	# Bubble "jitters", or moves side to side as it rises
	frames = 0		# Number of elapsed frames
	waveMove = False	# Wave moves side to side
	waveFreq = 5		# how often (in frames) waves animate

	# Get dimensions of terminal window
	rows, cols = os.popen('stty size', 'r').read().split()
	rows = int(rows)
	cols = int(cols)

	# Check if terminal window is big enough
	if rows < 24 or cols < 30:
		print("Terminal window is too small. Must be at least 30x24")

	# Clear out terminal window
	print("\n"*(rows))

	while True:
		if fishExists:
			# Print stages 1-3
			for j in fishParams[fishID][5]:		# stage order from fishParams
				# Determine if bubble is produced this "frame"
				if fishParams[fishID][4] == "T" and not bubble and fishPos < cols - 1:
					bubble = (random.random() < 0.05)
					if bubble:
						if fishParams[fishID][3] == "R":
							bubblePos = fishPos
						elif fishParams[fishID][3] == "L":
							bubblePos = cols - fishPos
						bubbleDepth = fishParams[fishID][2]
				if bubble and bubbleDepth >= 0:
					# 5% chance to pop bubble but guaranteed above certain depth
					bubblePopped = bubbleDepth >= 0 and \
						(random.random() < 0.05 or 
						bubbleDepth >= fishDepth - 5)
					printBubble(bubblePos, bubbleDepth, fishDepth, cols, bubblePopped, waveMove)
					# Reset bubble attributes
					if bubblePopped:
						bubble = False
						#bubblePopped = False
						#bubbleDepth = 0
						bubbleJitter = False
				elif not bubble and bubblePopped:
					printBubble(bubblePos, bubbleDepth, fishDepth, cols, bubblePopped, waveMove)
					bubblePopped = False
					bubbleDepth = 0
				# Print wave and blank lines above fish
				else:
					if waveMove:
						print(Color.Blue + "\n\\" + "/\\"*((cols - 1) / 2) + Color.Reset)
					else:
						print(Color.Blue + "\n" + "/\\"*((cols - 1) / 2) + "/" + Color.Reset)
					print("\n"*(fishDepth - 3)) #(len(fish[fishID][0]) - 2) ))

				# Print bubble inline with fish
				printFish(fish[fishID][j], fishParams[fishID][1], fishPos, fishParams[fishID][3], cols, bubble, bubbleDepth, bubblePos)

				# print blank lines and floor below fish
				printFloor(floor, cols, fishDepth, len(fish[fishID][0]), rows, waveMove)

				# Adjust bubble position and depth as needed
				if bubble:
					bubbleDepth += 1
					bubbleJitter = not bubbleJitter
					if bubbleJitter:
						bubblePos += 1
					else:
						bubblePos -= 1

				# increase number of frames, adjust wave movement, and sleep
				frames += 1
				fishPos += 1
				if frames % waveFreq == 0:
					waveMove = not waveMove
				if fishPos >= (cols + fishParams[fishID][1] - 1):	# Fish moved out of frame (17 is length of fish)
					fishExists = False
					fishPos = 0
					break
				time.sleep(pause)
		else:
			# Print wave and floor
			if waveMove:
				print(Color.Blue + "\n\\" + "/\\"*((cols - 1) / 2) + Color.Reset)
			else:
				print(Color.Blue + "\n" + "/\\"*((cols - 1) / 2) + "/" + Color.Reset)
			if (rows > 24):		# I don't know why this is needed
				print("\n"*(rows / 2 + 2))
			else:
				print("\n"*(rows / 2 + 1))
			printFloor(floor, cols, (rows / 2), 5, rows, waveMove)
			# Increase frames and adjust wave movement
			frames += 1
			if frames % waveFreq == 0:
				waveMove = not waveMove
			# Check if fish appears next frame
			fishExists = random.random() < 0.05
#			fishExists = True
			fishID = random.randint(0, len(fish) - 1)
#			fishID = 11
			fishDepth = random.randint(4, rows - len(floor) - len(fish[fishID][0]) - 1)
			time.sleep(pause)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		os.system("clear")
		print("done")
