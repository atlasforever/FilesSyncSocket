#!/usr/bin/python3

import os
import json
import shutil
from filesctrl import *
from nanomsg import Socket, PAIR, PUB

def file_ctrl(finfo, repo, sock):
	path = os.path.join(repo, finfo["path"])
	if finfo["method"] == "delete":
		os.remove(path)
	elif finfo["method"] == "update" || finfo["method"] == "create":
		size = sock.recv()
		n = 0
		with open(path, "wb") as f:
			while n < size:
				l = sock.recv()
				f.write(l)
			os.utime(path, (os.path.getatime(path), finfo["mtime"]))


def dir_ctrl(finfo, repo):
	path = os.path.join(repo, finfo["path"])
	if finfo["method"] == "delete":
		shutil.rmtree(path, ignore_errors=True)	# remove the whole directory
	elif finfo["method"] == "update":
		os.utime(path, (os.path.getatime(path), finfo["mtime"]))
	elif finfo["method"] == "create":
		try:
			os.makedirs(path)
		except OSError as e:
			if e.error != errno.EEXIST:
				raise


srv_addr = input("Please input the server address\n")
srv_port = input("Please input the server port\n")
repo = input("Please input the REPO directory\n")
if not os.path.isdir(repo):
	exit("Not a valid directory")

host = "tcp://127.0.0.1:50000"
with Socket(PAIR) as s:
	s.connect(host)
	files = json.dumps(filesinfo(repo))
	files = files.encode()
	s.send(files) # send client files list

	diff = conn.recv()	# diff list
	diff = json.loads(diff.decode())

	for finfo in diff:
		if finfo["ftype"] == "directory":
			dir_ctrl(finfo, repo)
		elif finfo["ftype"] == "file":
			file_ctrl(finfo, repo, s)
					

