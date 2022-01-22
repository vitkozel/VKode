print("  > Initiating Dev view")

# OPEN VKSETTINGS.PY TO EDIT SHELL BASIC SETTINGS!

import pymsgbox

print("  > Vblock check skipped in Dev view")
from vksettings import vblock

print("  > Loading external libraries")

from urllib.request import urlopen
import vkode
import time
from datetime import datetime
import os
clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

cas = datetime.now()
print('  > Done, Loading VKode Shell Settings,  ', cas)

from vksettings import versioncheck
from vksettings import noticeversion
from vksettings import skipstartdelay
from vksettings import nula
from vksettings import mezera
from vksettings import noticeverafter
from vksettings import deletestart
from vksettings import consolerunning

while True:

    
	cas = datetime.now()
	print('  > Done, Starting VKode Console in Dev view,', mezera, cas)
	cas = datetime.now()
	print('  > VKode Console Successfuly started in Dev view,', mezera, cas)
	print(nula)

	print('    ____                 _    ___ ')
	print('   / __ \___ _   __     | |  / (_)__ _      __')
	print('  / / / / _ \ | / /     | | / / / _ \ | /| / /')
	print(" / /_/ /  __/ |/ /      | |/ / /  __/ |/ |/ / ")
	print("/_____/\___/|___/       |___/_/\___/|__/|__/ ")

	print(nula)


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
