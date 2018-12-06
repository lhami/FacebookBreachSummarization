
'''
This function is used to fix the encoding issues in our text and remove the 
failed ascii conversions that appear as /xc/xf and so on in our dataset
'''

fname = "cleaned.json"

def main():
	with open(fname, 'r') as myfile:
		data=myfile.read()

	res = data.decode('ascii', errors='ignore').encode('utf-8')

	print "Finished Re-encoding"

	text_file = open("new1.json", "w")
	text_file.write(res)
	text_file.close()

main()
