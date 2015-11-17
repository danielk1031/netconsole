#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import argparse
import termios
import fcntl
import os
import time
from datetime import datetime
from threading import Thread

HOST = ''		# Symbolic name meaning all available interfaces
PORT = 6666		# Default netconsole client IN Port

# Netconsole Client
class Netconsole():
	def __init__(self, host, port, c_sigint):
		self.host = host
		self.port = port
		self.c_sigint = c_sigint
		self.max_size = 4096
		self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_addr = (host, port)
		self.client.bind(self.client_addr)
		self.stopflag = 0
		self.server = None

	def __recv(self):
		while True:
			self.data, self.server = self.client.recvfrom(self.max_size)
			if args.HOST != '':
				if self.server[0] == args.HOST:
					sys.stdout.write(self.data)
			else:
				sys.stdout.write(self.data)

	def __send(self):
		while True:
			try:
				self.client_input = sys.stdin.read(1)
			except IOError:
				time.sleep(0.001)
				continue
			if self.client_input == self.c_sigint:
				print "\nLeave Netconsole Client.\n"
				termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
				fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
				break
			else:
				if self.server is not None:
					self.client.sendto(self.client_input, self.server)

	def worker_send(self):
		th_send = Thread(target = self.__send)
		th_send.setDaemon(True)
		th_send.start()
		th_send.join()
		self.stopflag = 1

	def worker_recv(self):
		th_recv = Thread(target = self.__recv)
		th_recv.setDaemon(True)
		th_recv.start()

	def close(self):
		while self.stopflag == 0 :
			pass
		self.client.close()


def argv_gen():
	parser = argparse.ArgumentParser(description='A Python Based Netconsole Client')
	parser.add_argument('--ip', type=str, action="store", dest='HOST',
			default='', help="Specify ip address to listen. Default is ''")
	parser.add_argument('-p', '--port', type=int, action="store", dest='PORT',
			default=6666, help="Specify port to listen. Default 6666 is used.")
	parser.add_argument('-q', '--quit', type=str, action="store", dest='C_SIGINT',
			default="\x14", help="Specify input to quit netconsole. Default ^T is used.")
	args = parser.parse_args()
	return args

def nonblocking_stdin():
	global fd, oldterm, oldflags
	fd = sys.stdin.fileno()
	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)
	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

def def_C_SIGINT(c_sigint):
	ret = c_sigint[0]
	asciitbl = { '@': "\x00", 'A': "\x01", 'B': "\x02", 'C': "\x03", 'D': "\x04",
			'E': "\x05", 'F': "\x06", 'G': "\x07", 'H': "\x08", 'I': "\x09",
			'J': "\x0a", 'K': "\x0b", 'L': "\x0c", 'M': "\x0d", 'N': "\x0e",
			'O': "\x0f", 'P': "\x10", 'Q': "\x11", 'R': "\x12", 'S': "\x13",
			'T': "\x14", 'U': "\x15", 'V': "\x16", 'W': "\x17", 'X': "\x18",
			'Y': "\x19", 'Z': "\x1a", '[': "\x1b", '\\': "\x1c", ']': "\x1d",
			'^': "\x1e", '_': "\x1f", '?': "\x7f" }

	if c_sigint.upper()[:5] in ["CTRL+", "CTRL-"]:
		ret = asciitbl.get(c_sigint[5].upper(), "\x14")
	elif c_sigint[0] == "^":
		ret = asciitbl.get(c_sigint[1].upper(), "\x14")
	else:
		if len(c_sigint) != 1:
			return ("\x14", "^T")
		try:
			c_sigint[0].decode("ascii")
		except: # using default
			ret = "\x14"
			quitstr = "^T"

	if ret == c_sigint[0] and ret != "\x14":
		quitstr = ret
	else:
		quitstr = "^" + [k for k, v in asciitbl.iteritems() if v == ret][0]

	return (ret, quitstr)

if __name__ == "__main__" :
	args = argv_gen()
	nonblocking_stdin()

	args.C_SIGINT, quitstr = def_C_SIGINT(args.C_SIGINT)
	print "Using %s to quit this Netconsole Client" % quitstr
	if args.HOST == '':
		print "Listen to port %d" % args.PORT
	else :
		print "Listen to port %d, target is %s" % (args.PORT, args.HOST)

	client1 = Netconsole(args.HOST, args.PORT, args.C_SIGINT)
	client1.worker_recv()
	client1.worker_send()
	client1.close()
