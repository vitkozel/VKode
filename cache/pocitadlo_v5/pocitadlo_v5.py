# VKODE SHORTCUT
# Created in Python 3.10.0


import vkode_build


# Run the script
while True:
	#print("") # The startup line (delete the comment to activate)
	text = ('run("pocitadlo_v5.vkbuild")') # 'pocitadlo_v5.vkbuild' will be replaced with the .vkode file name
	if text.strip() == "": continue
	result, error = vkode_build.run('<sdin>', text) # Print the result to the Console

	# Errors:
	if error: 
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))
