#!/usr/bin/env python3

import sys
import requests
import shutil
import os
import urllib.request

from html.parser import HTMLParser

# Ignore Susy Certificate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SusyHTMLParser(HTMLParser):
	
	fechados = False
	in_files = []
	res_files = []
	count = 0
	out = False

	def handle_starttag(self, tag, attrs):
		if tag=='a' and not self.fechados:
			if self.out:
				#print("File OUT:", attrs[0][1])
				self.count+=1
				self.res_files.append(attrs[0][1])
			else:
				#print("File IN: ", attrs[0][1])
				self.count+=1
				self.in_files.append(attrs[0][1])
			self.out = not self.out

	def handle_endtag(self, tag):
		if tag=='blockquote':
			self.fechados = True

	def get_in_files(self):
		return self.in_files

	def get_res_files(self):
		return self.res_files

def get_susy_files(susy_link):
	print("Detecting susy test files", end='\r')
	html = requests.get(susy_link, verify=False)

	parser = SusyHTMLParser()
	parser.feed(html.text)
	print("Sucessfully detected %d susy test files to download" % parser.count)
	return parser.get_in_files(), parser.get_res_files()


def download_file(url, file_name):
	# Download the file from `url` and save it locally under `file_name`:
	with open(file_name, 'w') as out_file:
		data = requests.get(url, verify=False).text # a `bytes` object
		out_file.write(data)

def download_tests(susy_tests_url, in_files, res_files, dir_name):
	susy_path = susy_tests_url.split('/')[:-1]

	try:
		shutil.rmtree(dir_name)
	except FileNotFoundError:
		pass
	os.mkdir(dir_name)

	data_url = '/'.join(susy_path) + '/'

	print()
	try:
		for i in range(len(in_files)):

			os.mkdir(os.path.join(dir_name, str(i+1)))
			
			# download test input
			print('Downloading file %d of %d' %(i*2+1, len(in_files)*2), end='\r')
			download_file(data_url + in_files[i], os.path.join(dir_name, str(i+1), in_files[i]))
			
			# Download test output
			print('Downloading file %d of %d' %(i*2+2, len(in_files)*2), end='\r')
			download_file(data_url + res_files[i], os.path.join(dir_name, str(i+1), res_files[i]))
	
	except Exception as e:
		print('Connection Failed!')
		print('Error:', e)
		print()
		sys.exit('Exiting program')

