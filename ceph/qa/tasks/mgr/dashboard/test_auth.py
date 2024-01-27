# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

import jwt
from teuthology.orchestra.run import \
    CommandFailedError  # pylint: disable=import-error

from .helper import DashboardTestCase


class AuthTest(DashboardTestCase):

    AUTO_AUTHENTICATE = False

    def setUp(self):
        super(AuthTest, self).setUp()
        self.reset_session()

    def _validate_jwt_token(self, token, username, permissions):
        payload = jwt.decode(token, options={'verify_signature': False})
        self.assertIn('username', payload)
        self.assertEqual(payload['username'], username)

        for scope, perms in permissions.items():
            self.assertIsNotNone(scope)
            self.assertIn('read', perms)
            self.assertIn('update', perms)
            self.assertIn('create', perms)
            self.assertIn('delete', perms)

    def test_login_without_password(self):
        with self.assertRaises(CommandFailedError):
            self.create_user('admin2', '', ['administrator'])

    def test_a_set_login_credentials(self):
        # test with Authorization header
        self.create_user('admin2', 'admin2', ['administrator'])
        self._post("/api/auth", {'username': 'admin2', 'password': 'admin2'})
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin2", data['permissions'])
        self.delete_user('admin2')

        # test with Cookies set
        self.create_user('admin2', 'admin2', ['administrator'])
        self._post("/api/auth", {'username': 'admin2', 'password': 'admin2'}, set_cookies=True)
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin2", data['permissions'])
        self.delete_user('admin2')

    def test_login_valid(self):
        # test with Authorization header
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'})
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin", data['permissions'])

        # test with Cookies set
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'}, set_cookies=True)
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin", data['permissions'])

    def test_login_invalid(self):
        # test with Authorization header
        self._post("/api/auth", {'username': 'admin', 'password': 'inval'})
        self.assertStatus(400)
        self.assertJsonBody({
            "component": "auth",
            "code": "invalid_credentials",
            "detail": "Invalid credentials"
        })

        # test with Cookies set
        self._post("/api/auth", {'username': 'admin', 'password': 'inval'}, set_cookies=True)
        self.assertStatus(400)
        self.assertJsonBody({
            "component": "auth",
            "code": "invalid_credentials",
            "detail": "Invalid credentials"
        })

    def test_logout(self):
        # test with Authorization header
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'})
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin", data['permissions'])
        self.set_jwt_token(data['token'])
        self._post("/api/auth/logout")
        self.assertStatus(200)
        self.assertJsonBody({
            "redirect_url": "#/login"
        })
        self._get("/api/host")
        self.assertStatus(401)
        self.set_jwt_token(None)

        # test with Cookies set
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'}, set_cookies=True)
        self.assertStatus(201)
        data = self.jsonBody()
        self._validate_jwt_token(data['token'], "admin", data['permissions'])
        self.set_jwt_token(data['token'])
        self._post("/api/auth/logout", set_cookies=True)
        self.assertStatus(200)
        self.assertJsonBody({
            "redirect_url": "#/login"
        })
        self._get("/api/host", set_cookies=True)
        self.assertStatus(401)
        self.set_jwt_token(None)

    def test_token_ttl(self):
        # test with Authorization header
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '5'])
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'})
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host")
        self.assertStatus(200)
        time.sleep(6)
        self._get("/api/host")
        self.assertStatus(401)
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '28800'])
        self.set_jwt_token(None)

        # test with Cookies set
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '5'])
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'}, set_cookies=True)
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host", set_cookies=True)
        self.assertStatus(200)
        time.sleep(6)
        self._get("/api/host")
        self.assertStatus(401)
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '28800'])
        self.set_jwt_token(None)

    def test_remove_from_blacklist(self):
        # test with Authorization header
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '5'])
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'})
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        # the following call adds the token to the blacklist
        self._post("/api/auth/logout")
        self.assertStatus(200)
        self._get("/api/host")
        self.assertStatus(401)
        time.sleep(6)
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '28800'])
        self.set_jwt_token(None)
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'})
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        # the following call removes expired tokens from the blacklist
        self._post("/api/auth/logout")
        self.assertStatus(200)

        # test with Cookies set
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '5'])
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'}, set_cookies=True)
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        # the following call adds the token to the blocklist
        self._post("/api/auth/logout", set_cookies=True)
        self.assertStatus(200)
        self._get("/api/host", set_cookies=True)
        self.assertStatus(401)
        time.sleep(6)
        self._ceph_cmd(['dashboard', 'set-jwt-token-ttl', '28800'])
        self.set_jwt_token(None)
        self._post("/api/auth", {'username': 'admin', 'password': 'admin'}, set_cookies=True)
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        # the following call removes expired tokens from the blocklist
        self._post("/api/auth/logout", set_cookies=True)
        self.assertStatus(200)

    def test_unauthorized(self):
        # test with Authorization header
        self._get("/api/host")
        self.assertStatus(401)

        # test with Cookies set
        self._get("/api/host", set_cookies=True)
        self.assertStatus(401)

    def test_invalidate_token_by_admin(self):
        # test with Authorization header
        self._get("/api/host")
        self.assertStatus(401)
        self.create_user('user', 'user', ['read-only'])
        time.sleep(1)
        self._post("/api/auth", {'username': 'user', 'password': 'user'})
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host")
        self.assertStatus(200)
        time.sleep(1)
        self._ceph_cmd_with_secret(['dashboard', 'ac-user-set-password', 'user'], 'user2')
        time.sleep(1)
        self._get("/api/host")
        self.assertStatus(401)
        self.set_jwt_token(None)
        self._post("/api/auth", {'username': 'user', 'password': 'user2'})
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host")
        self.assertStatus(200)
        self.delete_user("user")

        # test with Cookies set
        self._get("/api/host", set_cookies=True)
        self.assertStatus(401)
        self.create_user('user', 'user', ['read-only'])
        time.sleep(1)
        self._post("/api/auth", {'username': 'user', 'password': 'user'}, set_cookies=True)
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host", set_cookies=True)
        self.assertStatus(200)
        time.sleep(1)
        self._ceph_cmd_with_secret(['dashboard', 'ac-user-set-password', 'user'], 'user2')
        time.sleep(1)
        self._get("/api/host", set_cookies=True)
        self.assertStatus(401)
        self.set_jwt_token(None)
        self._post("/api/auth", {'username': 'user', 'password': 'user2'}, set_cookies=True)
        self.assertStatus(201)
        self.set_jwt_token(self.jsonBody()['token'])
        self._get("/api/host", set_cookies=True)
        self.assertStatus(200)
        self.delete_user("user")
