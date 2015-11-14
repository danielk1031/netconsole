#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import argparse
from datetime import datetime
from threading import Thread

HOST = ''		# Symbolic name meaning all available interfaces
PORT = 6666		# Default netconsole client IN Port

# Netconsole Client
class Netconsole():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.max_size = 4096
		self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_addr = (host, port)
		self.client.bind(self.client_addr)
		self.stopflag = 0
		self.server = None

	def _recv(self):
		while True:
			self.data, self.server = self.client.recvfrom(self.max_size)
			if args.HOST != '':
				if self.server[0] == args.HOST:
					sys.stdout.write(self.data)
			else:
				sys.stdout.write(self.data)

	def _send(self):
		while True:
			self.client_input = sys.stdin.readline()
			if self.client_input == "quit\n":
				if self.server is not None:
					self.client.sendto("Leave Netconsole Client.\n", self.server)
				break
			if self.client_input is not None:
				if self.server is not None:
					self.client.sendto(self.client_input, self.server)

	def worker_send(self):
		th_send = Thread(target = self._send)
		th_send.setDaemon(True)
		th_send.start()
		th_send.join()
		self.stopflag = 1

	def worker_recv(self):
		th_recv = Thread(target = self._recv)
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
	args = parser.parse_args()
	return args

if __name__ == "__main__" :
	args = argv_gen()
	client1 = Netconsole(HOST, args.PORT)
	if args.HOST == '':
		print "Listen to port %d" % args.PORT
	else :
		print "Listen to port %d, target is %s" % (args.PORT, args.HOST)
	client1.worker_recv()
	client1.worker_send()
	client1.close()
