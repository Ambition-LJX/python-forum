# flask_sqlalchemy
from markupsafe import Markup
from flask_avatars import Avatars
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
mail = Mail()
cache = Cache()
csrf = CSRFProtect()
avatars = Avatars()
jwt = JWTManager()
cors = CORS()
