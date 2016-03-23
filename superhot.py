from ctypes import *
from ctypes.wintypes import *
import sys
import time
import codecs
import colorama
import os
import subprocess

colorama.init()

superhotpath = None
superhotprocess = None

if not os.path.isdir(os.path.expanduser('~/.6kk')):
    os.mkdir(os.path.expanduser('~/.6kk'))

if os.path.isfile(os.path.expanduser('~/.6kk/superhotpath')):
    with open(os.path.expanduser('~/.6kk/superhotpath')) as pathfile:
        superhotpath = pathfile.read().strip()
        if not os.path.isfile(superhotpath):
            superhotpath = None

if not superhotpath:
    import webbrowser
    import psutil
    webbrowser.open('steam://run/322500')
    while not superhotpath:
        for process in psutil.process_iter():
            try:
                if process.name() == 'SH.exe':
                    superhotpath = process.exe()
                    process.terminate()
                    with open(os.path.expanduser('~/.6kk/superhotpath'), 'w') as pathfile:
                        pathfile.write(superhotpath)
                    break
            except:
                pass
        time.sleep(1 / 60)

superhotprocess = subprocess.Popen(superhotpath, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF



pid = superhotprocess.pid
textAddress = 0x28000010 #0x2A8F4010
textAddressFound = False
#colorAddress = 0x3A3E9FC0

testingBuffer = create_string_buffer(12)
testingBufferSize = 12

textBuffer = create_string_buffer(3072)
textBufferSize = 3072
#colorBuffer = create_string_buffer(6144)
#colorBufferSize = 6144
bytesRead = c_ulong(0)
processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

print('trying to find memory offset')

while not textAddressFound:
	textAddress = 0x28000010
	for _ in range(0x8000):
		ReadProcessMemory(processHandle, textAddress - 0x0C, testingBuffer, testingBufferSize, byref(bytesRead))
		if testingBuffer[:] == b'\x00\x00\x00\x00\x00\x00\x00\00\x00\x06\x00\x00':
			textAddressFound = True
			break
		else:
			textAddress += 0x1000

print('\003[2J')
			
lastFrame = None
while True:
	currentFrame = ''
	ReadProcessMemory(processHandle, textAddress, textBuffer, textBufferSize, byref(bytesRead))
	#ReadProcessMemory(processHandle, colorAddress, colorBuffer, colorBufferSize, byref(bytesRead))
	#currentColor = colorama.Fore.WHITE
	for i in range(24):
		for j in range(64):
			posIndex = i * 64 + j
			charIndex = posIndex * 2
			charCode = ord(textBuffer[charIndex + 1]) * 0x100 + ord(textBuffer[charIndex])
			charString = chr(charCode)
			"""
			colorIndex = posIndex * 4
			color = colorfromslice(colorBuffer[colorIndex:colorIndex + 4])
			if color != currentColor:
				string += color
				currentColor = color
			"""
			currentFrame += charString.encode(sys.stdout.encoding, 'replace').decode(sys.stdout.encoding)
	if lastFrame is None:
		output = ('\033[1;1H' + currentFrame[:64] + '\n' + currentFrame[64:128] + '\n' +
				  currentFrame[128:192] + '\n' + currentFrame[192:256] + '\n' +
				  currentFrame[256:320] + '\n' + currentFrame[320:384] + '\n' +
				  currentFrame[384:448] + '\n' + currentFrame[448:512] + '\n' +
				  currentFrame[512:576] + '\n' + currentFrame[576:640] + '\n' +
				  currentFrame[640:704] + '\n' + currentFrame[704:768] + '\n' +
				  currentFrame[768:832] + '\n' + currentFrame[832:896] + '\n' +
				  currentFrame[896:960] + '\n' + currentFrame[960:1024] + '\n' +
				  currentFrame[1024:1088] + '\n' + currentFrame[1088:1152] + '\n' +
				  currentFrame[1152:1216] + '\n' + currentFrame[1216:1280] + '\n' +
				  currentFrame[1280:1344] + '\n' + currentFrame[1344:1408] + '\n' +
				  currentFrame[1408:1472] + '\n' + currentFrame[1472:])
	else:
		output = ''
		curpos = (-1, -1)
		for i in range(24):
			for j in range(64):
				posIndex = i * 64 + j
				if currentFrame[posIndex] != lastFrame[posIndex]:
					if curpos != (j, i):
						output += '\033[' + str(i + 1) + ';' + str(j + 1) + 'H'
					output += currentFrame[posIndex]
					curpos = (j + 1, i)
	if output:
		print(output, end='')
	lastFrame = currentFrame[:]