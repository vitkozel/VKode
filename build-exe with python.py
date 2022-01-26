# .VKODE > EXE BUILDER
# This script will generate a python script which will run the .vkode code. After that, Python will export the .py file to .exe
# The script solution is not optimal since it has been written to work on as most devices as possible.



import os # Library needed to generate the Shortcut
import pathlib # Library needed to get the path
import time
from unicodedata import name
import shutil

from gevent import sleep # Library needed to get the time
location = str(pathlib.Path(__file__).parent.resolve()) # Getting location of this file
location = location + "\\"
run = os.getcwd()

# Takes original .vkode file location writed in Cache, located in cache/buildtake.saver
buildtakefile = open(location + "cache/buildtake.saver")
buildtake = buildtakefile.read()
buildtakefile.close()

# Asks for some more information first
#buildto = input("TO:    ") # Final project folder destination path
buildas = input("NAME:  ") # Name of the final file
#buildpth = buildto + "\\" + buildas # Path to final file

# Asks if you really want to proceed
ask = 1
while ask == 1:
    print("  > VKode and Python will now build " + buildtake + " to .exe file. Are you sure you want to continue?")
    yesno = input("y/n > ")

    if yesno == "y":
        print("  > Proceeding, please wait")
        ask = 0
    elif yesno == "n":
        print("  > Cancelling process")
        exit()
    else:
        print("  > yes or no expected, please try again")
ask = 0

start_time = time.time() # Begins the timer

# Creates folder for the build project in buildto/buildas = buildpth
print("  > Saving data into the VKode's cache folder")
path = os.getcwd()
buildto = location + "cache\\" + buildas
os.mkdir(buildto)

# Copies buildtake files to buildpth with the worst solution possible
print("  > Copying " + buildtake)
readbuildtake = open(buildtake, "r")
readedbuildtake = readbuildtake.read()
readbuildtake.close()
writebuildtake = open(buildto + "\\" + buildas + ".vkbuild", "w")
writebuildtake.write(readedbuildtake)
writebuildtake.close()

# Starts generating .py file (Shortcut) that will run the .vkode file when started
print("  > Generating Shortcut")
readshortcut = open(location + "shortcut.py", "r")
readedshortcut = readshortcut.read()
readshortcut.close()
shortcutlocation = buildto + "\\" + buildas + ".py"
writeshortcut = open(shortcutlocation, "w")
wshort = readedshortcut.replace("1984", buildas + ".vkbuild") # Replaces the 1984 inside the shorcut code
writeshortcut.write(wshort)
writeshortcut.close()

print("  > Generating VKode")
strings_f = open(location + "strings_with_arrows.py", "r") # File needed to run .vkode file
strings = strings_f.read()
strings_f.close()
strings_w = open(buildto + "\\" + "strings_with_arrows.py", "w")
strings_w.write(strings)
strings_w.close()

vkode_f = open(location + "vkode_build.py", "r") # Special version of vkode.py
vkode = vkode_f.read()
vkode_f.close()
vkode_w = open(buildto + "\\" + "vkode_build.py", "w")
vkode_w.write(vkode)
vkode_w.close()

# Finally contacting Python to make the exe
print("  > Contacting Python")
command = 'pyinstaller --noconfirm --onedir --console --no-embed-manifest  "' + shortcutlocation + '"' # Generates the command line
import subprocess # Built-in library to use CMD
print("  > Generating .exe")
time.sleep(0.2)
print("  > Contacting Python with  " + command)
time.sleep(1) # Wait a second to make it more dramatic
subprocess.call(command, shell=True) # Calls the Python

time.sleep(0.5)
print("  > Finishing build, please wait")

result = run + "\\dist\\" + buildas + "\\"

copy_vkbuild_r = open(buildto + "\\" + buildas + ".vkbuild", "r")
copy_vkbuild = copy_vkbuild_r.read()
copy_vkbuild_r.close()
copy_vkbuild_w = open(result + buildas + ".vkbuild", "w")
copy_vkbuild_w.write(copy_vkbuild)
copy_vkbuild_w.close()

time.sleep(0.2)
end_time = time.time() # Stops the timer
time_lapsed = end_time - start_time # Calculate the time

print("  > Build finished, busy for " + str(time_lapsed)) # Finish line
time.sleep(0.2)
os.startfile(result)