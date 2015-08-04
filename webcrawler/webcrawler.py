#! /usr/bin/env python
# -*- coding: utf-8 -*
"""Crawls links on a website recursively and produces a siteMap


"""

__author__ = "Tharak Krishnan (tharak.krishnan@gmail.com)"
__version__ = "$Revision: 1.0$"
__date__ = "$Date: 2015/08/01 $"
__copyright__ = "Copyright (c) 2015 Tharak Krishnan"
__license__ = "Python"

import re
from sets import Set
from urlparse import urlparse

class WebCrawler():
	""" Web crawler class crawls a specific website
	"""
	def __init__(self, url="https://www.digitalocean.com", outdir="out", max_level=1000, debug=0):
		self.url=url					#URL of the website to crawled
		self.siteMap = {self.url:""}	#Datastructure storing the URL and links found in crawled webpages
		self.outdir=outdir.rstrip("/")+"/"	#Output Directory
		self.level = 0					#variable counting the crawl depth
		self.MaxLevel = max_level		#Maximum allowed crawl depth allowed by the User
		self.crawled=Set([])			#A Set datastructure containing previously crawled sites to avoid repetition
		self.debug=debug				#Debug flag allowing user to control debug messages on the console
		self.domains=Set([urlparse(self.url).netloc.lower()])
		
		from os import path, makedirs
		if not path.exists(self.outdir): 
			makedirs(self.outdir)
			
		
	def __crawl_site(self, url_key=""):
		"""Recursively crawls the url passed and populates the sitemap datastructure
		"""

		if self.level > self.MaxLevel: 	#Do not continue crawling if we are at maximum allowed depth
			return
		
		if url_key=="":    				#This variable contains the postfix that needs to be appended to the domain name
			url=self.url				#in order to crawl a webpage
		else:
			url=url_key
			
		if(self.debug > 0): print "Now crawling: %s"%(url)
		
		url_list=[]
		
		for key in self.siteMap:		#When we cycle through the siteMap datastructure we convert to a url_list
		 	url_list.append(key)		#Otherwise, the interpreter complains that dictionary is constantly changing 
		
		for key in url_list:			#Fetch the URLs in the webpage and append to siteMap for URLs that have not yet been crawled. 
			if self.siteMap[key] == "":
				urls =self.__extract_url(url)
				self.siteMap[key] = urls

				for url_key in urls:	#If the URL has already been crawled or has a # tag, dont crawl it.
					if (self.debug > 1): 
						print "url_key: %s, crawled: %s"%(url_key,self.crawled)
					if url_key in self.crawled:
						continue
					if "#" in url_key:
						continue
					
					#We do not want to crawl external domains. 
					parsed = urlparse(url_key)
					
					if (self.debug > 1): 
						print parsed.netloc
					
					if parsed.netloc.lower() in self.domains:		#If netloc is empty or is digitalocean.com then the page is part of local domain and needs to be crawled.    
						
						if (self.debug > 1): 
							print "\nLevel=%s,URL=%s\n"%(self.level, url_key)
						self.siteMap[url_key] = ""  #Add webpage to siteMap before crawling to allow it be crawled.
						self.crawled.add(url_key)   #Update the crawled set to indicate that this website has been crawled ( will prevent us from being stuck in a loop)
						self.level = self.level+1   #Increment depth count
						self.__crawl_site(url_key)	
						self.level = self.level-1	#Decrement depth count once the page and all its children have been crawled
			

	def __print_siteMap(self):
		"""Prints the siteMap datastructure in an XML like format
		"""
		#Dump Sitemap to an XML file
		try:                                
			fd = open(self.outdir+"site.xml", "w") 
			try:                           
				fd.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
				fd.write("<WEBSITE>\n")
				for key in self.siteMap:
					fd.write("\t<WEBPAGE>\n")
					fd.write("\t\t<ADDRESS>\"%s\"</ADDRESS>\n"%(key))
					for loc in self.siteMap[key]:
						fd.write("\t\t<LINK>\"%s\"</LINK>\n"%(loc))
					fd.write("\t</WEBPAGE>\n")
				fd.write("</WEBSITE>\n")
			finally:                        
				fd.close()                    			  
		except IOError:                     
			pass    
		#Dump siteMap to a json file
		import json
		with open(self.outdir+'site.json', 'w') as fp:
			json.dump(self.siteMap, fp, indent=4)    
    
		
					
	def get_siteMap(self):
		"""Initiates the crawler and populates the siteMap
		"""
		self.__crawl_site()
		self.__print_siteMap()
		return self.siteMap

	def __extract_url(self, url): 
		"""Extracts the links in the input URL
		"""
		
		import urllib2
		from urllister import URLLister
		from sgmllib import SGMLParseError
		
		req = urllib2.Request(url, headers={'User-Agent' : "Tharak Krishnan's Browser"}) 
		try:
			usock = urllib2.urlopen(req)
			parser = URLLister(url)
		
			try:
				parser.feed(usock.read())
				parser.close()
			except Exception as exception:
				if (self.debug > 0): 
					print "sgmllib: Unable to parse web page.\n sgmllib: Raised exception %s"%(type(exception).__name__)
					fd = open(self.outdir+"%s.err"%type(exception).__name__, "a")
					fd.write( "%s\n"%(url))	
					fd.close()
				pass
			usock.close()
			return parser.urls
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception as exception:
			if (self.debug > 0): 
				print "urllib2: Page does not exist or Malformed web address.\n sgmllib: Raised exception %s"%(type(exception).__name__) 
				fd = open(self.outdir+"%s.err"%type(exception).__name__, "a")
				fd.write( "%s\n"%(url))	
				fd.close()
			return []
		


if __name__ == "__main__":
	wc=WebCrawler(url="http://digitalocean.com", outdir="out",debug=1);
	wc.get_siteMap()
	