#!/usr/bin/python

from sqlalchemy import create_engine
import json

e = create_engine("sqlite:///titanic.db")
conn = e.connect()
results = conn.execute("select * from titanic")
l = []
for row in results.cursor.fetchall():
    d ={}
    for key, value in zip(results.keys(), row):
	    d.update({key: value})
    l.append(d)

print(json.dumps(l))
