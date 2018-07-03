
import os.path
import log

# Execute the code with all the test files
def run_tests(user_code, in_files, out_dir, timeout):
	size = len(in_files)
	log.uprint()
	for i in range(size):
		log.uprint('Executing test %d of %d' %(i+1, size), end='\r')
	log.uprint()


class BarbieTest():
	def __init__(self, user_code, susy_file, in_file, directory, index):
		self.id = index
		self.in_file = in_file
		self.susy_file = susy_file
		self.out_file = None

		self.user_code = user_code

		self.directory = directory

		self.first_error_out = None
		self.first_error_susy = None
		self.difference_count = 0
		self.correct = False
		self.cmp_file = None
		self.path_folder = None

	def run(self, timeout=2):
		self.out_file = self.user_code.exe_code(self.in_file, self.directory, self.id, timeout)

    # Compare the code output with the expected result
	def compare(self):
		# Open our output and the susy answer
		susy = open(self.susy_file)
		try:
			test = open(self.out_file)
		except FileNotFoundError:
			folder = os.path.dirname(self.susy_file)
			for file in os.listdir(folder):
				if file.endswith(".out"):
					self.out_file = os.path.join(folder, file)
					break
			test = open(self.out_file)
		self.cmp_file = self.susy_file.split('.')[0] + '.cmp'
		# Let's write a .cmp comparison file
		with open(self.cmp_file, 'w') as barbie_out:

			s_lines = susy.readlines()
			t_lines = test.readlines()

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
						self.first_error_out = msg_o
						self.first_error_susy = msg_s

					# Write to file
					barbie_out.write(msg_s)
					barbie_out.write(msg_o)

					difference_count+=1

			# Number of different lines encountered
			self.difference_count += abs(len(s_lines) - len(t_lines))

			msg_f =  "\nDifference count: %d" % self.difference_count
			barbie_out.write(msg_f+'\n')

			if not self.difference_count:
				msg_t = "Teste %d: Resultado correto!" % (self.id)
			else:
				msg_t = "Teste %d: Resultado incorreto. Linhas divergentes: %d" % (self.id, self.difference_count)

			log.uprint(msg_t,)

		susy.close()
		test.close()

		self.correct = (self.difference_count==0)
