from .visca import Visca
import threading
import socket

class ViscaServer(threading.Thread):
	def __init__(self):
		super().__init__()
		self.context = {
			"tilt_absolute": -16384,
			"pan_absolute": -16384,
			"zoom": -16384,
			"focus": -16384,
		}

		self.visca = Visca()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.setblocking(False)
		self.socket.bind(('127.0.0.1', 1259))

		self.callbacks = []

	def add_callback(self, fn):
		self.callbacks.append(fn)

	def run(self) -> None:
		while True:
			try:
				command, address = self.socket.recvfrom(1024)

				result = self.visca.parse(command)
				if result:
					print(*result)
					if result[0].endswith("Inquery"):
						reponse = self.visca.build(result[0]+"Response", self.context)
						# print(result[0]+"Response", reponse)
						self.socket.sendto(reponse, address)

					for fn in self.callbacks:
						fn(
							self.context,
							result
						)

				else:
					print("Unknown command", command)

			except socket.error:
				pass