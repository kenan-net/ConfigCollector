#!/usr/bin/python3
import os
import mysql.connector
import logging
from mysql.connector import errorcode

logger = logging.getLogger("Database")


# noinspection PyPep8Naming
class Database:
	"""

	"""

	def __init__(self, dbHost = None, dbPort = None, dbName = None, dbUser = None, dbPass = None, dbConfigFile = None):
		"""
		Default class constructor. Used to initialize the class object.
		Class object can be initialized using the arguments or using the database configuration file which is an XML
		file which contains all the necessary data to connect to the MySQL server.
		:param dbHost: string containing the address of the MySQL server
		:param dbPort: integer containing the port on which the MySQL server is listening for connection requests
		:param dbName: string representing the name of the database that we are going to be using
		:param dbUser: string representing the username for given MySQL server and database
		:param dbPass: string representing the password for given user
		:param dbConfigFile: string representing the path to a databace configuration file which can be used instead of
		all previous arguments. If this path is set to something other than None than this file will be used and other
		arguments will be ignored!
		"""
		# Initialization of class instance variables
		self._dbHost = None
		self._dbPort = None
		self._dbName = None
		self._dbUser = None
		self._dbPass = None
		self._initialized = False
		self._connected = False
		self._connection = None
		logger.debug("Initializing database class object")
		if dbConfigFile is not None:
			logger.debug("Path to database configuration file provided")
			if not os.path.isfile(dbConfigFile):
				logger.error("Path to configuration file provided but file not found at provided path!")
				return
			else:
				logger.debug("Configuration file exists. Using configuration file at path: {0}".format(dbConfigFile))

			# Parse the XML file and extract information's from that file
			from xml.dom.minidom import parse
			import xml.dom.minidom
			DOMTree = xml.dom.minidom.parse(dbConfigFile)
			xmlRootElement = DOMTree.documentElement
			if xmlRootElement.hasAttribute("database"):
				# There should be only one root element!
				logger.debug("Initializing with values from XML file")
				# TODO Maybe check if the element exists first
				dbHost = xmlRootElement.getElementsByTagName("dbHost")[0]
				self._dbHost = dbHost.childNodes[0].data
				dbPort = xmlRootElement.getElementsByTagName("dbPort")[0]
				self._dbPort = dbPort.childNodes[0].data
				dbName = xmlRootElement.getElementsByTagName("dbName")[0]
				self._dbName = dbName.childNodes[0].data
				dbUser = xmlRootElement.getElementsByTagName("dbUser")[0]
				self._dbUser = dbUser.childNodes[0].data
				dbPass = xmlRootElement.getElementsByTagName("dbPass")[0]
				self._dbPass = dbPass.childNodes[0].data
				# For more debugging options, we can print the values which have been used to initialize the object
				self.__print_values()
				# It seems that everything went well. We have initialized the class object.
				self._initialized = True
			else:
				# Root element not found.
				logger.error("Failed parsing XML file. Please check your configuration file!")
				return
		elif (dbHost is None) or (dbPort is None) or (dbName is None) or (dbUser is None) or (dbPass is None):
			logger.error("Unable to initialize class object! Insufficient number of arguments or wrong arguments.")
			return
		else:
			# All the necessary arguments are provided. We can initialize the Database class object.
			logger.debug("Path to database configuration file not provided. Using constructor arguments.")
			self._dbHost = dbHost
			self._dbPort = dbPort
			self._dbName = dbName
			self._dbUser = dbUser
			self._dbPass = dbPass
			self.__print_values()
			self._initialized = True
			return

	def __del__(self):
		"""
		Default class destructor. Called whenever a class instance (object) is deleted. Does the clean-up.
		:return: None
		"""
		if self._connected:
			self._connection.close()
		logger.info("Database class object deleted.")
		return

	def isInitialized(self):
		"""
		Used to inform the user that the class object is properly initialized.
		Main purpose of this method is to be used with automated test.
		:return: boolean value. True if object is successfully initialized, otherwise returns False!
		"""
		return self._initialized

	def isConnected(self):
		"""
		Returns the last known status of the connection with MySQL server.
		:return: boolean value. True if connected to the server, otherwise returns False
		"""
		return self._connected

	def connect2database(self):
		"""
		Connects to the MySQL database server and if connection is successful, selects the database.
		Database which will be selected is the one which was provided in the constructor either as an argument of the
		constructor or in the configuration file. Also, if connection was successful, sets the proper flag to True,
		otherwise to false.
		:return: boolean value. True if connection successful, otherwise returns False. Also sets the object "connected"
		flag accordingly.
		"""
		logger.info("Connecting to database...")
		if not self._initialized:
			logger.error("Connecting to database failed. Object not initialized properly!")
			self._connected = False
			return

		try:
			cnx = mysql.connector.connect(user=self._dbUser, password=self._dbPass, host=self._dbHost, port=self._dbPort)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				logger.error("Connecting to database server failed. Wrong username and/or password!")
				self._connected = False
				return False
			else:
				logger.error("Connecting to database server failed. Error: {0}".format(err.msg))
				self._connected = False
				return False

		# We are now connected to the MySQL server. Select the database
		logger.info("Connection with MySQL server established. Selecting database...")
		try:
			cnx.database = self._dbName
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_BAD_DB_ERROR:
				logger.warning("Database with given name {0} does not exist.".format(self._dbName))
				# TODO Maybe we can create a database?
				self._connected = False
				cnx.close()
				return False
			else:
				logger.error("Selecting database failed! Error: {0}".format(err.msg))
				self._connected = False
				cnx.close()
				return False

		# If database exists, check if it contains all the necessary table's used to store device specific data. If the
		# tables are not there, we should create them. This will ensure that on every start we are checking for the
		# tables and if one of them is not there, it will be created!
		# TODO Check if the tables exist - we need to know which tables
		self._connected = True
		self._connection = cnx
		logger.info("Connection with MySQL database server successful! Database selected.")
		return True

	@staticmethod
	def createDatabaseIfNonExisting(dbHost=None, dbPort=None, dbName=None, dbUser=None, dbPass=None):
		"""

		:param dbHost:
		:param dbPort:
		:param dbName:
		:param dbUser:
		:param dbPass:
		:return:
		"""
		if (dbHost is None) or (dbPort is None) or (dbName is None) or (dbUser is None) or (dbPass is None):
			# Some of the arguments is missing! We need all of this to connect to a database server and create a database
			logger.error("Some of the expected arguments is not provided.")
			return False
		# We have all we need. Establish a connection
		try:
			cnx = mysql.connector.connect(user=dbUser, password=dbPass, host=dbHost, port=dbPort)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				logger.error("Connecting to database server failed. Wrong username and/or password!")
				return False
			else:
				logger.error("Connecting to database server failed. Error: {0}".format(err.msg))
				return False

		# We are now connected to the MySQL server. Select the database
		logger.info("Connection with MySQL server established. Creating database...")
		try:
			cnx.database = dbName
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_BAD_DB_ERROR:
				logger.warning("Database with given name {0} does not exist. We will try to create it.".format(dbName))
				try:
					cursor = cnx.cursor()
				except mysql.connector.Error as err:
					logger.error("Failed creating cursor. Error: {0}".format(err.msg))
					cnx.close()
					return False
				# Cursor was created. Now we can try executing MySQL statement
				try:
					cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dbName))
				except mysql.connector.Error as err:
					logger.error("Failed creating database! Error: {0}".format(err.msg))
					cnx.close()
					return False
				# Statement executed correctly
				cnx.close()
				logger.info("Database {0} was successfully created".format(dbName))
				return True
			else:
				logger.error("Selecting database failed! Error: {0}".format(err.msg))
				cnx.close()
				return False
			# None of the exceptions happened -> Database exists!
		logger.warning("Database with given name already exists! Database will not be created again!")
		cnx.close()
		return True

	def __executeSqlStatement(self, sqlStatement):
		"""

		:param sqlStatement:
		:return:
		"""
		try:
			cursor = self._connection.cursor()
		except mysql.connector.Error as err:
			logger.error("Error! Failed creating cursor. Error: {0}".format(err.msg))
			return False
		# Cursor was created. Now we can try executing MySQL statement
		try:
			cursor.execute(sqlStatement)
		except mysql.connector.Error as err:
			logger.error("Error! Failed executing MySQL statement! Error: {0}".format(err.msg))
			return False
		# Statement executed correctly
		return True

	def __print_values(self):
		"""

		:return: No return value
		"""
		logger.debug("Object is initialized with the following values:")
		logger.debug("Host: {0}@{1}".format(self._dbHost, self._dbPort))
		logger.debug("Database name: {0}".format(self._dbName))
		logger.debug("Username: {0}".format(self._dbUser))
		logger.debug("Password: {0}".format(self._dbPass))