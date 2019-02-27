from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy.sql import text
from sqlalchemy import create_engine, func, update, MetaData
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
        parser.add_argument('Survived', required=False)
        parser.add_argument('Pclass', required=False)
        parser.add_argument('Name', required=False)
        parser.add_argument('Sex', required=False)
        parser.add_argument('Age', required=False)
        parser.add_argument('Siblings/Spouses Aboard', required=False)
        parser.add_argument('Parents/Children Aboard', required=False)
        parser.add_argument('Fare', required=False)

        # Parse the arguments into an object
        args = parser.parse_args()
        
        conn = e.connect()
        # find value of new id
        new_id = len(conn.execute("select * from titanic").cursor.fetchall()) + 1
        args.update({'id':new_id})
        try:
            conn.execute("insert into titanic (id, Survived, Pclass, Name, Sex, Age, [Siblings/Spouses Aboard], [Parents/Children Aboard], Fare) values (?,?,?,?,?,?,?,?,?)",  ((args['id']), (args['Survived']), (args['Pclass']), (args['Name']), (args['Sex']), (args['Age']), (args['Siblings/Spouses Aboard']), (args['Parents/Children Aboard']), (args['Fare'])))
            #conn.execute("insert into titanic (id, Survived, Pclass, Name, Sex, Age, Siblings/Spouses Aboard, Parents/Children Aboard, Fare) values (%d, %s, %d, %s, %s, %f, %d, %d, %f)"  % (new_id, args['Survived'], args['Pclass'], args['Name'], args['Sex'], args['Age'], args['Siblings/Spouses Aboard'], args['Parents/Children Aboard'], args['Fare']))
            #conn.execute(text("""INSERT INTO TITANIC(id, Survived, Pclass, Name, Sex, Age, [Siblings/Spouses Aboard], [Parents/Children Aboard], Fare) VALUES(:id, :Survived, :Pclass, :Name, :Sex, :Age, :[Siblings/Spouses Aboard], :[Parents/Children Aboard], :Fare""") **args)
            #conn.execute(text("""INSERT INTO TITANIC DEFAULT VALUES"""))

        except:
            return args
            #return {'message': 'Failed to input data'}, 502
        # cur[args['identifier']] = args
        #conn.commit()

        return {'message': 'Person Added', 'data': args}, 201


class People_Id(Resource):
    def get(self, identifier):

        conn = e.connect()
        results = conn.execute("select * from titanic where id='%s'" % identifier)
        person_dict = {}
        for key, value in zip(results.keys(), results.cursor.fetchall()[0]):
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
    
            # If id does not exist in the database, return a 404 error.
	    if len(person_dict) == 0:
	        return {'message': 'Person not Found', 'data': person_dict}, 404
	    else:
	        # Delete person with id = identifier
	        conn.execute("delete from titanic where id='%s'" % identifier)
	        return {'message': 'Success', 'Deleted': person_dict}
    
    
    def put(self, identifier):
    	parser = reqparse.RequestParser()
	parser.add_argument('Survived', required=False)
	parser.add_argument('Pclass', required=False)
	parser.add_argument('Name', required=False)
	parser.add_argument('Sex', required=False)
	parser.add_argument('Age', required=False)
	parser.add_argument('Siblings/Spouses Aboard', required=False)
	parser.add_argument('Parents/Children Aboard', required=False)
	parser.add_argument('Fare', required=False)

        # Pass the arguments into an object
	args = parser.parse_args()

        # Check if identifier is a valid id number
        conn = e.connect()
        is_identifier_valid = False
        for ID in conn.execute("select id from titanic").cursor.fetchall():
            if ID == identifier:
                is_identifier_valid = True
        #if not is_identifier_valid:
        #    return {'message': 'ID is not valid'}, 400

        # Check if any fields other than id have been sent via put request
        if len(args) == 0:
            return {'message': 'No fields to update'}, 400
        else:
            stmt = ''
            d = {}
            for key, value in args.iteritems():
                if value == None:
                    break
                else:
                    stmt += '[' + key + '] = ' + str(value) + ', '
            stmt.rstrip(', ') 
            meta = MetaData()
            meta.reflect(bind=e)
            conn = e.connect()

            titanic_table = meta.tables['titanic']
            #update_stmt = titanic_table.update().\
            #        where(titanic_table.c.id == identifier).\
            #        values([{key:value} for key, value in args.iterkeys(), args.itervalues()])
	    #conn.execute("update titanic set " + stmt + " where id=%d" % identifier)
            #conn.commit()
            conn.execute(update_stmt)
	    return {'message': 'Person Updated', 'data': stmt}, 201

api.add_resource(People_Id, "/people/<int:identifier>")
api.add_resource(People_Meta, "/people")

if __name__ == "__main__":
    app.run()
