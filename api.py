from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy.sql import text
from sqlalchemy import create_engine, func, update, MetaData
import json
import uuid

# Create a engine for connecting to SQLite3.
# Assuming titanic.db is in your app root folder

e = create_engine("sqlite:///titanic.db")

app = Flask(__name__)
api = Api(app)


class People_Meta(Resource):
    def get(self):
        people_list = []
        # Connect to databse
        conn = e.connect()
        # Perform query and return JSON data
        query = conn.execute(text("select * from titanic"))

        for row in query.cursor.fetchall():
            person_dict = {}
            for key, value in zip(query.keys(), row):
                person_dict.update({key: value})
            people_list.append(person_dict)
                
        conn.close()

        return people_list


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=False, location='args')
        parser.add_argument('survived', required=True, location='args')
        parser.add_argument('p_class', required=True, location='args')
        parser.add_argument('name', required=True, location='args')
        parser.add_argument('sex', required=True, location='args')
        parser.add_argument('age', required=True, location='args')
        parser.add_argument('siblings_or_spouses_aboard', required=True, location='args')
        parser.add_argument('parents_or_children_aboard', required=True, location='args')
        parser.add_argument('fare', required=True, location='args')

        # Parse the arguments into an object named args
        args = parser.parse_args()

        # generate id and update args object
        new_id = str(uuid.uuid4())
        args.update({'id':new_id})
        
        # Connect to databse
        conn = e.connect()
        
        try:
            conn.execute(text("insert into titanic (id, survived, p_class, name, sex, age, siblings_or_spouses_aboard, parents_or_children_aboard, fare) values (:id, :survived, :p_class, :name, :sex, :age, :siblings_or_spouses_aboard, :parents_or_children_aboard, :fare)"),  
                       [{"id": (args['id']), "survived": (args['survived']), "p_class": (args['p_class']), "name": (args['name']), "sex": (args['sex']), "age": (args['age']), "siblings_or_spouses_aboard": (args['siblings_or_spouses_aboard']), "parents_or_children_aboard": (args['parents_or_children_aboard']), "fare": (args['fare'])}],
            )
            conn.commit()
            
            return {'message': 'data added', 'data': args}, 201
        except:
            return {'message': 'failed to input data', 'data': args}, 502
        finally:
            conn.close()


class People_Id(Resource):
    def get(self, identifier):

        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        person_dict = {}
        for row in result.cursor.fetchall():
            for key, value in zip(result.keys(), row):
                person_dict.update({key: value})
        
        conn.close()

        if person_dict == {}:   # If the are no records with id = identifier, then exit with 404. Could have used 'if len(person_dict) > 0' instead
            return {'message': 'id not found', 'invalid id': identifier}, 404 #####
        
        return person_dict
    

    def delete(self, identifier):
        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        person_dict = {}
        for row in result.cursor.fetchall():
            for key, value in zip(result.keys(), row):
                person_dict.update({key: value})

        if person_dict == {}: # If the are no records with id = identifier, close connection then exit with 404
            conn.close()
            return {'message': 'id not found', 'invalid id': identifier}, 404 #####
    
        # Delete person with id = identifier
        conn.execute(text("delete from titanic where id = :identifier"), {"identifier": identifier})
        conn.commit()
        conn.close()

        return {'message': 'Success', 'deleted': [person_dict]}, 200
    
    
    def put(self, identifier):
        parser = reqparse.RequestParser()
        parser.add_argument('survived', required=False)
        parser.add_argument('p_class', required=False)
        parser.add_argument('name', required=False)
        parser.add_argument('sex', required=False)
        parser.add_argument('age', required=False)
        parser.add_argument('siblings_or_spouses_aboard', required=False)
        parser.add_argument('parents_or_children_aboard', required=False)
        parser.add_argument('fare', required=False)

        # Pass the arguments into an object
        args = parser.parse_args()
        # check if any fields have been designated for an update
        if len(args.values()) == 0:
            return {'message': 'no fields require an update'}, 404  ####

        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        person_dict = {}
        for row in result.cursor.fetchall():
            for key, value in zip(result.keys(), row):
                person_dict.update({key: value})

        # if person_dict is empty, there is no record with id == identifier
        if person_dict == {}: 
            conn.close()
            return {'message': 'id is not valid', 'invalid id': identifier}, 404  ####
        
        # construct query statement 'stmt'
        stmt = f'UPDATE titanic SET '

        for key, value in args.items():
            if value == None:
                pass
            else:
                stmt += f'{key} = "{value}", '
    
        stmt = stmt.rstrip(' ,')  # remove trailing ', ' from stmt using stmt.rstrip(' ,') 
        stmt += f' WHERE id = "{identifier}"'

        # execute query
        conn.execute(text(stmt))
        conn.commit()
        conn.close()

        return {'message': 'person updated', 'data': stmt}, 201


api.add_resource(People_Id, "/people/<string:identifier>")
api.add_resource(People_Meta, "/people")

if __name__ == "__main__":
    app.run(debug=True)
