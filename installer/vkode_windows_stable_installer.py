print("DO NOT CLOSE THIS WINDOW!")
print("VKode installer")
print("")
from asyncio import SubprocessProtocol
from turtle import clear
from pymsgbox import *
import tkinter
from tkinter import filedialog
import os
import subprocess
import wget
from urllib.request import urlopen
import shutil
import zipfile
import winshell
from pathlib import Path
directory = __file__

print(" 1.  Hello! Thank you for your interest in VKode.")
alert(text='Hello!\nThank you for your interest in VKode.', title='Install VKode', button='OK')
print(" 2.  Choose some safe location for VKode. SSD recommended.")
alert(text='Choose some safe location for VKode. SSD recommended.', title='Install VKode', button='OK')
print(" 3.  Please proceed to the file browser window.")
print("")
global file_path_variable

def dir():
    global file_path_variable
    makedir = 1

    root = tkinter.Tk()
    root.withdraw()
    def search_for_file_path ():
        currdir = os.getcwd()
        tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='VKode install directory')
        if len(tempdir) > 0:
            print ("You chose: %s" % tempdir)
        return tempdir


    file_path_variable = search_for_file_path()
    file_path_variable = file_path_variable + "/vkode"

    proceed = 0
    if os.path.isdir(file_path_variable) == True:
        print("The directory already exists")
        if len(os.listdir(file_path_variable) ) == 0:
            print("The directory does exist, but it's empty, proceeding")
            makedir = 0
            proceed = 1
        else:
            alert('Chosen directory already exists. Please, clear the directory or choose other location.', 'VKode Installation Error')
            dir()
    else:
        proceed = 1

    print("")

    if proceed == 1:
        proceed = 0
        print(" 4.  VKode will be installed in ", file_path_variable)
        print("")

        if makedir != 0:
            print("Creating directory")
            os.mkdir(file_path_variable)
        file_path_variable = file_path_variable + "/"

        confirm_window = confirm(text='VKode will be installed to ' + file_path_variable + "\nDo you wish to proceed?", title='VKode installer', buttons=['INSTALL', 'Change directory', 'Cancel installation'])
        if confirm_window == "Change directory":
            print("Change directory requested")
            dir()
        elif confirm_window == "Cancel installation":
            print("Cancelling installation")
            exit()       
dir()

print("")
print(" 5.  Installer will now download the VKode. It might take a minute")
print("")

verze = urlopen("http://smartmark.jecool.net/cloud/vkode/ver/ver.txt").read()
verze = verze.decode('utf-8')
file_name = str(verze) + ".zip"
download_url = "http://smartmark.jecool.net/cloud/vkode/package/" + file_name
print("VKODE Windows Stable (from installer), build " + verze)

wget.download(download_url)
print("  DONE")

shutil.move(file_name, file_path_variable)

print("")
print(" 6. Downloading completed, installing..")
print("")


with zipfile.ZipFile(file_path_variable + file_name, 'r') as zip_ref:
    zip_ref.extractall(file_path_variable)

os.remove(file_path_variable + file_name)

print("Package extracted")
