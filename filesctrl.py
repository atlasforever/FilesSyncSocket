#!/usr/bin/python3
import os

def rm_repo_path(path, repo):
	path = path.replace(repo, "")
	if path[0] == "/":
		path = path[1:]
	return path

def filesinfo(repo):
	filelist = []
	for root, dirs, files in os.walk(repo, topdown = False):
		for name in files:
			path = os.path.join(root, name)
			mtime = os.path.getmtime(path)
			ftype = "file"
			path = rm_repo_path(path, repo)
			item = dict(path = path, mtime = mtime, ftype = ftype)
			filelist.append(item)
		for name in dirs:
			dirpath = os.path.join(root, name)
			if not os.listdir(dirpath):
				mtime = os.path.getmtime(dirpath)
				ftype = "directory"
				dirpath = rm_repo_path(dirpath, repo)
				item = dict(path = dirpath, mtime = mtime, ftype = ftype)
				filelist.append(item)
	return filelist


if __name__ == "__main__":
	import json

	repo = input("input repo...")
	info = filesinfo(repo)
	print(info)
