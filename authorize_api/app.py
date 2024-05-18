from flask import Flask
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')

jwt = JWTManager(app)
redis_client = FlaskRedis(app)
db = SQLAlchemy(app)

from models import User
with app.app_context():
    db.create_all()

from auth import auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
