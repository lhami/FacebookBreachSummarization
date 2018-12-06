# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 17:25:08 2018

@author: Leah
"""
#Fix encoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
from collections import Counter
#from nltk import FreqDist
import nltk
from nltk.corpus import stopwords
import time
from multiprocessing import Pool
import csv

path = "../jusText_Cleaning_Code/cleaned.json"

def get_stopwords():
	#the default stopwords list isn't quite sufficient
	nltk_defaults = stopwords.words('english')
	punctuation = [',', ':', '.', ';', '-', '"', '--', '!', '?', '(', ')', '``', '\'\'']
	custom_words = ['would', 'though', 'it', 'still', 'he', 'at', 'even', 'but', 'like', 'upon', 'a']
	return set(nltk_defaults + punctuation + custom_words)

def freq_by_pos(row):
	record, stop_words = row
	#print "Evaluating document: ", record['originalurl']
	pageText = record['text']

	#returns a list of (word, pos) tuples
	stopWords = get_stopwords()
	sentList = nltk.sent_tokenize(pageText)
	wordsInSentsPos = [nltk.pos_tag(nltk.word_tokenize(s)) for s in sentList]
	wordsPos = [w for s in wordsInSentsPos for w in s if w[0].lower() not in stopWords and len(w[0]) > 2 and "\\x" not in w[0]]
	posDict = {"verbs":"VB","adjectives":"JJ","nouns":"NN","adverbs":"RB"}
	for x in posDict:
		posDict[x] = possubset_freq(wordsPos,posDict[x])
	#print posDict, "\n\n"
	return posDict
	
def get_input():
	stop_words = get_stopwords()
	print "Reading Input JSON..."
	with open(path) as f:
		content = f.readlines()
	content = [(json.loads(x.lower()), stop_words) for x in content]
	print "Done loading json!"
	return content

def possubset_freq(wordlist,postag):
	#the pos tags are pretty granular so this checks if the first letters
	#match the first letters of the pos tag.
	#Params for common parts of speech:
	#VB- verbs    NN- nouns    JJ- adjectives    RB- adverbs
	return Counter([w[0] for w in wordlist if w[1][:len(postag)] == postag and w[0] is not None])

def writeCSV(counter,outdir = None,filename = "output.csv"):
	if outdir is None or outdir == ".":
		filepath = filename
	else:
		filepath = os.path.join(outdir,filename)
	with open(filepath, mode='w') as fp:
		writer = csv.writer(fp, delimiter=",")
		writer.writerow(['Token','Freq'])
		for tup in counter.most_common():
			writer.writerow(tup)

def fnn():
	st = time.time()
	print "Start Time: ", st
	documents = get_input()
	#documents = documents[:7]

	print "Length: ", len(documents)
	#individual_results = [ freq_by_pos(record) for record in documents ]

	p = Pool(15)
	individual_results = p.map(freq_by_pos, documents) #a list of the results from each document
	#each entry in the list is a dictionary where each key (POS tag) has a FreqDist value

	final_results = compile_results(individual_results)
	
	end = time.time()
	print "End Time: ", end-st

	print "Final Results"
	for pos, dist in final_results.iteritems():
		print pos
		print dist.most_common(50), "\n\n"
		writeCSV(dist,".","facebook_common_%s.csv" % pos)
		

def compile_results(distributions):
	print "Merging Results..."
	res = {}
	for row in distributions: #for each document
		for key, value in row.iteritems(): #for each POS,FreqDist
			if key not in res: #starts each POS tag with an empty counter so the addition works
				res[key] = Counter()
			res[key] = res[key] + value
	print "Done merging results..."
	return res


fnn()

#pageText = "The 2017 Total Solar Eclipse: Everything You Need to Know For the first time in U.S. history, a total solar eclipse that crosses the country from coast to coast will be visible only in America, and you can watch it live on TIME.com beginning at noon on Monday. The rare celestial spectacle in August has been dubbed “The Great American Eclipse.” The moon will completely block the sun, momentarily engulfing parts of about a dozen states in sudden darkness, on Aug. 21, 2017, experts say. No one outside the continental U.S. will be able to see the eclipse, which makes landfall on the West Coast near Salem, Ore. and continues diagonally across the country until it hits Columbia, S.C. In addition to being the first total solar eclipse with a trajectory exclusive to the U.S. since the birth of America in 1776, it’s also the first total eclipse of the sun that will be visible from the contiguous U.S. since 1979. What is a total solar eclipse? A total solar eclipse, or total eclipse of the sun, happens when the moon passes directly between the sun and the Earth and completely covers the entire face of the sun. The phenomenon typically only lasts for about two minutes for those standing within the eclipse’s path of totality. However, a partial eclipse — which happens when the moon only blocks a portion of the sun — usually lasts about two to three hours. In August, all of North America will experience a partial eclipse but only some states will get to witness the total eclipse. The event is different from a lunar eclipse, which occurs when the Earth passes between the sun and moon and blocks sunlight from reaching the moon. Lunar eclipses are more common than solar eclipses, according to Dr. Noah Petro, NASA’s lunar expert at the Goddard Space Flight Center. During a total solar eclipse, the skies darken suddenly and the air gets noticeably colder, facing by about 10ºF (5.5ºC), says Fred Espenak, a famed eclipse expert and retired NASA astrophysicist. Espenak knows a thing or two about total solar eclipses, having experienced 27 of them in all seven continents over the course of his 65 years. “It’s a visceral reaction. You feel something in the pit of your stomach like something is wrong in the day, something is not right,” he said in a recent interview with TIME. “As totality begins, and the shadow sweeps over you, the hairs on the back of your neck and arms stand up. You just go, ‘Wow.’” Espenak said it doesn’t become pitch-black outside; the sky looks more like it would in the evening, about 30 minutes before sunset. The sudden change confused ancient peoples and still throws animals and nature for a loop. “Flowers tend to close up like it’s nighttime. Birds tend to stop singing. I’ve seen cows head back to barns. I’ve heard crickets,” Espenak recalled. “All of a sudden now the sun, which was too bright to look at seconds ago, is replaced by this black disk with this ghostly halo around it, which is just exquisitely beautiful.” What time is the total solar eclipse? The solar eclipse will spread across the U.S. from Lincoln Beach, Ore., where a partial eclipse will begin at 9:05 a.m. PST on Aug. 21. The total solar eclipse will begin there at 10:16 a.m. The total eclipse will then move from the West Coast to the East Coast, ending near Columbia, S.C. at 2:44 p.m. EST. In all, the eclipse will take just about an hour and a half to traverse the country. In each place where the total solar eclipse can be viewed, it typically lasts no longer than two minutes and 40 seconds. Where can this year’s total solar eclipse be seen? NASA Most skygazers in Oregon, Idaho, Wyoming, Nebraska, Missouri, Kentucky, Tennessee, Georgia, North Carolina and South Carolina will get front row seats to the upcoming total solar eclipse — if weather permits, according to NASA, which has provided a solar eclipse map and diagram to show the times of totality. The eclipse’s path of totality officially touches 14 states, but it clips a few very narrowly, meaning the eclipse can only be viewed widely in about 10 states. Viewers must be within the eclipse’s path of totality, which spans about 70 miles wide, to see the sun as it’s completely blocked. In most places across the country, tickets for the best seats to view the eclipse have already sold out. Here’s what to expect: Oregon Oregon is expecting a million visitors worldwide to flock to the state to be the first in the country to see the total solar eclipse, which will be best viewed in Salem, Madras and Lime, according to The Oregonian. Many hotels in the state have been fully booked for the occasion for about four years, the newspaper said. Oregon State Parks said more than 1,000 state camping sites made available for the total solar eclipse have been fully booked as well. A viewing party at the state fairgrounds in Salem, which is being organized by the Oregon Museum of Science and Industry, has also sold out. But people can still buy tickets to participate in the nearly weeklong Oregon Solarfest, which features music, shopping, food and other activities in the high deserts of Madras. Idaho In Idaho, the eclipse begins near Idaho Falls at 10:15 a.m. local time, with totality starting at 11:33 a.m. To get the best view, experts say those in the state should head to mountaintop locations like the top of the Sun Valley and Borah Peak. However, as with many of the states that fall within the eclipse’s path of totality, reservations for hotels and spaces may be limited in the Gem State. Wyoming Wyoming is among the most popular hotspots for eclipse-watching since it offers many dramatic views even without a once-in-a-lifetime celestial event. Casper, Wyo. will start seeing a partial eclipse at 10:22 a.m. local time and a total eclipse at 11:42 a.m. Yellowstone National Park is near the path of totality, and Grand Teton National Park is in the center of the eclipse’s route, according to GreatAmericanEclipse.com. Montana, Iowa and Kansas The total solar eclipse will be visible in Montana but likely for less than a minute and only in a small part of the state that isn’t reachable by road, experts say. A sliver of Iowa in the eclipse’s path is also too tiny to promise a good sighting. People living in the northeast corner of Kansas, which is in the eclipse’s path, are encouraged to join neighbors in Nebraska and Missouri for a better view. Nebraska Nebraska residents and visitors will have plenty of places to view the phenomenon, which diagonally cuts across the heart of the Cornhusker State from the northwest to southeast. The eclipse hits Lincoln, Neb. at 11:37 a.m. local time and fully covers the sun at 1:02 p.m. The spectacle can be seen along Interstate 80 starting before North Platte to Lincoln. Missouri A large swath of Missouri is also in the eclipse’s path of totality. The eclipse begins in the Show Me State at 11:46 a.m. local time and totality hits Jefferson City at 1:13 p.m. Experts recommend that residents of St. Louis and Kansas City view the eclipse from St. Joseph on the Missouri River. Illinois The total solar eclipse can also be seen in the southernmost section of Illinois, which is slated to have the longest duration of totality. Carbondale, Ill. will witness the total eclipse for an estimated two minutes and 35 seconds or two minutes and 40 seconds, starting at 1:20 p.m. local time, experts predict. Southern Illinois University has planned a day of festivities on its campus and is working with the Adler Planetarium of Chicago to provide a viewing experience. Kentucky Kentucky will also experience a longer-than-usual total solar eclipse, which begins in Paducah at 1:22 p.m. It’s best to head to Paducah or Hopkinsville for prime viewing. A huge viewing party is shaping up in Nashville, Tenn., which will experience totality at 1:27 p.m. The city’s Adventure Science Center has been fielding calls from people across the globe looking to take part in the planetarium’s three-day music festival and viewing party, according to local station NewsChannel5. Georgia, North Carolina and South Carolina Clayton, Ga. will start seeing the total eclipse at 2:35 p.m. local time before the eclipse moves toward North Carolina near Charlotte and then Columbia, S.C. for totality at 2:41 p.m. South Carolina is the last stop on the eclipse’s path, which ends in the Atlantic Ocean around 4:06 p.m. The state’s Clemson University will host a viewing party, which is expected to lure thousands of people, according to the Associated Press. For those who aren’t in the path of totality, there will be plenty of places to live stream views of the total eclipse online, including on Time.com. What’s the safest way to view the solar eclipse? It’s safe to look at the sun with the naked eye and without any protection only during the totality phase of a total solar eclipse, but it’s dangerous to stare directly at the sun at any other time, including during a partial solar eclipse. Looking at the sun while wearing regular sunglasses during a partial solar eclipse is unsafe, and using binoculars or telescopes without the proper equipment, including solar filters, can severely damage your eyes. NASA says on its website that eclipse gazers should use special solar filters or “eclipse glasses,” making sure that the glasses are not scratched or damaged. Espenak said the filtered glasses are inexpensive, usually made out of cardboard material, and cost about $2 in most places. He said astronomy magazines may even include free pairs in upcoming issues to honor the major scientific event. Astronomers Without Borders, an international nonprofit group, is giving away more than 100,000 eclipse-viewing glasses to youth centers, children’s hospitals and other organizations in underserved areas of the country that apply for them. “This eclipse is historic, with a huge effort underway by organizations across the country to prepare people for the experience and use this rare opportunity to teach science,” Astronomers Without Borders President Mike Simmons said in a statement. “We’re very pleased to be able to provide access to eclipse viewing to those who might otherwise miss out.” A pinhole camera, which can be made at home with two pieces of paper or cardboard, is another tool to use to safely view a partial solar eclipse. Punch a small hole in the middle of one of the pieces of paper and then hold that piece of paper above your shoulder to let the sun strike it. An inverted image of the shape of the sun during a partial solar eclipse will be projected onto the second piece of paper, which could be placed be on the ground. The pinhole camera allows viewers to see the projected image of the sun without looking directly at it. While it’s not the real deal, the pinhole projector gives viewers an idea of when totality nears. Like the special solar glasses, pinhole projectors can be put away during totality. What’s the best way to photograph a solar eclipse? First things first: Do not take photos without wearing proper eye gear and protections, experts warn. Espenak suggests not taking any photos at all and just sitting back to experience the short total solar eclipse, but he acknowledges that many will want keepsakes of the rare sight. In that case, he recommends just using a smartphone over a more expensive or professional camera. Most new models of smartphones today will be able to capture the same image. “You’re not going to get close-ups of the eclipse, but you’ll be able to get the sky and the changing colors,” he said. For close-up snapshots, photographers should use a newer digital camera model that has a deeper or larger zoom lens than a typical point-and-shoot camera. The most versatile camera is the DSLR, or digital single lens reflex, Espenak explains on his website. But if you spend too much time fussing over your photography equipment, the moment will zip by, Espenak warns. “It races by so quickly. It’s the fastest two minutes of your life. It ends much too quickly,” he said. Espenak — whose expertise has earned him the nickname “Mr. Eclipse” in the science world and international eclipse chaser community — said seeing a total solar eclipse is a life-changing experience. “It’s certainly beyond words,” he said. “It’s so far out of the realm of everyday experience.” He saw his first total solar eclipse in 1970, when he was 18 years old and living in New York. “It literally took my breath away,” he said. The teenager had driven hundreds of miles from Staten Island to North Carolina and became hooked. He said he has been to every total eclipse since the 1990s. “As soon as it was over, I knew I had to see another one,” he said of his first experience. “I couldn’t let it be a once-in-a-lifetime event.” When is the next solar eclipse? After the U.S.-only eclipse this year, there will be another in July 2019, visible in parts of Argentina and Chile. Americans who miss the August event can will get another shot in 2024, when a solar eclipse comes up from Mexico and hits several states on its diagonal path from Texas through New England. SPONSORED FINANCIAL CONTENT You May Like Stories From Read More Sign Up for Our Newsletters Sign up to receive the top stories you need to know now on politics, health, money and more"
#Freqs = freq_by_pos(pageText)
#print(Freqs)

#Freqs is currently a dictionary of nltk FreqDist objects, one for each pos.
#Going to keep as FreqDist because they can be merged by adding Freqs + Freqs
#If this code is run individually on each collection
