#!/usr/bin/env python3

import sys
import os.path
import getopt
import os
import susy_interface as susy
from barbie_test import BarbieTest
from barbie_exceptions import UnknownLanguageException
from codes import PythonCode, CCode, CodeLanguage
from barbie_call import BarbieCall
import log

def get_local_tests(tests_folder):
	in_files  = []
	res_files = []
	# search for test files in the tests_folder
	for root, dirs, files in os.walk(tests_folder):
		# Enter each test directory
		if root is not tests_folder:
			for arq in files:
				# Check the extension
				name, ext = os.path.splitext(arq)
				if (ext == '.in' or 'in' in name) and ext not in ['.cmp', '.out']: # input file
					in_files.append(arq)
				elif (ext == '.res' or 'res' in name) and ext not in ['.cmp', '.out']: # result file
					res_files.append(arq)
	# Sort the files, so they are executed in order
	in_files.sort()
	res_files.sort()
	return in_files, res_files

def run_and_compare(user_code, in_files, res_files, tests_dir_name, timeout=2):
	results = list()
	# Check the output of each test
	for index in range(1, len(res_files)+1):
		test_directory = os.path.join(tests_dir_name, str(index))

		susy_file = os.path.join(test_directory, res_files[index-1])
		input_file = os.path.join(test_directory, in_files[index-1])

		# Compare your output with the expected output got from susy
		test = BarbieTest(user_code, susy_file, input_file, test_directory, index)
		test.run(timeout)
		results.append(test)

	for test in results:
		test.compare()

	return results

def get_language_and_compile(files):
	if 'py' in files:
		user_code = PythonCode()
		user_code.source_files = files['py']
		user_code.exec_file = files['py'][0]
	elif 'c' in files:
		user_code = CCode()
		user_code.source_files = files['c']
		user_code.compile()
	else:
		raise UnknownLanguageException
	return user_code

def prepare_code(files, executable_file=None):
	# If the user got us one, compile the source code
	if files:
		# Try to compile the source code
		try:
			user_code = get_language_and_compile(files)
			if type(user_code) is CCode:
				assert user_code.compilation_sucess, "Falha na compilação"
				log.uprint('Código compilado com sucesso!')
		except UnknownLanguageException:
			eprint('Não foi fornecido código de nenhuma linguagem conhecida')
			usage()
			exit(2)
		# If there was a compilation problem
		except AssertionError as e:
			# Notificate the user about the problem
			eprint("Falha na compilação!")
			eprint("OUTPUT >>>", user_code.gcc_file)
			# Show the compilation output and end the program
			with open(user_code.gcc_file, 'r') as gcc:
				log.eprint(gcc.read())
			exit(1)
	elif executable_file:
		user_code = CodeLanguage();
		user_code.exec_file = executable_file
	return user_code

def usage():
	log.uprint("""\
Barbie:
O seu Susy local

usage: python3 barbie.py [-h] [-e] [-u] [-l] [-t] [Arquivos de código]

Opções:
-e, --executable    Executa a barbie utilizando um arquivo
                    executavel, de um código já compilado.
-u, --url           Fornecer diretamente o link da página
                    com os arquivos de teste do susy.
-l, --local         Não acessa o Susy e faz os testes com os
                    arquivos já baixados anteriormente.
-t, --timeout       Define o timeout de execução de cada teste
                    o valor deve ser dado em segundos.
""")


def execute(barbie_call):
	user_code = prepare_code(barbie_call.code_files, barbie_call.executable_file)

	tests_dir_name = os.path.realpath("testes/")
	in_files = None
	res_files = None

	# If the program is not set to run locally and no url was given,
	# prompt user for the class info and discover the url
	if not barbie_call.test_files_url and not barbie_call.local:
		barbie_call.test_files_url = susy.discover_susy_url(barbie_call.disciplina, barbie_call.turma, barbie_call.codigo_lab)

	# The user may input the url from the desired tests page
	if barbie_call.test_files_url:
		# List all susy files of open tests
		in_files, res_files = susy.get_susy_files(barbie_call.test_files_url)
		# Download all the open tests
		susy.download_tests(barbie_call.test_files_url, in_files, res_files, tests_dir_name)

	# Option to run the program locally, and don't acess Susy
	if barbie_call.local:
		in_files, res_files = get_local_tests(tests_dir_name)

	# If we sucessufuly got all needed files,
	# we may run all tests and compare our output with the expected
	if in_files and res_files:
		run_and_compare(user_code, in_files, res_files, tests_dir_name, barbie_call.timeout)
	exit()

def main():

	try:
		opts, args = getopt.getopt(sys.argv[1:], "he:u:lt:", ["help", "executable=","url=", "local", "timeout"])
	except getopt.GetoptError as err:
		# print help information and exit:
		eprint(err)  # will print something like "option -a not recognized"
		usage()
		exit(2)

	barbie_call = BarbieCall()

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			exit()
		elif o in ("-e", "--executable"):
			barbie_call.executable_file = os.path.realpath(a)
		elif o in ("-u", "--url"):
			barbie_call.test_files_url = a
		elif o in ("-l", "--local"):
			barbie_call.local = True
		elif o in ("-t", "--timeout"):
			barbie_call.timeout = double(a)
		else:
			assert False, "unhandled option"

	barbie_call.code_files = dict()
	for path in args:
		# Get extension
		ext = os.path.splitext(path)[1][1:].strip()
		if ext not in barbie_call.code_files:
			barbie_call.code_files[ext] = list()
		# Save in the dict the path to this file
		barbie_call.code_files[ext].append(os.path.realpath(path))

	# We need to receive at least a
	if (not barbie_call.executable_file and not barbie_call.code_files):
		usage()
		exit(2)

	if not barbie_call.test_files_url and not barbie_call.local:
		barbie_call.disciplina   = input("Disciplina: ")
		barbie_call.turma        = input("Turma:      ")
		barbie_call.codigo_lab   = input("Lab:        ")

	execute(barbie_call)


if __name__=="__main__":
	log.supress_output = False
	main()
else:
	log.supress_output = False
