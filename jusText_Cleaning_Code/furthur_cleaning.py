import json
import copy
import re

fname = "cleaned.json"

def read_input_file():
	with open(fname) as f:
		content = f.readlines()
	original_content = [json.loads(x) for x in content]
	lowercase_content = [json.loads(x.lower()) for x in content]

	return (original_content, lowercase_content)

def write_output_file(data):
	new_file = open("new2.json", "w")
	for line in data:
		new_file.write(json.dumps(line) + "\n")
	new_file.close()

def documentIsGood(doc):
	#titles
	if ("twitter" == doc['title'] or
			"recent news |  whatshaking | current news feeds" == doc['title'] or
			"objective news" == doc['title'] or
			"landing page" == doc['title'] or
			"401" in doc["title"]):
		print "title=", doc["title"]
		return False

	#originalurls
	if ("money.us" in doc['originalurl'] or 
			"ti.me" in doc['originalurl'] or
			"nakedcapitalism" in doc["originalurl"] or
			"reddit" in doc['originalurl']):
		print "originalurl=", doc['originalurl']
		return False

	#texts
	javascript_not_supported_error = "as your browser does not support javascript you won't be able to use all the features of the website"
	if any(javascript_not_supported_error in p for p in doc['text']):
		print "text contains ", javascript_not_supported_error
		return False
	if any("trendolizer" in p for p in doc['text']):
		print "text contains trendolizer"
		return False
	if not doc["text"]:
		print "text is empty"
		return False
	if not any("facebook" in p for p in doc['text']):
		print "text does not contain facebook"
		return False
	if all(not p for p in doc['text']):
		print "all paragraphs are empty"
		return False
	return True

def main():
	og_content, lower_content = read_input_file()
	cleaned = []

	for i in range(0, len(og_content)):
		if type(og_content[i]['text']) != list:
			og_content[i]['text'] = [copy.copy(og_content[i]['text'])]
			lower_content[i]['text'] = [copy.copy(lower_content[i]['text'])]
		
		assert type(og_content[i]['text']) == list
		assert type(lower_content[i]['text']) == list

		og_content[i]['text'] = filter(None, og_content[i]["text"])
		lower_content[i]["text"] = filter(None, lower_content[i]["text"])
	
		if documentIsGood(lower_content[i]):
			cleaned.append(og_content[i])
		else:
			print "Removing document ", i, "\n--------"

	print "Original Length:", len(og_content)
	print "Length: ", len(cleaned)

	write_output_file(cleaned)

main()
