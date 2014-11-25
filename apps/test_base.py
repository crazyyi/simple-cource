import unittest2 as unittest

class BaseTestCase(unittest.TestCase):
	"""A base test case for flask-tracking."""

	def create_app(self):
		app.config.from_object('config.TestConfiguration')
		return app

	def setUp(self):
		pass

	def tearDown(self):
		pass