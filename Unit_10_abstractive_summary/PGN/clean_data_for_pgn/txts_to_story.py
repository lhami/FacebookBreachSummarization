import getopt
import sys
import hashlib
import os

def hashhex(s):
  """Returns a heximal formated SHA1 hash of the input string."""
  h = hashlib.sha1()
  h.update(s)
  return h.hexdigest()

def processFiles(inDir,outputDir,subDir):

    #Make sure there is an output directory
    if not os.path.exists(os.path.join(outputDir,subDir)): os.makedirs(os.path.join(outputDir,subDir))
    
    URL_FILE = open(os.path.join(outputDir,'all_urls.txt'),'w')
	
    for infile in os.listdir(inDir):
        with open(os.path.join(inDir,infile), 'r') as fs:
            h = hashhex(infile.encode())
            fileName = os.path.join(outputDir,subDir,h+'.story') #create the. story file version of the article
            FILE = open(fileName,'w')
            FILE.write(fs.read())
            FILE.close()
            URL_FILE.write('%s\n' % infile)
    URL_FILE.close()

if __name__ == '__main__':
        
	print((sys.argv))
	
	try:
	   opts, args = getopt.getopt(sys.argv[1:],"f:h:o:s:")
	except getopt.GetoptError:
		
		print(("opts:"))
		print((opts))
		
		print(('\n'))
		print(("args:"))
		print((args))
		
		print(("Incorrect usage of command line: "))
		print(('python txts_to_story.py -f <input directory> -o <output directory> -s <folder name for story files>'))
	   
	  
	   
		sys.exit(2)
	   
	#initialize cmd line variables with default values
	inDir = None
	outputDir = None
	subDir = "story_files"

	
	for opt, arg in opts:
		print((opt,'\t',arg))
		if opt == '-h':
		   print(('python txts_to_story.py -f <input directory> -o <output directory> -s <folder name for story files>'))
		   sys.exit()
		elif opt in ("-f"):
		   inDir = arg
		elif opt in ("-o"):
			outputDir = arg
		elif opt in ("-s"):
			subDir = arg
        

           
	print('\n')
	print("Input Directory:",inDir)
	print("Output directory:", outputDir)
	print("Story file subdirectory:", os.path.join(outputDir,subDir))
	print('\n')
    
	processFiles(inDir,outputDir,subDir)
