from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

from Resources.courseEnrolment import UserCourses
from Resources.users import User,Login
from Resources.courses import Course
from Resources.profile import ProfileResource
from Resources.feedback import Feedback
# from Resources.events import Events
from Resources.eventEnrolment import EnrolledEvents

app = Flask(__name__)
api = Api(app)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BUNDLE_ERRORS'] = True

#setting up jwt
app.config["JWT_SECRET_KEY"] = "super-secret"  # we should remember to change this
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

migrations = Migrate(app,db)
db.init_app(app)

#routes
api.add_resource(User, '/users', '/users/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(UserCourses, '/userCourse','/userCourse/<int:id>')
api.add_resource(Course, '/course','/course/<int:id>')
api.add_resource(ProfileResource, '/profile','/profile/<int:id>')
@app.route("/")
def index():
    return "<h1>Welcome to Elimika!</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)