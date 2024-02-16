from flask_restful import Resource ,fields ,marshal_with,reqparse ,marshal
from flask_jwt_extended import jwt_required , get_jwt_identity
from models import FeedbackModel ,db

Feedback_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'comment': fields.String,
    'likes': fields.Integer,
    'dislikes': fields.Integer,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
}

class Feedback(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', required=True, help="user_id is required!")
    parser.add_argument('comment', required=False, )
    parser.add_argument('likes', required= False )
    parser.add_argument('dislikes', required= False)
    

    @marshal_with(Feedback_fields)
    def get(self, id=None):
    
        if id:
            feedback = FeedbackModel.query.filter_by(id = id).first()
            return feedback
        else:
            feedbacks = FeedbackModel.query.all()

            return feedbacks
        

    #@jwt_required()
    def post(self):
      data = Feedback.parser.parse_args() 

      feedback= FeedbackModel(**data)

      try:
          db.session.add(feedback)
          db.session.commit()
          return {'message':'successfully added your feedback'},201
      except Exception as e:
                print(f"An error occurred: {e}")
                return {"message":"User already has a feedback with this user_id"},400

      
 
    
    #@jwt_required()
    def patch(self,id):
        data = FeedbackModel.Feedback_parser.parse_args()
        Feedback = FeedbackModel.query.get(id)

        if Feedback:
            for key,value in data.items():
                setattr(Feedback,key,value)
            try:
                db.session.commit()

                return {"message":"Feedback updated successfully"}
            except:
                return {"message":"Feedback unable to be updated"}
            
        else:
            return {"message":"Feedback not found"}
        

    #@jwt_required()
    def delete(self,id):
        Feedback = FeedbackModel.query.filter_by(id = id).first()
        if Feedback:
            try:
                db.session.delete(Feedback)
                db.session.commit()

                return {"message":"Feedback deleted"}
            except:
                return {"message":"Feedback unable to be deleted"}
        else:
            return {"message":"Feedback not found"}

