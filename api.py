from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from typing import Any
import uuid

# Create a engine for connecting to SQLite3.
# Assuming titanic.db is in your app root folder

e = create_engine("sqlite:///titanic.db")

app = Flask(__name__)
api = Api(app)


class People_Meta(Resource):
    def get(self) -> "list[dict[str, str]]":
        # Connect to databse
        conn = e.connect()
        # Perform query and return list of JSON objects (dictionaries)
        query = conn.execute(text("select * from titanic"))

        # for row in query.cursor.fetchall():
        #     person_dict = {}
        #     for key, value in zip(query.keys(), row):
        #         person_dict.update({key: value})
        #     people_list.append(person_dict)
        
        people_list = [ 
            {key: value for key, value in zip(query.keys(), row)}
                for row in query.cursor.fetchall()
        ]

        conn.close()

        return people_list


    def post(self) -> "tuple[dict[str,Any], int]":
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
            conn.execute(text("insert into titanic (id, survived, p_class, name, sex, age, siblings_or_spouses_aboard, parents_or_children_aboard, fare) \
                              values (:id, :survived, :p_class, :name, :sex, :age, :siblings_or_spouses_aboard, :parents_or_children_aboard, :fare)"),  
                       [{"id": (args['id']), "survived": (args['survived']), "p_class": (args['p_class']), "name": (args['name']), "sex": (args['sex']), "age": (args['age']), "siblings_or_spouses_aboard": (args['siblings_or_spouses_aboard']), "parents_or_children_aboard": (args['parents_or_children_aboard']), "fare": (args['fare'])}],
            )
            conn.commit()
            
            return {'message': 'data added', 'data': args}, 201
        except:
            return {'message': 'failed to input data', 'data': args}, 502
        finally:
            conn.close()


class People_Id(Resource):
    def get(self, identifier) -> "tuple[dict[str, Any], int]":

        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        # person_dict = {}
        # for row in result.cursor.fetchall():
        #     for key, value in zip(result.keys(), row):
        #         person_dict.update({key: value})

        person_dict = {
            key: value 
            for row in result.cursor.fetchall()
                for key, value in zip(result.keys(), row)
        }

        conn.close()

        if person_dict == {}:   # If the are no records with id = identifier, then exit with 404. Could have used 'if len(person_dict) > 0' instead
            return {'message': 'id not found', 'invalid id': identifier}, 404 #####
        
        return person_dict, 200
    

    def delete(self, identifier) -> "tuple[dict[str, Any], int]":
        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        # person_dict = {}
        # for row in result.cursor.fetchall():
        #     for key, value in zip(result.keys(), row):
        #         person_dict.update({key: value})

        person_dict = {
            key: value 
            for row in result.cursor.fetchall()
                for key, value in zip(result.keys(), row)
        }

        if person_dict == {}: # If the are no records with id = identifier, close connection then exit with 404
            conn.close()
            return {'message': 'id not found', 'invalid id': identifier}, 404 #####
    
        # Delete person with id = identifier
        conn.execute(text("delete from titanic where id = :identifier"), {"identifier": identifier})
        conn.commit()
        conn.close()

        return {'message': 'Success', 'deleted': [person_dict]}, 200
    
    
    def put(self, identifier) -> "tuple[dict[str, Any], int]":
        parser = reqparse.RequestParser()
        parser.add_argument('survived', required=False, location='args')
        parser.add_argument('p_class', required=False, location='args')
        parser.add_argument('name', required=False, location='args')
        parser.add_argument('sex', required=False, location='args')
        parser.add_argument('age', required=False, location='args')
        parser.add_argument('siblings_or_spouses_aboard', required=False, location='args')
        parser.add_argument('parents_or_children_aboard', required=False, location='args')
        parser.add_argument('fare', required=False, location='args')
        parser.add_argument('value', required=False, location='args')

        # Pass the arguments into an object
        args = parser.parse_args()

        # determine if the request came with at least one of the designated arguments only
        # i.e. check if any fields have been designated for an update
        if len(request.args) == 0 or False in [key in args.keys() for key in request.args.keys()]:
            return [{'message': 'at least one of the designated parameters only must be sent with this request', 'parameters': request.args}], 404  ####

        conn = e.connect()
        result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        # person_dict = {}
        # for row in result.cursor.fetchall():
        #     for key, value in zip(result.keys(), row):
        #         person_dict.update({key: value})

        person_data = {
            key: value 
            for row in result.cursor.fetchall()
                for key, value in zip(result.keys(), row)
        }

        # if person_dict is empty, there is no record with id == identifier
        if person_data == {}: 
            conn.close()
            return [{'message': 'id is not valid', 'id': identifier}], 404  ####
        
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

        new_result = conn.execute(text("select * from titanic where id = :identifier"), {"identifier": identifier})

        updated_person_data = {
            key: value 
            for row in new_result.cursor.fetchall()
                for key, value in zip(new_result.keys(), row)
        }
        conn.close()

        return [{'message': 'person updated', 'update statement': stmt, 'old data': person_data, 'updated data': updated_person_data}], 201
    

class People_Any(Resource):
    def get(self) -> "tuple[list[dict[str, Any]], int]":
        parser = reqparse.RequestParser()
        parser.add_argument('survived', required=False, location='args')
        parser.add_argument('p_class', required=False, location='args')
        parser.add_argument('name', required=False, location='args')
        parser.add_argument('sex', required=False, location='args')
        parser.add_argument('age', required=False, location='args')
        parser.add_argument('siblings_or_spouses_aboard', required=False, location='args')
        parser.add_argument('parents_or_children_aboard', required=False, location='args')
        parser.add_argument('fare', required=False, location='args')
        parser.add_argument('operator', required=False, location='args')
        parser.add_argument('value', required=False, location='args')

        # Pass the arguments into an object
        args = parser.parse_args(strict=False) 

        # require the request comes with one of the designated parameters only
        request_arguments = list(request.args.keys())
        if len(request_arguments) == 1 and request_arguments[0] in args.keys():
            v = {key: value for key, value in zip(args.keys(), args.values()) if value != None}

            key, value = v.popitem()
            conn = e.connect()
            result = conn.execute(text(f'select * from titanic where {key} = :value'), {"value": value})

            people_list = [ 
                {key: value for key, value in zip(result.keys(), row)}
                    for row in result.cursor.fetchall()
            ]

            conn.close()

            return people_list, 200
        else:
            return [{'message': 'error! exactly one of the specified parameters must be sent with this request', 'parameters': request_arguments}], 201



api.add_resource(People_Any, "/people_any")
api.add_resource(People_Id, "/people/<string:identifier>")
api.add_resource(People_Meta, "/people")

if __name__ == "__main__":
    app.run(debug=True)
