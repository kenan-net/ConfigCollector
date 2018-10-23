import unittest
import logging

from src.Database import Database

logging.basicConfig(format='%(name)s - %(levelname)s:%(message)s', level=logging.INFO)


class MySQLDatabaseTests(unittest.TestCase):
	def test_aa_create_database(self):
		"""

		:return:
		"""
		print("Testing creation of database")
		result = Database.createDatabaseIfNonExisting(dbHost="localhost", dbPort=3306, dbName="testDatabase", dbUser="test", dbPass="test")
		self.assertTrue(result, "Creating database if it does not exist failed!")
		return

	def test__ab_constructor_with_arguments(self):
		print("Testing Database class constructor with arguments (No configuration file)")
		databaseObject = Database(dbHost="localhost", dbPort=3306, dbName="Name", dbUser="user", dbPass="pass")
		self.assertTrue(databaseObject.isInitialized(), "Creating database object with arguments failed.")
		return

	def test_ac_constructor_with_config_file(self):
		print("Testing Database class constructor with configuration file")
		databaseObject = Database(dbConfigFile="c:mysql.xml")
		self.assertTrue(databaseObject.isInitialized(), "Creating database object with configuration file failed.")
		return

	def test_ad_connection(self):
		print("Testing connection to the database server")
		databaseObject = Database(dbHost="localhost", dbPort=3306, dbName="testDatabase", dbUser="test", dbPass="test")
		self.assertTrue(databaseObject.connect2database(), "Connecting to database failed.")
		return


if __name__ == '__main__':
	unittest.main()
