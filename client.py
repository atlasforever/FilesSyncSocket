#!/usr/bin/python3

import os
import json
import shutil
from filesctrl import *
from nanomsg import Socket, PAIR, PUB

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

with Socket(PUB) as s:
	s.connect((srv_addr, int(srv_port)))
	files = json.dumps(filesinfo(repo))
	data = files.encode()
	s.send(data) # send client files list

	data = conn.recv()	# diff list
	diff = json.loads(data.decode())

	for finfo in diff:
		if finfo["ftype"] == "directory":
			dir_ctrl(finfo, repo)
		elif finfo["ftype"] == "file":
				

