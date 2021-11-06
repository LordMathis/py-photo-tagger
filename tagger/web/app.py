from flask import Flask

from flask import Flask
from flask_restx import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
api = Api(app)


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


upload_parser = reqparse.RequestParser()
upload_parser.add_argument('image', location='files',
                           type=FileStorage, required=True)


@api.route('/upload')
@api.expect(upload_parser)
class ImageUpload(Resource):
    def post(self):
        args = upload_parser.parse_args()
        image_file = args['image']
        data = image_file.read()

        return {"type": str(type(data)), "size": len(data)}
