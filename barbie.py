#!/usr/bin/env python3

import sys
import subprocess
import os.path
import getopt

# Execute the code with the input from the in_file and save the output in the out_dir
def exe_code(exec_file, in_file, out_dir, index):
	out = open(os.path.join(out_dir, str(index), in_file.split('.')[0]) + '.out', 'w')
	ins = open(os.path.join(out_dir, str(index), in_file), 'r')
	subprocess.Popen(exec_file, stdin=ins, stdout=out, stderr=subprocess.STDOUT, universal_newlines=True)
	out.close()
	ins.close()

# Execute the code with all the test files
def run_tests(exec_file, in_files, out_dir):
	size = len(in_files)
	print()
	for i in range(size):
		print('Executing test %d of %d' %(i+1, size), end='\r')
		exe_code(exec_file, in_files[i], out_dir, i+1)
	print()

# Compare the code output with the expected result
def compare_susy(susy_file, out_file, index):
	# Open our output and the susy answer
	# Let's write a .cmp comparison file
	with open(susy_file.split('.')[0] + '.cmp', 'w') as barbie_out:

		s_lines = susy.readlines()
		t_lines = test.readlines()

	# Let's write a .cmp comparison file
	with open(susy_file.split('.')[0] + '.cmp', 'w') as barbie_out:

		s_lines = susy.readlines()
		t_lines = test.readlines()

		difference_count = 0

		# Number of lines of each output
		msg_1 = "Susy file: %s with %d lines\n" % (susy_file, len(s_lines))
		msg_2 = "Test file: %s with %d lines\n" % (out_file, len(t_lines))

		# Write to the file
		barbie_out.write(msg_1)
		barbie_out.write(msg_2)


		for i in range(min(len(s_lines), len(t_lines))):
			# If lines are differnt
			if s_lines[i] != t_lines[i]:
				# Save difference
				msg_s = "[%d] susy: %s" % (i, s_lines[i])
				msg_o = "[%d] out:  %s" % (i, t_lines[i])

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

	# Compile source code
	compilation_args = ["gcc", "-Wall", source_code, "-o", exec_file]
	with open(gcc_out, 'w') as out:
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
	# Excute the tests
	run_tests(exec_file, in_files, tests_dir_name)
	# Check the output of each test
	for arq in res_files:
		test = os.path.splitext(arq)[0]
		index  = res_files.index(arq)+1
		# Compare your output with the expected output got from susy
		compare_susy(os.path.join(tests_dir_name, str(index), arq), os.path.join(tests_dir_name, str(index), test) + '.out', index)

def usage():
	print("""\
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

	# We need to receive at least a
	if (not exec_file and not source_code):
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

	# If the program is not set to run locally and no url was given,
	# prompt user for the class info and discover the url
	if not url and not local:
		import susy_interface as susy

		disc  =	input("Disciplina: 	")
		turma = input("Turma: 		")
		lab   = input("Lab: 		")
		url = susy.discover_susy_url(disc, turma, lab)

	# The user may input the url from the desired tests page
	elif url:
		import susy_interface as susy
		# List all susy files of open tests
		in_files, res_files = susy.get_susy_files(url)
		# Download all the open tests
		susy.download_tests(url, in_files, res_files, tests_dir_name)

	# Option to run the program locally, and don't acess Susy
	elif local:
		in_files, res_files = get_local_tests(tests_dir_name)

	# If we sucessufuly got all needed files,
	# we may run all tests and compare our output with the expected
	if in_files and res_files:
		run_and_compare(exec_file, in_files, res_files, tests_dir_name)


if __name__=="__main__":
	main()
