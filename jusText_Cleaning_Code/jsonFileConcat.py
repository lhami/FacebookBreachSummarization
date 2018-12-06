import os

input_folder = "cleaned.json`"
output_path = "cleaned.json"
json_files = [pos_json for pos_json in os.listdir(input_folder) if pos_json.endswith('.json')]

with open(output_path, 'w') as out:
	for file in json_files:
		with open(input_folder + file) as f:
			for line in f.readlines(): out.write(line)
