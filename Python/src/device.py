#!/usr/bin/python3
import logging
import paramiko
import socket
import time
logger = logging.getLogger("Device")


class Device:
	"""
	# This class provides a simpler interface to use the SSH mechanism to connect to a remote device and execute commands
	on the remote device.
	http://docs.paramiko.org/en/2.4/index.html
	"""

	def __init__(self, ip_address, username, password, port=22, firmware=None, description=None):
		"""
		Default class constructor. Called whenever a new object is instantiated.
		Expects IP address of a device, username and password which are used when connecting to the device.
		Those are the mandatory fields.
		Optional fields are port (by default set to 22), firmware version of the device, and the description of the device.
		Parameteres:
		ip_address: string representing IP address of the device to which we want to connect
		username: string username which will be used when connecting to given device
		password: string password which will be used when connecting to given device
		port: integer value representing the port number to be used when connecting
		firmware: string holding the version of the firmware
		description: string representing the description of the device
		"""
		# Device variables
		self._ip_address = ip_address
		self._port = port
		self._username = username
		self._password = password
		self._firmware = firmware
		self._description = description
		self._connectionTimeout = 10

		# Connection variables
		self._client = paramiko.SSHClient()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._connected = False

		# Now connect to the device
		self.__connect()
		if not self._connected:
			logger.error("Connection failed!")
		logger.debug("New Device object created. Device IP: {}".format(ip_address))
		return

	def __del__(self):
		"""
		Default class destructor. Called when the class instance has been deleted.
		:return: No return value.
		"""
		if self._connected:
			self._client.close()
		logger.debug("Device object deleted. Device IP: {}".format(self._ip_address))
		return

	def __connect(self):
		"""
		Private method used to connect to the device.
		:return: No return value. Sets the instance variable "_connected" to True if connection is established
		"""
		logger.info("Connecting to device at {}".format(self._ip_address))
		if not len(self._username):
			logger.error("No username provided!")
			return
		if not len(self._password):
			logger.error("No password provided!")
			return

		try:
			# WARNING - When passing arguments to connect function, there is a passphrase and password!
			# Passphrase is used when you are using a key file and you need a passphrase to unlock the key!
			# Password is used when device expects username/pwssord pair to authenticate.
			self._client.connect(hostname=self._ip_address, port=self._port, username=self._username,
								password=self._password, timeout=self._connectionTimeout, look_for_keys=False)
		except paramiko.ssh_exception.BadHostKeyException:
			logger.error("Host key given by the SSH server did not match what we were expecting.")
			self._client.close()
			return
		except paramiko.ssh_exception.BadAuthenticationType:
			logger.error("Error - bad authentication type. Should you be using public key when authenticating?")
			self._client.close()
			return
		except  paramiko.ssh_exception.AuthenticationException as e:
			logger.error("Error - unable to authenticate. Wrong username/password.")
			self._client.close()
			return
		except paramiko.SSHException:
			logger.error("Error when establishing connection. SSH Exception happened!")
			self._client.close()
			return
		except socket.error as e:
			logger.error("Socket error happened. Error: {0}".format(e))
			self._client.close()
			return
		logger.info("Connected to the device at: {0}".format(self._ip_address))
		self._connected = True
		return

	def is_connected(self):
		"""
		Returns the status of the connection.
		:return: True when connection is established, False otherwise
		"""
		return self._connected

	def execute_command(self, cmd):
		"""
		Executes given command on a remote device and prints the output of the command!
		:param cmd: String command that will be executed on the device.
		:return: It returns tuple (error, message string) where error is boolean and is set to true if executing command
		has failed. Otherwise it is set to false. If error is set to true, message string contains error message, otherwise
		it contains command output
		"""
		# List1 = [12, "Ravi", "B.Com FY", 78.50]  # list
		# Tuple1 = (12, "Ravi", "B.Com FY", 78.50)  # tuple
		# Dictionary1 = {"Rollno": 12, "class": "B.com FY", "percentage": 78.50}  # dictionary
		# List and tuple items are indexed.
		logger.debug("Executing command: {0}".format(cmd))
		try:
			stdin, stdout, stderr = self._client.exec_command(cmd)
		except paramiko.SSHException:
			logger.error("Executing command {0} on device {1} failed.".format(cmd, self._ip_address))
			toBeReturned = (True, "Failed executing command!")
			return toBeReturned
		# WARNING: Once you read stdout or stderr, you loose the buffer and second read will give you empty buffer
		error = stderr.read()
		if len(error):
			logger.error("Executing command failed. Command output: {0}".format(error))
			toBeReturned = (True, error)
			return toBeReturned
		output = stdout.read()
		if len(output):
			logger.debug("Executing command successful. Command output: {0}".format(output))
		toBeReturned = (False, output)
		return toBeReturned

	def get_firmware_version(self):
		"""
		Used to get the firmware version of the device.
		Note: This information is not obtained from the device it self! It was provided when the class instance was created.
		:return: string representing the firmware version
		"""
		return self._firmware

	def get_description(self):
		"""
		Used to get the description of the device. This description was provided when the class instance was created.
		:return: string representing the description of the device
		"""
		return self._description

	def write_output_to_file(self, data):
		"""
		Writes string "data" which is provided as an argument to a text file which will have the name in format:
		username@ip-address.txt
		:param data: String data that will be written to a text file.
		:return: returns True if data has been successfully written to a file, otherwise returns False
		"""
		currentTime = time.localtime()
		year = currentTime.tm_year
		month = currentTime.tm_mon
		day = currentTime.tm_mday
		hour = currentTime.tm_hour
		minute = currentTime.tm_min
		# sec = currentTime.tm_sec
		fileName = "{0}@{1}-{2}-{3}-{4}_{5}-{6}.txt".format(self._username, self._ip_address, year, month, day, hour, minute)
		try:
			logFile = open(fileName, 'w')
		except IOError as e:
			logger.error("Error while creating file. I/O error({0}): {1}".format(e.errno, e.strerror))
			logger.error("Data will not be saved to file.")
			return False
		else:
			logFile.write(data)
			logFile.close()
		return True
