#!/usr/bin/python3
import logging
from Device import Device

logging.basicConfig(format='%(name)s - %(levelname)s:%(message)s', level=logging.INFO)


def main():
	# Create a new device. When creating a new device, provide a device IP address, username and password which will be
	# used to establish an SSH connection
	dev = Device("192.168.0.19", "pi", "raspberry")
	if dev.is_connected():
		print("Executing commands")
		dev.execute_command("ls")
		dev.execute_command("pwd")
	else:
		print("Not connected to the device")


if __name__ == "__main__":
	main()
