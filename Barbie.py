#!/usr/bin/env python3

import sys
import requests
import shutil
import os
import subprocess
import urllib.request
import os.path

from html.parser import HTMLParser

class SusyHTMLParser(HTMLParser):
	
	fechados = False
	in_files = []
	res_files = []
	out = False

	def handle_starttag(self, tag, attrs):
		if tag=='a' and not self.fechados:
			if self.out:
				print("File OUT:", attrs[0][1])
				self.res_files.append(attrs[0][1])
			else:
				print()
				print("File IN: ", attrs[0][1])
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
	
	html = requests.get(susy_link, verify=False)

	parser = SusyHTMLParser()
	parser.feed(html.text)

	return parser.get_in_files(), parser.get_res_files()

def download_file(url, file_name):
	# Download the file from `url` and save it locally under `file_name`:
	with open(file_name, 'w') as out_file:
		data = requests.get(url, verify=False).text # a `bytes` object
		out_file.write(data)


def download_tests(susy_tests_url, in_files, res_files, dir_name):
	susy_path = susy_tests_url.split('/')[:-1]
	#local_path = susy_path[3:]

	try:
		shutil.rmtree(dir_name)
	except FileNotFoundError:
		pass
	os.mkdir(dir_name)

	data_url = '/'.join(susy_path) + '/'

	print()
	try:
		for i in range(len(in_files)):
			print('Downloading file %d of %d' %(i*2+1, len(in_files)*2), end='\r')
			download_file(data_url + in_files[i], dir_name + in_files[i])
			print('Downloading file %d of %d' %(i*2+2, len(in_files)*2), end='\r')
			download_file(data_url + res_files[i], dir_name + res_files[i])
	except Exception as e:
		print('Connection Failed!')
		print('Error:', e)
		print()
		sys.exit('Exiting program')

def exe_code(exec_file, in_file, out_dir):
	out = open(out_dir + in_file.split('.')[0] + '.out', 'w')
	ins = open(out_dir + in_file, 'r')
	process = subprocess.Popen(exec_file, stdin=ins, stdout=out, stderr=subprocess.STDOUT, universal_newlines=True)
	out.close()
	ins.close()

def run_tests(exec_file, in_files, out_dir):
	size = len(in_files)
	print()
	for i in range(size):
		print('Executing test %d of %d' %(i+1, size), end='\r')
		exe_code(exec_file, in_files[i], out_dir)
	print()


def compare_susy(susy_file, out_file, index):
	susy = open(susy_file)
	test = open(out_file)

	with open(susy_file.split('.')[0] + '.cmp', 'w') as barbie_out:

		s_lines = susy.readlines()
		t_lines = test.readlines()

		diference_count = 0

		msg_1 = "Susy file: %s with %d lines" % (susy_file, len(s_lines))
		msg_2 = "Test file: %s with %d lines" % (out_file, len(t_lines))

		barbie_out.write(msg_1)
		barbie_out.write(msg_2)


		for i in range(min(len(s_lines), len(t_lines))):
			if s_lines[i] != t_lines[i]:
				msg_s = "[%d] susy: %s" % (i, s_lines[i])
				msg_o = "[%d] out:  %s" % (i, t_lines[i])

				barbie_out.write(msg_s)
				barbie_out.write(msg_o)

				diference_count += 1

		msg_f =  "Diference count: %d" % diference_count
		barbie_out.write(msg_f)

		if not diference_count:
			msg_t = "Teste %d: Resultado correto!" % (index)
		else:
			msg_t = "Teste %d: Resultado incorreto. Linhas divergentes: %d" % (index, 1 + diference_count + abs(len(s_lines), len(t_lines)))

		print(msg_t,)


	susy.close()
	test.close()

def main():

	exec_file = sys.argv[1]
	url = sys.argv[2]

	tests_dir_name = "dados/"

	in_files, res_files = get_susy_files(url)
	download_tests(url, in_files, res_files, tests_dir_name)
	run_tests(exec_file, in_files, tests_dir_name)
	for arq in res_files:
		print()
		test = arq.split('.')[0]
		compare_susy(os.path.join(tests_dir_name, arq), os.path.join(tests_dir_name, test) + '.out', res_files.index(arq))


if __name__=="__main__":
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	main()
