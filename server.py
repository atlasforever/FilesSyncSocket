#!/usr/bin/python3
import os
import json
import socket
import struct
from filesctrl import *

def difflist(repo, c_list):
	c_list = json.loads(c_list)
	s_list = filesinfo(repo)
	dlist = []
	flag = 0	# if client have the same file
	for s_file in s_list:
		for c_idx in range(len(c_list)):
			# both have a same file
			c_file = c_list[c_idx]
			if c_file == 0:
				continue
			if s_file["path"] == c_file["path"]:
				# update client file only when it's older than the server one
				if s_file["mtime"] > c_file["mtime"]:
					item = dict(path = s_file["path"],
								mtime = s_file["mtime"],
								ftype = s_file["ftype"],
								method = "update")
					dlist.append(item)
				c_list[c_idx] = 0	# leave the one they both have
				flag = 1
				break
		if flag == 0:	# client doesn't have it
			item = dict(path = s_file["path"],
						mtime = s_file["mtime"],
						ftype = s_file["ftype"],
						method = "create")
			dlist.append(item)
		flag = 0
	
	# delete these files which the server doesn't have
	for c_file in c_list:
		if c_file != 0:
			item = dict(path = c_file["path"],
						mtime = c_file["mtime"],
						ftype = c_file["ftype"],
						method = "delete")
			dlist.append(item)
	return dlist



repo = input("Please input the REPO directory\n")
if not os.path.isdir(repo):
	exit("Not a valid path")
port = input("Please input the port listening to\n")
if not port.isdigit():
	exit("Not a valid port number")

host = ""
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((host, int(port)))
	s.listen(1)
	conn, addr = s.accept()
	with conn:
		print("Connected by", addr)
		c_list = conn.recv(4096)
		c_list = c_list.decode()
		diff = difflist(repo, c_list)
		rawdiff = json.dumps(diff).encode()
		size = struct.pack("!1I", len(rawdiff))
		conn.sendall(size)
		conn.sendall(rawdiff)

		for finfo in diff:
			if finfo["ftype"] == "file" and (finfo["method"] == "update"
				 		 or finfo["method"] == "create"):
				path = os.path.join(repo, finfo["path"])
				size = os.path.getsize(path)
				size = struct.pack("!1I", size)
				conn.sendall(size)
				with open(path, "rb") as f:
					l = f.read(1024)
					while l:
						conn.sendall(l)
						l = f.read(1024)
