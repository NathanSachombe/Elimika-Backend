from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)
api = Api(app)
CORS(app)
bcrypy = Bcrypt(app)
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BUNDLE_ERRORS'] = True

#setting up jwt
app.config["JWT_SECRET_KEY"] = "super-secret"  # we should remember to change this
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

migrations = Migrate(app,db)
db.init_app(app)


@app.route("/")
def index():
    return "<h1>Welcome to Elimika!</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)