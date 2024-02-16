from models import UserModel,db
from flask_restful import Resource, fields, marshal, reqparse
from sqlalchemy import or_
from flask_bcrypt import generate_password_hash

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
# from Resources.courseEnrolment import userCourse_fields
from Resources.courses import resource_fields

user_fields = {
    "id" : fields.Integer,
    "username" : fields.String,
    "email" : fields.String,
    "password" : fields.String,
    "role":fields.String,
    "courses": fields.Nested(resource_fields)
}

class User(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('username', required=True, type=str, help="Enter the username")
    user_parser.add_argument('email', required=True, type=str,help="Enter the email")
    user_parser.add_argument('role', required=True, type=str,help="Enter the role")
    user_parser.add_argument('password', required=True, type = str, help="Enter the password")

    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=current_user_id).first()
        if not user:
            return {"message": "user not found"}
        return marshal(user, user_fields)
    
    def post(self):
        user_data = User.user_parser.parse_args()

        user_data['password'] = generate_password_hash(user_data['password'])
        
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

             # Refresh the user object after committing to get the updated information
             db.session.refresh(new_user)

             # Convert the user to JSON
             user_json = new_user.to_json()

             # Create access and refresh tokens
             access_token = create_access_token(identity=user_json['id'])
             refresh_token = create_refresh_token(identity=user_json['id'])

             # Return success message and tokens
             return {
                 "message": "Account created successfully",
                 "status": "success",
                 "access_token": access_token,
                 "refresh_token": refresh_token,
                 "user": user_json
                 }, 201

        except:
                 return {"message": "Unable to create user", "status": "fail"}, 500

    #when admin wants to delete a user or a user wants to delete his or her account
    @jwt_required
    def delete(self):
        current_user_id = get_jwt_identity()
        user = UserModel.query.get(current_user_id)
        if user:
            try:
                db.session.delete(user)
                db.session.commit()

                return {"message":"Account deleted successfully"}
            except:
                return {"message":"user unable to be deleted"}
        else:
            return {"message":"user not found"}
       

class Login(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('usernameOrEmail', required=True, type=str, help="Enter the email or username")
    user_parser.add_argument('password', required=True, type=str, help="Enter password")

    def post(self):
        data = Login.user_parser.parse_args()

        user = UserModel.query.filter(or_(UserModel.email == data['usernameOrEmail'], UserModel.username == data['usernameOrEmail'])).first()

        if user:
            checking_password = user.check_password(data['password'])
            if checking_password:
                # don't forget access token and refresh token
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
            return {"message": "Invalid email/username or password", "status": "fail"}, 403