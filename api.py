from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('src', type=str, help='Source of uploaded image')

class CharlieVision(Resource):
    def get(self):
        return {'hello': 'world'}

    def post(self):
        args = parser.parse_args()
        print(args)
        return args["src"], 201

api.add_resource(CharlieVision, '/')

if __name__ == '__main__':
    app.run(debug=True)