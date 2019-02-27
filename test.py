from flask import Flask, request
from flask_restful import Resource, Api, reqparse
#from flask.views import MethodView
from sqlalchemy import create_engine
import json

# Create a engine for connecting to SQLite3.
# Assuming titanic.db is in your app root folder

e = create_engine("sqlite:///titanic.db")

def get():
    # Connect to databse
    conn = e.connect()
    # Perform query and return JSON data
    #query = conn.execute("select * from titanic")
    people_list = []
    #for row in query.cursor.fetchall():
    #    person_dict = {}
    #    for key, value in zip(query.keys(), row):
    #        person_dict.update({key: value})    
    #    people_list.append(person_dict)

    #return {'message':'success', 'data':people_list},200
    return conn.execute("select id from titanic").cursor.fetchall()


def post():
    parser = reqparse.RequestParser()
    parser.add_argument('Survived', required=True)
    parser.add_argument('Pclass', required=True)
    parser.add_argument('Name', required=True)
    parser.add_argument('Sex', required=True)
    parser.add_argument('Age', required=True)
    parser.add_argument('Siblings/Spouses Aboard', required=True)
    parser.add_argument('Parents/Children Aboard', required=True)
    parser.add_argument('Fare', required=True)

    #  Parse the arguments into an object
    args = parser.parse_args()

    conn = e.connect()
    conn.execute("insert into titanic (Survived, Pclass, Name, Sex, Age, Siblings/Spouses Aboard, Parents/Children Aboard, Fare) values (%s, %s, %s, %s, %s, %s, %s, %s)"  % (args['Survived'], args['Pclass'], args['Name'], args['Sex'], args['Age'], args['Siblings/Spouses Aboard'], args['Parents/Children Aboard'], args['Fare']))
    # cur[args['identifier']] = args
    #conn.commit()
    
    print(args)
    #return {'message': 'Person Added', 'data': args}, 201


def put(identifier):
    d = {}
    d.update({'Survived':'True'})
    d.update({'Pclass':'1'})
    d.update({'Name':'John John'})
    d.update({'Sex':'Male'})
    d.update({'Age':'23'})
    d.update({'Siblings/Spouses Aboard':'2'})
    d.update({'Parents/Children Aboard':'1'})
    d.update({'Fare':'2.99'})

    # Parse the arguments into an object

    # Check if any fields other than id have been sent via put request
    if len(d) == 0:
        return {'message': 'No fields to update'}, 400
    #elif conn.execute("select id from titanic").cursor.fetchall()
    else:
        stmt = ''
        for key, value in d.iteritems():
            stmt += "[" + key + "] = " + str(value) + ", "
        stmt.rstrip(', ')
        #conn = e.connect()
        #conn.execute("update titanic set " + stmt .rstrip(', ') + " where id=%d" % identifier)
        print("update titanic set " + stmt  + " where id='%s'" % identifier)
        return {'message': 'Person Updated', 'data': d}, 201
