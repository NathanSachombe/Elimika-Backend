from flask import Flask
from flask_jwt_extended import JWTManager,jwt_required,get_jwt_identity
from models import db,EventModel,UserEventModel,UserModel
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
from Resources.events import Events
from Resources.eventEnrolment import EnrolledEvents
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)
api = Api(app)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

#email configuration
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kevin.wanjiru600@gmail.com'
app.config['MAIL_PASSWORD'] = 'jjpsewfynmpgkeom'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


#database and error handling setup
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
api.add_resource(EnrolledEvents,'/enrolledEvent','/enrolledEvent/<int:id>')
api.add_resource(Feedback,'/feedback','/feedback/<int:id>')
api.add_resource(Events,'/event','/event/<int:id>')
api.add_resource(ProfileResource, '/profile','/profile/<int:id>')


#Function to send a booking confirmation email 
def send_booking_confirmation_email(email,event_title,username):
    msg = Message('Event Booking Confirmation', sender='kevin.wanjiru600@example.com', recipients=[email])
    msg.body = f'Dear {username} You have successfully booked for the event:{event_title} , Hope you enjoy the Event!'
    mail.send(msg)

@app.route('/enrolledEvent', methods=['POST'])
@jwt_required()
def post():
    data = EnrolledEvents.enrolledEvent_parser.parse_args()
    current_user_id = get_jwt_identity()
    check_event_existence = EventModel.query.get(data['event_id'])

    if not check_event_existence:
        return {"message": "Event not found"}, 404

    existing_booking = UserEventModel.query.filter_by(user_id=current_user_id, event_id=data['event_id']).first()

    if existing_booking:
        # User has already booked for this event
        return {"message": "You have already booked for this event"}, 400
        
    # getting the capacity of the event a person is booking tor so that he cant book if no space
    event = EventModel.query.get(data['event_id'])
    if event.capacity <= 0:
        return {"message": "Event is already fully booked"}, 400

    # Decrementing  event capacity when a user succesfully books an event
    event.capacity -= 1
    db.session.commit()

    data['user_id'] = current_user_id
    new_event = UserEventModel(**data)
        
    db.session.add(new_event)
    db.session.commit()
    user = UserModel.query.filter_by(id = current_user_id).first()
    email = user.email
    username = user.username
    event_title = event.title
    if email and event_title:
        send_booking_confirmation_email(username,email,event_title )
    else:
        return {"message": "Email not found"}, 404
        
    return {"message": "Event booked successfully"}, 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)