#!/usr/bin/python3

import os
import json
import shutil
import socket
import struct
from filesctrl import *

def file_ctrl(finfo, repo, sock):
	path = os.path.join(repo, finfo["path"])
	if finfo["method"] == "delete":
		os.remove(path)
	elif finfo["method"] == "update" or finfo["method"] == "create":
		size = sock.recv(4)
		size = struct.unpack("!1I", size)[0]
		if not os.path.exists(os.path.dirname(path)):
			try:
				os.makedirs(os.path.dirname(path))
			except OSError as e:
				if e.error != errno.EEXIST:
					raise
		with open(path, "wb") as f:
			n = 0
			while n < size:
				l = sock.recv(1024)
				f.write(l)
				n = n + len(l)
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((srv_addr, int(srv_port)))
	files = json.dumps(filesinfo(repo))
	files = files.encode()
	s.sendall(files) # send client files list

	size = s.recv(4)
	size = struct.unpack("!1I", size)[0]
	diff = s.recv(size)	# diff list
	diff = json.loads(diff.decode())

	for finfo in diff:
		if finfo["ftype"] == "directory":
			dir_ctrl(finfo, repo)
		elif finfo["ftype"] == "file":
			file_ctrl(finfo, repo, s)
