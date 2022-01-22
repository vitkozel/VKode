
# LINES ABOVE ARE SOURCE CODES OF VKODE AND THE .VKODE FILE.
# -- 1985

# VKODE SHORTCUT
# Created in Python 3.10.0


# Copy vkode.py file to the folder
vkode_r = open("vk", "r")
vkode = vkode_r.read()
vkode_r.close()
vkode_w = open("vkode.py", "w")
vkode_w.write(vkode)
vkode_w.close()

# Copy string_with_arrows.py aswell
vkode_r = open("vk_st", "r")
vkode = vkode_r.read()
vkode_r.close()
vkode_w = open("strings_with_arrows.py", "w")
vkode_w.write(vkode)
vkode_w.close()

# Finally import vkode.py
import vkode


# Run the script
while True:
	#print("") # The startup line (delete the comment to activate)
	text = ('run("jn")') # 'jn' will be replaced with the .vkode file name
	if text.strip() == "": continue
	result, error = vkode.run('<sdin>', text) # Print the result to the Console

	# Errors:
	if error: 
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))
