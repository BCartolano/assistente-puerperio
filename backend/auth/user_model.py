# -*- coding: utf-8 -*-
"""Modelo User para Flask-Login (SQLite/users.db). Usado por app.py (user_loader) e blueprints.auth_routes."""
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, name, email, baby_name=None):
        self.id = str(user_id)
        self.name = name
        self.email = email
        self.baby_name = baby_name
