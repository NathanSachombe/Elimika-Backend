from flask import Flask,request,flash, jsonify, url_for
from flask_jwt_extended import JWTManager,jwt_required,get_jwt_identity,create_access_token,create_refresh_token
from models import db,EventModel,UserEventModel,UserModel
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
from itsdangerous import URLSafeSerializer
from sqlalchemy import or_
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

#serializer secret
serializer = URLSafeSerializer('thisismysecrekicanttellanyone')
#secret key for the app 
app.secret_key = 'thisisasectret'
#database and error handling setup
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BUNDLE_ERRORS'] = True

#setting up jwt
app.config["JWT_SECRET_KEY"] = "thisisasecrettoeveryone"  # we should remember to change this
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

migrations = Migrate(app,db)
db.init_app(app)

#routes
api.add_resource(User, '/users', '/users/<int:id>')
#api.add_resource(Login, '/login')
api.add_resource(UserCourses, '/userCourse','/userCourse/<int:id>')
api.add_resource(Course, '/course','/course/<int:id>')
api.add_resource(EnrolledEvents,'/enrolledEvent','/enrolledEvent/<int:id>')
api.add_resource(Feedback,'/feedback','/feedback/<int:id>')
api.add_resource(Events,'/event','/event/<int:id>')
api.add_resource(ProfileResource, '/profile','/profile/<int:id>')

@app.route('/users', methods=['POST'])
def register():
    user_data = request.get_json()
    #we are not taking the confirm data to our database it was for user to confirm his password so we remove it
    user_data.pop('confirmPassword', None)
    # Hashing the password
    hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
    user_data['password'] = hashed_password

    #its false in the db.model when a user confirms email its set to true
    user_data['verified'] = False
    
    new_user = UserModel(**user_data)

    # Check if email is already taken
    existing_email = UserModel.query.filter_by(email=user_data['email']).first()
    if existing_email:
        return {"message": "Email already taken", "status": "fail"}, 400

    # Check if username is already taken
    existing_username = UserModel.query.filter_by(username=user_data['username']).first()
    if existing_username:
        return {"message": "Username already taken", "status": "fail"}, 400

    try:
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Generate a token for email verification
        token = serializer.dumps(user_data['email'], salt='email-confirm')

        # Send verification email
        msg = Message('Elimika elimika', sender='elimika@gmail.com', recipients=[user_data['email']])
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg.body = f'Click the following link to confirm your email: {confirm_url}'
        mail.send(msg)
        
        flash('Confirmation email sent. Check your inbox!', 'success')
        return {"message": "Confirmation email sent verify your email to login", "status": "success"}, 201
    except:
        return {"message": "Unable to register user:", "status": "fail"}, 500

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        # Update verified field to True
        user = UserModel.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash_message = 'Email confirmed successfully! You can now log in.'
            return jsonify({'message': flash_message}), 200
        else:
            flash_message = 'User not found with this email.'
            return jsonify({'message': flash_message}), 404
    except:
        flash_message = 'The confirmation link is invalid or has expired.'
        return jsonify({'message': flash_message}), 400

# Logging in with username or email
@app.route('/login', methods=['POST'])
def login():
    # Get user credentials from request data
    data = Login.user_parser.parse_args()
    email_or_username = data['usernameOrEmail']
    password = data['password']

    # Check if user exists by email or username
    user = UserModel.query.filter(or_(UserModel.email == email_or_username, UserModel.username == email_or_username)).first()

    if user:
        if user.verified:  # Check if user is verified
            if user.check_password(password):  # Validate password
                # Generate access token and refresh token
                user_json = user.to_json()
                access_token = create_access_token(identity=user_json['id'])
                refresh_token = create_refresh_token(identity=user_json['id'])
                return {
                    "message": "Login successful",
                    "status": "success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user_json
                }, 200
            else:
                return {"message": "Invalid email/username or password", "status": "fail"}, 403
        else:
            return {"message": "Email not verified. Please verify your email first.", "status": "fail"}, 403
    else:
        return {"message": "Invalid email/username or password", "status": "fail"}, 404


#Function to send a booking confirmation email 
def send_booking_confirmation_email(email,event_title):
    msg = Message('Event Booking Confirmation', sender='elimika@gmail.com', recipients=[email])
    msg.body = f'You have successfully booked for the event: {event_title} , Hope you enjoy the Event!'
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
    #username = user.username
    event_title = event.title
    if email and event_title:
        send_booking_confirmation_email(email,event_title )
    else:
        return {"message": "Email not found"}, 404
        
    return {"message": "Event booked successfully"}, 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)