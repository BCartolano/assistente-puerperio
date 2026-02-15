# -*- coding: utf-8 -*-
# Blueprints da Sophia: auth, chat, health, edu.
# Importe e registre em app.py com app.register_blueprint(bp).

from backend.blueprints.edu_routes import edu_bp
from backend.blueprints.health_routes import health_bp
from backend.blueprints.auth_routes import auth_bp
from backend.blueprints.chat_routes import chat_bp

__all__ = ["edu_bp", "health_bp", "auth_bp", "chat_bp"]
