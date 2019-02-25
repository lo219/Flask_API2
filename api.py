from flask import Flask, request
from flask_restful import Resource, Api, reqparse
#from flask.views import MethodView
from sqlalchemy import create_engine
import json

# Create a engine for connecting to SQLite3.
# Assuming titanic.db is in your app root folder

e = create_engine("sqlite:///titanic.db")

app = Flask(__name__)
api = Api(app)


class People_Meta(Resource):
    def get(self):
        # Connect to databse
        conn = e.connect()
	# Perform query and return JSON data
	query = conn.execute("select * from titanic")
	people_list = []
	for row in query.cursor.fetchall():
	    person_dict = {}
	    for key, value in zip(query.keys(), row):
	        person_dict.update({key: value})
	    people_list.append(person_dict)
			
	    #return json.dumps(people_list)
	    return {'message':'success', 'data':people_list},200


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Survived', required=True)
        parser.add_argument('Pclass', required=True)
        parser.add_argument('Name', required=True)
        parser.add_argument('Sex', required=True)
        parser.add_argument('Age', required=True)
        parser.add_argument('Siblings/Spouses Aboard', required=True)
        parser.add_argument('Parents/Children Aboard', required=True)
        parser.add_argument('Fare', required=True)

        # Parse the arguments into an object
        args = parser.parse_args()
        
        conn = e.connect()
        conn.execute("insert into titanic (Survived, Pclass, Name, Sex, Age, Siblings/Spouses Aboard, Parents/Children Aboard, Fare) values (%s, %s, %s, %s, %s, %s, %s, %s)"  % (args['Survived'], args['Pclass'], args['Name'], args['Sex'], args['Age'], args['Siblings/Spouses Aboard'], args['Parents/Children Aboard'], args['Fare']))
        # cur[args['identifier']] = args
        #conn.commit()

        return {'message': 'Person Added', 'data': args}, 201


class People_Id(Resource):
    def get(self, identifier):

        conn = e.connect()
        results = conn.execute("select * from titanic where id='%s'" % identifier)
        person_dict = {}
        for key, value in zip(results.keys(), results.cursor.fetchall()):
            person_dict.update({key: value})

        if len(person_dict) > 0:
            return {'message':'success', 'data':person_dict},200
            #return json.dumps(results.keys())
            #return results.keys()


    def delete(self, identifier):
        conn = e.connect()
        results = conn.execute("select * from titanic where id='%s'" % identifier)
        person_dict = {}
        for key, value in zip(results.keys(), results.cursor.fetchall()):
            person_dict.update({key: value})
    
            # If key does not exit in the database, return a 404 error.
	    if len(person_dict) == 0:
	        return {'message': 'Person not Found', 'data': person_dict}, 404
	    else:
	        # Delete person with id = identifier
	        conn.execute("delete from titanic where id='%s'" % identifier)
	        return {'message': 'Success', 'Deleted': person_dict}
    
    
    def put(self):
    	parser = reqparse.RequestParser()
	parser.add_argument('Survived', required=True)
	parser.add_argument('Pclass', required=True)
	parser.add_argument('Name', required=True)
	parser.add_argument('Sex', required=True)
	parser.add_argument('Age', required=True)
	parser.add_argument('Siblings/Spouses Aboard', required=True)
	parser.add_argument('Parents/Children Aboard', required=True)
	parser.add_argument('Fare', required=True)

        # Parse the arguments into an object
	args = parser.parse_args()
	
        conn = e.connect()
	conn.execute("insert into titanic %s values %s" % (args.keys(), args.values()))
	# cur[args['identifier']] = args
	#conn.commit()

        return {'message': 'Person Added', 'data': args}, 201

api.add_resource(People_Id, "/people/<int:identifier>")
api.add_resource(People_Meta, "/people")

if __name__ == "__main__":
    app.run()
