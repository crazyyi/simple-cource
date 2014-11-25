from flask import url_for

from test_base import BaseTestCase

from flask.ext.login import current_user
from .model import User

class UserViewsTests(BaseTestCase):
	def test_users_can_login(self):
		User(username='Joe', email='joe@joe.com', password='123456')

		response = self.app.post(url_for('users.login'),
			data={'email':'joe@joe.com', 'password':'123456'})
		self.assertTrue(current_user.username=='Joe')
		self.assertFalse(current_user.is_anonymous)
		self.assert_redirects(response, url_for('tracking.index'))

