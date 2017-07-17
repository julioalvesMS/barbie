#!/usr/bin/env python3

import sys
import subprocess
import os.path
import getopt
import tempfile
import os
import susy_interface as susy

class BarbieTest():
	def __init__(self, difference_count, first_error_out, first_error_susy, id, path_out, path_susy, path_cmp):
		self.first_error_out = first_error_out
		self.first_error_susy = first_error_susy
		self.difference_count = difference_count
		self.correct = (difference_count==0)
		self.id = id

		self.path_out = path_out
		self.path_susy = path_susy
		self.path_cmp = path_cmp
		self.path_folder = os.path.split(path_susy)[0]


# Execute the code with the input from the in_file and save the output in the out_dir
def exe_code(exec_file, in_file, out_dir, index):
	out = open(os.path.join(out_dir, str(index), in_file.split('.')[0]) + '.out', 'w')
	ins = open(os.path.join(out_dir, str(index), in_file), 'r')
	subprocess.Popen(exec_file, stdin=ins, stdout=out, stderr=out, universal_newlines=True)
	out.close()
	ins.close()

# Execute the code with all the test files
def run_tests(exec_file, in_files, out_dir):
	size = len(in_files)
	__print()
	for i in range(size):
		__print('Executing test %d of %d' %(i+1, size), end='\r')
		exe_code(exec_file, in_files[i], out_dir, i+1)
	__print()

# Compare the code output with the expected result
def compare_susy(susy_file, out_file, index):
	# Open our output and the susy answer
	susy = open(susy_file)
	test = open(out_file)
	path_cmp = susy_file.split('.')[0] + '.cmp'
	# Let's write a .cmp comparison file
	with open(path_cmp, 'w') as barbie_out:

		s_lines = susy.readlines()
		t_lines = test.readlines()

		difference_count = 0
		first_error_out = None
		first_error_susy = None

		# Number of lines of each output
		msg_1 = "Arquivo de resposta: %d Linhas\n" % (len(s_lines))
		msg_2 = "Arquivo de saida: %d Linhas\n" % (len(t_lines))

		# Write to the file
		barbie_out.write(msg_1)
		barbie_out.write(msg_2)


		for i in range(min(len(s_lines), len(t_lines))):
			# If lines are differnt
			if s_lines[i] != t_lines[i]:
				# Save difference
				msg_s = "[%d] susy: %s" % (i, s_lines[i])
				msg_o = "[%d] out:  %s" % (i, t_lines[i])

				if not first_error_out:
					first_error_out = msg_o
					first_error_susy = msg_s

				# Write to file
				barbie_out.write(msg_s)
				barbie_out.write(msg_o)

		# Number of different lines encountered
		difference_count += abs(len(s_lines) - len(t_lines))

		msg_f =  "\nDifference count: %d" % difference_count
		barbie_out.write(msg_f)

		if not difference_count:
			msg_t = "Teste %d: Resultado correto!" % (index)
		else:
			msg_t = "Teste %d: Resultado incorreto. Linhas divergentes: %d" % (index, difference_count)

		__print(msg_t,)


	susy.close()
	test.close()

	return BarbieTest(difference_count, first_error_out, first_error_susy, index, out_file, susy_file, path_cmp)


def _gcc_output_file(source_code):
	return os.path.splitext(source_code[0])[0] + '.gcc'

def compile_c(source_code, temp=False, dir='./'):

	temp_exe, exec_file = tempfile.mkstemp(dir=dir, suffix='.out')
	os.close(temp_exe)

	# Compile source code
	compilation_args = ["gcc", "-Wall", "-o", exec_file] + source_code
	if not temp:
		gcc_out = _gcc_output_file(source_code)
		with open(gcc_out, 'w') as out:
			process = subprocess.run(compilation_args, stdout=out, stderr=subprocess.STDOUT)
	else:
		with tempfile.NamedTemporaryFile() as out:
			process = subprocess.run(compilation_args, stdout=out, stderr=subprocess.STDOUT)

	# Check if the compilation failed, in wich case an Exception is raised
	process.check_returncode()
	# Return the path to the executable file
	return exec_file

def get_local_tests(tests_folder):
	in_files  = []
	res_files = []
	# search for test files in the tests_folder
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
	# Sort the files, so they are executed in order
	in_files.sort()
	res_files.sort()
	return in_files, res_files

def run_and_compare(exec_file, in_files, res_files, tests_dir_name):
	results = list()
	# Excute the tests
	run_tests(exec_file, in_files, tests_dir_name)
	# Check the output of each test
	for arq in res_files:
		test = os.path.splitext(arq)[0]
		index  = res_files.index(arq)+1
		# Compare your output with the expected output got from susy
		results.append(compare_susy(os.path.join(tests_dir_name, str(index), arq), os.path.join(tests_dir_name, str(index), test) + '.out', index))

	return results

def usage():
	__print("""\
	Welcome to Barbie!
	The Susy Simulator


	python3 barbie -e exec.out -u https://susy.ic.unicamp.br:9999/TURMA_DE_MC/N_LAB/dados/testes.html

	Exemplo:
	python3 barbie.py -e lab4 -u https://susy.ic.unicamp.br:9999/mc202d/4/dados/testes.html
	python3 barbie.py -c lab4.c -u https://susy.ic.unicamp.br:9999/mc202d/4/dados/testes.html
	python3 barbie.py -c lab4
	by: Mosquito""")


def main():

	try:
		opts, args = getopt.getopt(sys.argv[1:], "he:c:u:l", ["help", "executable=","code=", "url=", "local"])
	except getopt.GetoptError as err:
		# print help information and exit:
		__print(err)  # will print something like "option -a not recognized"
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

	# We need to receive at least a
	if (not exec_file and not source_code):
		usage()
		sys.exit(2)

	# If the user got us one, compile the source code
	if source_code:
		# Try to compile the source code
		try:
			exec_file = compile_c([source_code])
			__print('Código compilado com sucesso!')
		# If there was a compilation problem
		except subprocess.CalledProcessError:
			# Notificate the user about the problem
			gcc_f = _gcc_output_file(source_code)
			eprint("Falha na compilação!")
			eprint("OUTPUT >>>", gcc_f)
			# Show the compilation output and end the program
			with open(gcc_f, 'r') as gcc:
				eprint(gcc.read())
			sys.exit(1)

	tests_dir_name = os.path.realpath("testes/")
	in_files = None
	res_files = None

	# If the program is not set to run locally and no url was given,
	# prompt user for the class info and discover the url
	if not url and not local:

		disc  =	input("Disciplina: 	")
		turma = input("Turma: 		")
		lab   = input("Lab: 		")
		url = susy.discover_susy_url(disc, turma, lab)

	# The user may input the url from the desired tests page
	if url:
		# List all susy files of open tests
		in_files, res_files = susy.get_susy_files(url)
		# Download all the open tests
		susy.download_tests(url, in_files, res_files, tests_dir_name)

	# Option to run the program locally, and don't acess Susy
	if local:
		in_files, res_files = get_local_tests(tests_dir_name)

	# If we sucessufuly got all needed files,
	# we may run all tests and compare our output with the expected
	if in_files and res_files:
		run_and_compare(exec_file, in_files, res_files, tests_dir_name)

def __print(*args, **kargs):
	if not supress_output:
		print(*args, **kargs)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__=="__main__":
	supress_output = False
	main()
else:
	supress_output = True
	susy.supress_output = True
