#!/usr/bin/python3
import logging
import src.Device

logging.basicConfig(format='%(name)s - %(levelname)s:%(message)s', level=logging.INFO)


def process_command_output (error, message):
	if error:
		print("Executing command failed.")
		print("Error message: {0}".format(message))
	else:
		print("Executing command OK.")
		print("Command output: {0}".format(message))
	return


def main():
	# Create a new device. When creating a new device, provide a device IP address, username and password which will be
	# used to establish an SSH connection
	dev = src.Device.Device("192.168.0.19", "pi", "raspberry")
	if dev.is_connected():
		print("Connected to device. Now executing commands...")
		(error, message) = dev.execute_command("pwd")
		process_command_output(error, message)

		(error, message) = dev.execute_command("ls")
		process_command_output(error, message)

	else:
		print("Not connected to the device")


if __name__ == "__main__":
	main()
