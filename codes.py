import os
import subprocess
import os.path
import tempfile

class CodeLanguage():
	source_files = None
	exec_file = None

	# Execute the code with the input from the in_file and save the output in the out_dir
	def exe_code(self, in_file, out_dir, index, timeout):
		out_file = os.path.join(out_dir, str(index), in_file.split('.')[0]) + '.out'
		out = open(out_file, 'w')
		ins = open(os.path.join(out_dir, str(index), in_file), 'r')
		self.run(stdin=ins, stdout=out, stderr=out, timeout=timeout)
		out.close()
		ins.close()
		return out_file

	def run(self, stdin, stdout, stderr, timeout):
		subprocess.run(self.exec_file, stdin=stdin, stdout=stdout, stderr=stderr, universal_newlines=True, timeout=timeout)

class PythonCode(CodeLanguage):

	python3 = '/usr/bin/python3'

	def run(self, stdin, stdout, stderr, timeout):
		subprocess.run([self.python3, self.exec_file], stdin=stdin, stdout=stdout, stderr=stderr, universal_newlines=True, timeout=timeout)

class CCode(CodeLanguage):
	def __init__(self):
		self.gcc_file = None
		self.compilation_sucess = False

	def run(self, stdin, stdout, stderr, timeout):
		subprocess.run(self.exec_file, stdin=stdin, stdout=stdout, stderr=stderr, universal_newlines=True, timeout=timeout)

	def compile(self, temp=False, dir='./'):
		temp_exe, self.exec_file = tempfile.mkstemp(dir=dir, suffix='.out')
		temp_gcc, self.gcc_file = tempfile.mkstemp(dir=dir, suffix='.gcc')
		os.close(temp_exe)
		os.close(temp_gcc)

		# Compile source codes
		compilation_args = ["gcc", "-Wall", "-o", self.exec_file] + self.source_files
		with open(self.gcc_file, 'w') as out:
			process = subprocess.run(compilation_args, stdout=out, stderr=subprocess.STDOUT)

		try:
			# Check if the compilation failed, in wich case an Exception is raised
			process.check_returncode()
			self.compilation_sucess = True
		except:
			self.compilation_sucess = False
