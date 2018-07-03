
import os
import sys

supress_output = False
to_be_deleted = list()

def uprint(*args, **kargs):
	if not supress_output:
		print(*args, **kargs)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def exit(*args, **kwargs):
	for file in to_be_deleted:
		os.remove(file)
	sys.exit(*args, **kwargs)
