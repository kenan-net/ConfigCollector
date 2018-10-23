#!/usr/bin/python3
import logging
import src.device
import time

logging.basicConfig(format='%(name)s - %(levelname)s:%(message)s', level=logging.INFO)


def process_command_output(error, message):
	if error:
		print("Executing command failed.")
		print("Error message: {0}".format(message))
	else:
		print("Executing command OK.")
		print("Command output: {0}".format(message.decode("utf-8")))
	return


def main():
	# Create a new device. When creating a new device, provide a device IP address, username and password which will be
	# used to establish an SSH connection
	dev = src.device.Device("192.168.1.1", "user", "UseR2218!")
	if dev.is_connected():
		print("Connected to device. Now executing commands...")
		print("Executing command export on the device")
		(error, message) = dev.execute_command("export")
		# process_command_output(error, message)
		logFile = open("log.txt", 'a+')
		logFile.write(time.ctime() + "\n")
		if not error:
			print("Executing command successful! Saving command output to file.")
			result = dev.write_output_to_file(message.decode("utf-8"))
			if result:
				logFile.write("Data saved to config file!\n")
			else:
				logFile.write("Unable to save data to config file!\n")
			logFile.write("*******************************************\n")
			logFile.close()
		else:
			logFile.write("Executing command failed!\n")
			print("Executing command failed.")
			print("Error message: {0}".format(message))
	else:
		print("Not connected to the device")

	print("Exiting now")
	exit(0)

if __name__ == "__main__":
	main()
