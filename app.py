from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy

# Instanciating the App
app = Flask(__name__)
# Does not list out the warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Entering the URI of the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Instanciating the Api
api = Api(app)
# Instanciating the Database
db = SQLAlchemy(app)


# Model for Video instances persisted in the database
class VideoInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    views = db.Column(db.Integer, nullable=True)
    likes = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "Video(name:{}, views:{}, likes:{})".format(self.name, self.views, self.likes)


# Helper Messages
help_msg_name, help_msg_views, help_msg_likes = \
    "Name of the video required", "Views of the video required", "Likes of the video required"

# Request parser for put(adding video) requests [All the fields are required]
add_parser = reqparse.RequestParser()
add_parser.add_argument("name", type=str, help=help_msg_name, required=True)
add_parser.add_argument("views", type=int, help=help_msg_views, required=True)
add_parser.add_argument("likes", type=int, help=help_msg_likes, required=True)

# Request parser for patch(updating video) requests [All the fields are optional]
update_parser = reqparse.RequestParser()
update_parser.add_argument("name", type=str, help=help_msg_name)
update_parser.add_argument("views", type=int, help=help_msg_views)
update_parser.add_argument("likes", type=int, help=help_msg_likes)

# Response fields required for serialization(converting object instance to json)
# [Used in conjuction with marshal_with]
resposne_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "views": fields.Integer,
    "likes": fields.Integer
}


# Resource Class called when endpoint gets hit
class MediaProcessor(Resource):

    # Get Request [Abort with 404 status if video not present in the database]
    @marshal_with(resposne_fields)
    def get(self, video_id):
        video = VideoInstance.query.filter_by(id=video_id).first()
        if video is None:
            abort(404, message="Not Found : Video with video id {} is not found".format(video_id))
        return video

    # Put Request [Abort with 409 status if video already present in the database]
    @marshal_with(resposne_fields)
    def put(self, video_id):
        video_args = add_parser.parse_args()
        potential_duplicate = VideoInstance.query.filter_by(id=video_id).first()
        if potential_duplicate:
            abort(409, message="Already Exists : Video with video id {} already exists".format(video_id))
        video = VideoInstance(id=video_id, name=video_args["name"], views=video_args["views"],
                              likes=video_args["likes"])
        db.session.add(video)
        db.session.commit()
        return video

    # Patch (Update) Request [Abort with 404 status if video not present in the database]
    @marshal_with(resposne_fields)
    def patch(self, video_id):
        video_args = update_parser.parse_args()
        video = VideoInstance.query.filter_by(id=video_id).first()
        if video is None:
            abort(404, message="Not Found : Video with video id {} is not found".format(video_id))
        for key, value in video_args.items():
            if value is not None:
                setattr(video, key, value)
        db.session.commit()
        return video

    # Delete Request [Abort with 404 status if video not present in the database]
    @marshal_with(resposne_fields)
    def delete(self, video_id):
        video = VideoInstance.query.filter_by(id=video_id).first()
        if video is None:
            abort(404, message="Not Found : Video with video id {} is not found".format(video_id))
        VideoInstance.query.filter_by(id=video_id).delete()
        db.session.commit()
        return video


# Adding the class/resource to the Api
api.add_resource(MediaProcessor, "/media/videos/<int:video_id>")

if __name__ == '__main__':
    app.run(debug=True)
