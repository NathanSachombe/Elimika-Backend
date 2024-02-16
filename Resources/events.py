from flask_restful import Resource, reqparse, fields, marshal_with
from models import db, EventModel

resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'image': fields.String,
    'capacity': fields.Integer,
    'date': fields.DateTime,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
}

class Events(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True, help="Title is required")
    parser.add_argument('description', required=True, help='Description is required')
    parser.add_argument('image', required=True, help='Image is required')
    parser.add_argument('capacity', required=True, help='Capacity is required')
    parser.add_argument('date', required=False, help='Date is not required')

    # parser = reqparse.RequestParser()
    # parser.add_argument('title', required=False)
    # parser.add_argument('description', required=False)
    # parser.add_argument('image', required=False)
    # parser.add_argument('capacity', required=False)
    # parser.add_argument('date', required=False)

    @marshal_with(resource_fields)
    def get(self, id=None):
        if id:
            event = EventModel.query.filter_by(id=id).first()
            return event
        else:
            events = EventModel.query.all()
            return events

    def post(self):
        data = Events.parser.parse_args()
        event = EventModel(**data)
        try:
            db.session.add(event)
            db.session.commit()
            return {"message": "Event created successfully!"}, 201
        except Exception as e:
            return {"message": 'unable to add event', 'status': 'fail'}

    def delete(self, id):
        try:
            event = EventModel.query.filter_by(id=id).first()

            if event:
                db.session.delete(event)
                db.session.commit()
                return {"message": "Event deleted Successfully", 'status': 'SUCCESS'}
            else:
                return {"message": "No Event Found", 'status': 'FAILED TO DELETE'}
        except Exception as e:
            return {'message': "Failed To Delete The Event"}

    def patch(self, id):
        if id:
            event = EventModel.query.filter_by(id=id).first()

            if event:
                data = Events.update_parser.parse_args()
                for key, value in data.items():
                    if value is not None:
                        setattr(event, key, value)

                try:
                    db.session.commit()
                    return {'Message': 'Update successful', 'Status': 'OK'}, 201
                except Exception as e:
                    print(f'Error occurred while updating the user {e}')
                    db.session.rollback()
                    return {'Message': 'Failed to update the user', 'Status': 'FAILED'}
            else:
                return {'message': 'Event not found', 'Status': 'NOT FOUND'}