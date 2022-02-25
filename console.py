print("  > Initiating local data,")

# OPEN VKSETTINGS.TXT TO EDIT SHELL BASIC SETTINGS!

import pymsgbox
import requests
from colorama import init
init()
from colorama import Fore
import os

console_location = os.path.abspath(__file__)
console_location = console_location[:-10]

print('  > External resources 1/2 loaded, ')

opensettings = open(console_location + "vksettings.txt", "r")
writesettings = open(console_location + "vksettings.py", "w")
writesettings.write(opensettings.read())
writesettings.close()
opensettings.close()

print("  > VKsettings.txt loaded and variables converted,")

#print("  > Checking for Vblock")
from vksettings import vblock
if vblock == 1:
	print(Fore.RED + "  >", "Vblock set to 1, Console will be paused shortly." + Fore.RESET)
	pymsgbox.alert('VBlock has paused the Console. This might be problem, so if you have downloaded the Dev package, try changing Vblock value in vksettings.txt', 'Vblock error')
if vblock == 2:
		print(Fore.RED + "  > Vblock is set to 2, cancelling the startup immediately!" + Fore.RESET)
		pymsgbox.alert('VBlock is blocking the Console. If you have downloaded the Dev package, try changing Vblock value in vksettings.txt', 'Vblock error')
		exit()


print("  > Vblock OK,")

from urllib.request import urlopen
import time
from datetime import datetime
clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
cas = datetime.now()
print('  > External resources 2/2 loaded, ', cas)


offline = 0
#state = 0
from vksettings import versioncheck
from vksettings import noticeversion
from vksettings import skipstartdelay
from vksettings import nula
from vksettings import mezera
from vksettings import noticeverafter
from vksettings import deletestart
from vksettings import consolerunning
from vksettings	import autodevview
from vksettings import offline
from vksettings import state
from vksettings import verzi
from vksettings import statelocation
from vksettings import comes
from vksettings import wakereason

print('  > VK Settings variables loaded,  ', cas)

if skipstartdelay == 0:
	time.sleep(1)

import vkode
global warning_sign
warning_sign = Fore.RED + "  ! " + Fore.RESET
debugl = Fore.YELLOW + ">>> " + Fore.RESET

print('  > VKode resources loaded,  ', cas)

if offline == 0:
	print(warning_sign + "Console starting in offline mode")

timeout = 3
if offline == 1:
	try:
		request = requests.get("http://google.com/robots.txt", timeout=timeout)
		offline = 1
	except (requests.ConnectionError, requests.Timeout) as exception:
		offline = 0

verze = "0"
okv = "Version check failed. Please try again later"
if offline == 1:
	verze = urlopen(versioncheck).read()
	verzedek = int(verze.decode('utf-8'))
	verzelocal_f = open(console_location + "version.saver", "r")
	verzelocal = int(verzelocal_f.read())
	if verzedek == verzelocal:
		okv = "Your VK version is up to date,"
	elif verzedek > verzelocal:
		okv = "YOUR VKODE IS NOT UPDATED! Please update VKode, vkUpdate(), "
		if noticeversion == 1:
			noticeverafter = 1
	verzelocal_f.close()

cas = datetime.now()
print('  >', okv, mezera, cas)

#print(statelocation, state)

if skipstartdelay == 0:
	time.sleep(2)


def statelog():
	state = open(console_location + statelocation, "a")
	cas = datetime.now()
	state.write(str(cas))
	state.write("\nWAKE REASON: \n" + wakereason)
	state.write("\nINCLUDES:\n")
	state.write("vkode" + "(" + verzi + ")" + comes + "\n" + "vblock" + "(" + verzi + ")" + comes + "\n" + "console" + "(" + verzi + ")" + comes + "\n")
	#state.write("ALSO MAY INCLUDE LIBRARIES:\n")
	state.write("STATUS:\n")
	cas = datetime.now()
	state.write(str(cas) + "\n\n")
	

if state == 1:
	wakereason = "console start"
	statelog()

move_f = open(console_location + "devview/files/stats/stats_console.saver", "r")
move = move_f.read()
move_int = int(move)
move_f.close()
move_int = move_int + 1
move = str(move_int)
move_f = open(console_location + "devview/files/stats/stats_console.saver", "w")
move_f.write(move)
move_f.close()

consolerunning = 1

while True:



	if vblock == 1:
		print("  >", "Vblock is set to 1, the Console has been paused until new contact.")
		pymsgbox.alert('VBlock has paused the Console. This might be problem, so if you have downloaded the Dev package, try changing Vblock value in vksettings.txt', 'Vblock error')
		break
	if vblock == 2:
		print("  > Vblock is set to 2, killing the Console immediately!")
		pymsgbox.alert('VBlock is blocking the Console. If you have downloaded the Dev package, try changing Vblock value in vksettings.txt', 'Vblock error')
		exit()

	cas = datetime.now()
	print('  > Console successfuly started, ', mezera, cas)
	if skipstartdelay == 0:
		time.sleep(0.45)

	print(nula)

	print('/\   /\   | | __  ___    __| |  ___ ')
	print('\ \ / /   | |/ / / _ \  / _` | / _ |')
	print(' \ V /    |   < | (_) || (_| ||  __/')
	print("  \_/     |_|\_\ \___/  \__,_| \___|")



	print('Powered by VKode, Created with <3 in EU, twitter.com/vkode_')
	print('www.vkode.xyz')
	print(nula)

	if noticeverafter == 1:
		print(debugl + "YOUR VKODE IS NOT UPDATED! Update VKode, vkupdate()")

	print(nula)

	if deletestart == 1:
		if skipstartdelay == 0:
			time.sleep(0.6)
		time.sleep(0.15)
		clearConsole()
		print('/\   /\   | | __  ___    __| |  ___ ')
		print('\ \ / /   | |/ / / _ \  / _` | / _ |')
		print(' \ V /    |   < | (_) || (_| ||  __/')
		print("  \_/     |_|\_\ \___/  \__,_| \___|")
		print('Powered by VKode, Created with <3 by Vit Kozel in Czechia, twitter.com/vkode_')
		print('www.vkode.gq')
		print(nula)
		if noticeverafter == 1:
			print("YOUR VKODE IS NOT UPDATED! Update VKode, vkupdate()")


	if vblock == 1:
		print("  >", "Vblock is set to 1, the Console has been paused until new contact.")
		pymsgbox.alert('VBlock has paused the Console. This might be problem, so if you have downloaded the Dev package, try changing Vblock value in vksettings.py', 'Vblock error')
		break
	if vblock == 2:
		print("  > Vblock is set to 2, killing the Console immediately!")
		pymsgbox.alert('VBlock is blocking the Console. If you have downloaded the Dev package, try changing Vblock value in vksettings.py', 'Vblock error')
		exit()

	break


while True:
	print(nula)
	text = input(' >> ')
	if text.strip() == "": continue
	result, error = vkode.run('<stdin>', text)

	if error:
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))
