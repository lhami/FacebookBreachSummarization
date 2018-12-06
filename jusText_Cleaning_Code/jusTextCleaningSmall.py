import os
os.environ['PYSPARK_PYTHON'] = './pyspark/external_pkgs/bin/python'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
from datetime import date
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

#Load Spark Session
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
conf = SparkConf().setAppName('paracleaner')
sc = SparkContext(conf=conf)
spark = SparkSession.builder.appName('paracleaner').getOrCreate()
path = "/user/cs4984cs5984f18_team14/14_Facebook_Breach_small/articlehtmlsmall.json"
htmlDF = spark.read.json(path)

def bestGuess(old,new):
	#returns a date object
	if old is None: return new
	elif date(2018,3,17) <= new <= date(2018,9,19):
		if date(2018,3,17) <= old <= date(2018,9,19): return min(old,new)
		else: return new
	else: return old

def getDate(html):
	#A best attempt at retrieving the publication date from all articles, based on page metadata.
	from bs4 import BeautifulSoup
	from dateutil.parser import parse
	#Returns a string with the most likely date in ISO format
	page = BeautifulSoup(html, 'lxml')
	metas = page.find_all(lambda tag:tag.name == "meta" and [y for x,y in tag.attrs.iteritems() if x in ["itemprop","name","prop","property"]])
	potentialdates = [m['content'] for m in metas if m.has_attr('content')]
	times = page.select('time[datetime]')
	if len(times) > 0: potentialdates.append(times[0]['datetime'])
	potentialdates.extend([t.string for t in page.select('.time')])
	#potentialdates.extend([t['datetime'] for t in page.select('time[datetime]')])
	#would add all potential dates on the page but it looks like that tends to capture a lot of
	#dates for related articles.
	bestguess = None
	for d in potentialdates:
		if d is None: continue
		if d.isdigit() and len(d) != 10: continue
		try:
			day = parse(d).date()
		except:
			if d.isdigit():
				if len(d.lstrip('0')) == 10:
					day =  datetime.datetime.utcfromtimestamp(int(d)).date()
				elif len(d.lstrip('0')) == 13:
					day = datetime.datetime.utcfromtimestamp(int(d) / 1000).date()
				else: continue
			else: continue
		#now tries to figure out if the new time is more likely to be the
		#upload time than the existing bestguess
		bestguess = bestGuess(bestguess,day)
	if bestguess is not None: return bestguess.isoformat()
	else: return ""

def HtmlClean(rawtext):
	#Runs jusText on each entry, to remove boilerplate and return cleaned text.
	#Note that this requires that the input text has HTML still in-tact as jusText
	#splits text based on tags like <p> and <br />
	import justext
	paragraphs = justext.justext(rawtext,justext.get_stoplist("English"))
	return ' '.join([p.text for p in paragraphs if p.text.strip() != "" and not p.is_boilerplate])

pysparkClean = udf(HtmlClean, StringType())
pysparkDate = udf(getDate, StringType())

cleanDF = htmlDF.withColumn('cleantext',pysparkClean(htmlDF['text'])).withColumn('isopubdate',pysparkDate(htmlDF['text'])).drop('text').withColumnRenamed('cleantext','text').withColumnRenamed('originalUrl','originalurl')
cleanDF = cleanDF[~cleanDF["title"].contains("Forbidden") & ~cleanDF["title"].contains("forbidden") & ~cleanDF["title"].contains("page not found") & ~cleanDF["title"].contains("404") & ~cleanDF["title"].contains("403") & ~cleanDF["title"].contains("408") & ~cleanDF["title"].contains("ERROR") & ~cleanDF["title"].contains("Access Denied") & ~cleanDF["title"].contains("Page not found") & ~cleanDF["originalurl"].contains("money.cnn.com")]

cleanDF.coalesce(1).write.format('json').save('/user/cs4984cs5984f18_team14/14_Facebook_Breach_small/cleaned_paragraphs')
