from pyvisca import ViscaServer

server = ViscaServer()

def handler(server_context, command):
	command_name, command_values = command
	print(command_name, command_values, server_context)

server.add_callback(handler)

server.start()
server.join()
