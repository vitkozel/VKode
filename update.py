print("  > Please wait...")


from sre_parse import State
from tqdm import tqdm
import requests
from vkode import vkode_location
import os
import shutil
from urllib.request import urlopen


verzelocal_f = open(vkode_location + "version.saver")
verzelocal = verzelocal_f.read()
verzelocal_f.close()
from vksettings import versioncheck
verze = urlopen(versioncheck).read()
verzedek = verze.decode('utf-8')

print("  > Upgrading " + verzelocal + " to " + "VKode Windows Stable build .zip package build " + verzedek)

chunk_size = 1024
move_from = "vkode_cache/update/" + verzelocal
file_name = verzedek + ".zip"
url = "http://smartmark.jecool.net/cloud/vkode/package/" + file_name
zip_path = vkode_location + "cache/"
r = requests.get(url, stream = True)


total_size = int(r.headers['content-length'])
filename = url.split('/')[-1]

with open(filename, 'wb') as f:
	for data in tqdm(iterable = r.iter_content(chunk_size = chunk_size), total = total_size/chunk_size, unit = 'KB'):
		f.write(data)


print("  > Download completed, please wait, installing the package")

shutil.move(file_name, zip_path)

import zipfile
with zipfile.ZipFile(zip_path + file_name, 'r') as zip_ref:
    zip_ref.extractall(vkode_location)



from vksettings import statelocation
import time
from datetime import datetime

state = open(vkode_location + statelocation, "a")
cas = datetime.now()
state.write(str(cas))
state.write("\nWAKE REASON: \n" + "vkode updatet from " + verzelocal + " to " + verzedek)
state.write("\nINCLUDES:\n")
state.write("vkode" + "(" + "N/A" + ")" + "N/A" + "\n" + "N/A" + "(" + "N/A" + ")" + "N/A" + "\n" + "console" + "(" + "N/A" + ")" + "N/A" + "\n")
#state.write("ALSO MAY INCLUDE LIBRARIES:\n")
state.write("STATUS:\n")
cas = datetime.now()
state.write(str(cas) + "\n\n")
state.close()

changeversion = open(vkode_location + "version.saver", "w")
changeversion.write(verzedek)
changeversion.close()

print("  > Package installed")