from models import db, UserEventModel, EventModel
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_restful import Resource,fields, marshal_with, reqparse,marshal


resource_fields = {
    "id": fields.Integer,
    "user_id":fields.Integer,
    "event_id": fields.Integer,
}

class EnrolledEvents(Resource):
    enrolledEvent_parser = reqparse.RequestParser()
    enrolledEvent_parser.add_argument('event_id', required = True,type=int,help="event id is required" )

    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        if current_user_id:
            UserEvent = UserEventModel.query.filter_by(user_id=current_user_id).all()
            return marshal(UserEvent, resource_fields)
        else:
            return {"message":"you have not enrolled for any event"}
        
    @jwt_required()
    def post(self):
      data = EnrolledEvents.enrolledEvent_parser.parse_args()
      current_user_id = get_jwt_identity()
      check_event_existence = EventModel.query.get(data['event_id'])

      if not check_event_existence:
            return {"message": "event not found"}, 404
          
      existing_booking = UserEventModel.query.filter_by(user_id=current_user_id, event_id=data['event_id']).first()

      if existing_booking:
            # User has already booked for this event
            return {"message": "You have already booked for this event"}, 400

      data['user_id'] = current_user_id
      new_event = UserEventModel(**data)

      db.session.add(new_event)
      db.session.commit()
      
      return {"message": "Event booked successfully"}, 201
        


        
