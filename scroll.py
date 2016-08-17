import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

OFF = 0
ON  = 1
COLS = 16
ROWS = 7

# GPIO pin assignments
out = {
	"SER_1" : 3,
	"CLK_1" : 5,
	"CLR_1" : 7,
	"SER_2" : 11,
	"CLK_2" : 13,
	"CLR_2" : 15,
	"OE"    : 19
}

# "bitmaps" for characters
chars = {
	'H': [[1,0,1],[1,0,1],[1,1,1],[1,0,1],[1,0,1]],
	'E': [[1,1,1],[1,0,0],[1,1,1],[1,0,0],[1,1,1]],
	'L': [[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,1,1]],
	'O': [[0,1,1,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
	'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,1,0,1],[0,1,0,1,0]],
	'R': [[1,1,1,0],[1,0,0,1],[1,1,1,0],[1,0,0,1],[1,0,0,1]],
	'D': [[1,1,0],[1,0,1],[1,0,1],[1,0,1],[1,1,0]],
	'!': [[0,1,0],[0,1,0],[0,1,0],[0,0,0],[0,1,0]],
	' ': [[0],[0],[0],[0],[0]]
}

def set(s, b):
	GPIO.output(out[s], b)

def tick(s):
	set(s, OFF)
	set(s, ON)

def show(b):
	set("OE", not b)

def dispMatrix(m):
    # clear row shift register and set first bit
	tick("CLR_2")
	set("SER_2", ON)
	tick("CLK_2")
	set("SER_2", OFF)
	for j in range(ROWS):
	    # increment row shift register with CLK_2
	    # and clear column registers with CLR_1
		show(OFF)
		tick("CLK_2")
		tick("CLR_1")
		rc = 0
		for i in range(COLS):
		    # for each column tick the CLK_1 pin
		    # with SER_1 on for 1 bits, off for 0
			if m[j][COLS-1-i]: 
				rc += 1
				set("SER_1", ON)
				tick("CLK_1")
				set("SER_1", OFF)
			else:
				tick("CLK_1")
		tick("CLK_1")
		# ugly hack: adjust time row is lit depending
		# on the number of lit LEDs on the row
		# to make up for shortcomings in board design
		show(ON)
		sleep(0.00015 * rc)
		show(OFF)
		sleep(0.00015 * (COLS - rc))

for (k,v) in out.items():
	GPIO.setup(v, GPIO.OUT)

# clear shift registers
tick("CLR_1")
tick("CLR_2")

T = "HELLO WORLD! "

# create bit-matrix for string T
Tmat = [[],[],[],[],[]]
for c in T:
	for i in range(5):
		Tmat[i] += chars[c][i] + [0]

Tlen = len(Tmat[0])
Tmat = [[0]*Tlen] + Tmat + [[0]*Tlen]

for i in range(len(Tmat)):
	print(Tmat[i])

# loop for a while
for x in range(1000):
	if not x % 4:
	    # the LED matrix isn't large enough 
	    # to display the entire message
	    # so we scroll the bitmap on every 4th loop
		for i in range(len(Tmat)):
			Tmat[i] = Tmat[i][1:]+[Tmat[i][0]]
    # take a slice of every row that will fill the display
	M = [Tmat[i][:COLS] for i in range(ROWS)]
	dispMatrix(M)
	
show(OFF)
tick("CLR_1")
tick("CLR_2")

GPIO.cleanup()

