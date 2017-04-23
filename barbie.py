#!/usr/bin/env python3

import sys
import subprocess
import os.path
import getopt


def exe_code(exec_file, in_file, out_dir, index):
	out = open(os.path.join(out_dir, str(index), in_file.split('.')[0]) + '.out', 'w')
	ins = open(os.path.join(out_dir, str(index), in_file), 'r')
	subprocess.Popen(exec_file, stdin=ins, stdout=out, stderr=subprocess.STDOUT, universal_newlines=True)
	out.close()
	ins.close()

def run_tests(exec_file, in_files, out_dir):
	size = len(in_files)
	print()
	for i in range(size):
		print('Executing test %d of %d' %(i+1, size), end='\r')
		exe_code(exec_file, in_files[i], out_dir, i+1)
	print()


def compare_susy(susy_file, out_file, index):
	susy = open(susy_file)
	test = open(out_file)

	with open(susy_file.split('.')[0] + '.cmp', 'w') as barbie_out:

		s_lines = susy.readlines()
		t_lines = test.readlines()

		diference_count = 0

		msg_1 = "Susy file: %s with %d lines\n" % (susy_file, len(s_lines))
		msg_2 = "Test file: %s with %d lines\n" % (out_file, len(t_lines))

		barbie_out.write(msg_1)
		barbie_out.write(msg_2)


		for i in range(min(len(s_lines), len(t_lines))):
			if s_lines[i] != t_lines[i]:
				msg_s = "[%d] susy: %s" % (i, s_lines[i])
				msg_o = "[%d] out:  %s" % (i, t_lines[i])

				barbie_out.write(msg_s)
				barbie_out.write(msg_o)

				diference_count += 1

		diference_count += abs(len(s_lines) - len(t_lines))

		msg_f =  "\nDiference count: %d" % diference_count
		barbie_out.write(msg_f)

		if not diference_count:
			msg_t = "Teste %d: Resultado correto!" % (index)
		else:
			msg_t = "Teste %d: Resultado incorreto. Linhas divergentes: %d" % (index, diference_count)

		print(msg_t,)


	susy.close()
	test.close()


def _gcc_output_file(source_code):
	return os.path.splitext(source_code)[0] + '.gcc'

def compile_c(source_code):
	# Define the gcc output and the compile code files names
	gcc_out = _gcc_output_file(source_code)
	exec_file = os.path.splitext(source_code)[0]
	
	# Avoid the possibility of having the output with the same name as the input
	if exec_file == source_code:
		exec_file += ".out"

	compilation_args = ["gcc", source_code, "-o", exec_file]
	with open(gcc_out, 'w') as out:
		process = subprocess.run(compilation_args, stdout=out, stderr=subprocess.STDOUT)
	process.check_returncode()
	return exec_file


def get_local_tests(tests_folder):
	in_files  = []
	res_files = []
	# serach for test files in the tests_folder
	for root, dirs, files in os.walk(tests_folder):
		# Enter each test directory
		if root is not tests_folder:
			for arq in files:
				# Check the extension
				ext = os.path.splitext(arq)[1]
				if ext == '.in': # input file
					in_files.append(arq)
				elif ext == '.res': # result file
					res_files.append(arq)
	in_files.sort()
	res_files.sort()
	return in_files, res_files


def usage():
	print("""
	Welcome to Barbie!
	The Susy Simulator
	
	Pré-requisitos:
		1-gcc
		2-python 3.5 ou superior
	Como usar:
		1-Crie um execultável do seu programa em c com o gcc -o exec.out PROGRAMA.c
		2-exporte o exec.out para diretório da barbie
		3-use o comando no diretório da barbie

	python3 barbie -e exec.out -u https://susy.ic.unicamp.br:9999/TURMA_DE_MC/N_LAB/dados/testes.html

	Exemplo:
	python3 barbie.py -e lab4 -u https://susy.ic.unicamp.br:9999/mc202d/4/dados/testes.html
	python3 barbie.py -c lab4.c -u https://susy.ic.unicamp.br:9999/mc202d/4/dados/testes.html
	by: Mosquito""")


def main():
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "he:c:u:l", ["help", "executable=","code=", "url=", "local"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(err)  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	exec_file = None
	url = None
	source_code = None
	local = False
	
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-e", "--executable"):
			exec_file = os.path.realpath(a)
		elif o in ("-c", "--code"):
			source_code = os.path.realpath(a)
		elif o in ("-u", "--url"):
			url = a
		elif o in ("-l", "--local"):
			local = True
		else:
			assert False, "unhandled option"

	if (not url and not local) or (not exec_file and not source_code):
		usage()
		sys.exit(2)

	# If the user got us one, compile the source code
	if source_code:
		# Try to compile the source code
		try:
			exec_file = compile_c(source_code)
			print('Código compilado com sucesso!')
		# If there was a compilation problem
		except subprocess.CalledProcessError:
			# Notificate the user about the problem
			gcc_f = _gcc_output_file(source_code)
			print("Falha na compilação!")
			print("OUTPUT >>>", gcc_f)
			# Show the compilation output and end the program
			with open(gcc_f, 'r') as gcc:
				print(gcc.read())
			sys.exit(1)

	tests_dir_name = os.path.realpath("testes/")
	in_files = None
	res_files = None

	if url:
		import susy_interface as susy
		# List all susy files of open tests
		in_files, res_files = susy.get_susy_files(url)
		# Download all the open tests
		susy.download_tests(url, in_files, res_files, tests_dir_name)

	if local:
		in_files, res_files = get_local_tests(tests_dir_name)

	if in_files and res_files:
		# Excute the tests
		run_tests(exec_file, in_files, tests_dir_name)
		# Check the output of each test
		for arq in res_files:
			test = os.path.splitext(arq)[0]
			index  = res_files.index(arq)+1
			# Compare your output with the expected output got from susy
			compare_susy(os.path.join(tests_dir_name, str(index), arq), os.path.join(tests_dir_name, str(index), test) + '.out', index)


if __name__=="__main__":
	main()
