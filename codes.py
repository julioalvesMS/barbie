import os
import subprocess

class CodeLanguage():
	source_files = None
	exec_file = None

	def run(self, stdin, stdout, stderr, timeout=200):
		pass

class PythonCode(CodeLanguage):

	python3 = '/usr/bin/python3'

	def run(self, stdin, stdout, stderr, timeout=200):
		subprocess.run([self.python3, self.exec_file], stdin=stdin, stdout=stdout, stderr=stderr, universal_newlines=True, timeout=timeout)

class CCode(CodeLanguage):
	def run(self, stdin, stdout, stderr, timeout=200):
		subprocess.run(self.exec_file, stdin=stdin, stdout=stdout, stderr=stderr, universal_newlines=True, timeout=timeout)
