#!/usr/bin/env python3

import sys
import requests
import shutil
import os
import urllib.request

from html.parser import HTMLParser
from urllib.parse import urljoin

# Ignore Susy Certificate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

susy_base_url = "https://susy.ic.unicamp.br:9999/"

class SusyTestesHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.fechados = False
		self.in_files = []
		self.res_files = []
		self.count = 0
		self.out = False

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


class SusyClassHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.terminou = False
		self.disciplinas = []
		self.count = 0

	def handle_starttag(self, tag, attrs):
		if tag=='a' and not self.terminou:
			self.count+=1
			self.disciplinas.append(attrs[0][1])

	def handle_endtag(self, tag):
		if tag=='blockquote':
			self.terminou = True

	def get_discs(self):
		return self.disciplinas

def get_susy_files(susy_link):
	__print("Detecting susy test files")
	html = requests.get(susy_link, verify=False)

	parser = SusyTestesHTMLParser()
	parser.feed(html.text)
	__print("Sucessfully detected %d susy test files to download" % parser.count)
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

	__print()
	try:
		for i in range(len(in_files)):

			os.mkdir(os.path.join(dir_name, str(i+1)))

			# download test input
			__print('Downloading file %d of %d' %(i*2+1, len(in_files)*2), end='\r')
			download_file(data_url + in_files[i], os.path.join(dir_name, str(i+1), in_files[i]))

			# Download test output
			__print('Downloading file %d of %d' %(i*2+2, len(in_files)*2), end='\r')
			download_file(data_url + res_files[i], os.path.join(dir_name, str(i+1), res_files[i]))

	except Exception as e:
		eprint('Connection Failed!')
		eprint('Error:', e)
		eprint()
		eprint('Não foi possível obter os arquivos do sistema Susy')
		raise Exception

def _discover_susy_disc(disc, turma):
	discs = list()

	disc = disc.lower()
	turma = turma.lower()

	susy_disc = None

	html = requests.get(susy_base_url, verify=False)

	parser = SusyClassHTMLParser()
	parser.feed(html.text)

	discs = parser.get_discs()
	for opt in discs:
		if disc in opt and turma in opt:
			susy_disc = opt
	if not susy_disc:
		assert False, "Turma não encontrada"
	return susy_disc

def _discover_susy_lab(url, lab):
	discs = list()

	susy_disc = None

	html = requests.get(url, verify=False)

	parser = SusyClassHTMLParser()
	parser.feed(html.text)

	discs = parser.get_discs()
	for opt in discs:
		if lab in opt:
			susy_disc = opt

	if not susy_disc:
		assert False, "Lab não encontrado"
	return susy_disc + '/'

def discover_susy_url(disc, turma, lab):
	disc = _discover_susy_disc(disc, turma)
	url = urljoin(susy_base_url, disc)
	turma = _discover_susy_lab(url, lab)
	return urljoin(urljoin(url, turma), 'dados/testes.html')

def __print(*args, **kargs):
	if not supress_output:
		print(*args, **kargs)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

supress_output = False
