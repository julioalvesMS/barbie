import os

class BarbieCall:
    def __init__(self):
        self.code_files = None
        self.executable_file = None
        self.timeout = 2
        self.local = False
        self.test_files_url = None

        self.disciplina = None
        self.turma = None
        self.codigo_lab = None

        self.directory = os.getcwd()
