#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, sys
from datetime import datetime
from threading import Thread

HOST = ''		# Symbolic name meaning all available interfaces
PORT = 6666		# Default netconsole client IN Port

def recv():
	global client
	while True:
		data, client = server.recvfrom(max_size)
		sys.stdout.write(data)

def send():
	while True :
		server_input = sys.stdin.readline()
		if server_input == "quit\n" :
			server.sendto("Leave Netconsole Client.\n", client)
			break
		if server_input is not None :
			server.sendto(server_input, client)

if __name__ == "__main__" :
	server_address = (HOST, PORT)
	max_size = 4096

	print "Liscen to port %d" % PORT

	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server.bind(server_address)

	th_recv = Thread(target = recv)
	th_send = Thread(target = send)
	th_recv.setDaemon(True)
	th_send.setDaemon(True)
	th_recv.start()
	th_send.start()

	th_send.join()
	server.close()
