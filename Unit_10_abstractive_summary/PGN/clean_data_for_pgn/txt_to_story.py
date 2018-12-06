import getopt
import sys
import hashlib
import os

def hashhex(s):
  """Returns a heximal formated SHA1 hash of the input string."""
  h = hashlib.sha1()
  h.update(s)
  return h.hexdigest()

def processFiles(inFile,outputDir,subDir):

    #Make sure there is an output directory
    if not os.path.exists(os.path.join(outputDir,subDir)): os.makedirs(os.path.join(outputDir,subDir))
    
    URL_FILE = open(os.path.join(outputDir,'all_urls.txt'),'w')
    counter = 0
	
    with open(os.path.join(inFile), 'r') as fs:
        for line in fs:
            clusterid = "cluster %d" % counter
            h = hashhex(clusterid.encode())
            fileName = os.path.join(outputDir,subDir,h+'.story') #create the. story file version of the article
            FILE = open(fileName,'w')
            FILE.write(line)
            FILE.close()
            URL_FILE.write('%s\n' % clusterid)
            counter += 1
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
		print(('python txt_to_story.py -f <input text file> -o <output directory> -s <folder name for story files>'))
	   
	  
	   
		sys.exit(2)
	   
	#initialize cmd line variables with default values
	inFile = None
	outputDir = None
	subDir = "story_files"

	
	for opt, arg in opts:
		print((opt,'\t',arg))
		if opt == '-h':
			print(('python txt_to_story.py -f <input text file> -o <output directory> -s <folder name for story files>'))
			sys.exit()
		elif opt in ("-f"):
			inFile = arg
		elif opt in ("-o"):
			outputDir = arg
		elif opt in ("-s"):
			subDir = arg
        

           
	print('\n')
	print("Input Text File:",inFile)
	print("Output directory:", outputDir)
	print("Story file subdirectory:", os.path.join(outputDir,subDir))
	print('\n')
    
	processFiles(inFile,outputDir,subDir)
