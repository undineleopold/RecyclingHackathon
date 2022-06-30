import sqlite3
import json
from markupsafe import Markup

'''commenting out functionality depending on Python flask'''
#function connecting to the database
#def get_db_con():
#    if 'db' not in g: #create database connection if not in application context
#                      #store in g object, this avoids passing the connection as
#                      #argument between functions in the same context
#        g.db=sqlite3.connect('cities.db')
#        g.db.row_factory=sqlite3.Row #tells the connection to return rows that
#                                     #behave like dicts
#    return g.db

##what happens when request/app context is done
#@app.teardown_appcontext
#def close_db(e): #why does this function need an argument?
#    db=g.pop('db',None) #remove from g object if present
#    if db is not None:
#        db.close() #close the database connection
###############################################################

con=None

def get_db_con():
    global con
    if con is None:
        print('opening db connection')
        con=sqlite3.connect('demo.db')
        con.row_factory=sqlite3.Row
    return con

def close_db():
    global con
    if con is not None:
        print('closing db connection')
        con.close()
        con=None
    print(con)
    

#function querying the database on all materials in the city's list
def matlist_db(city:str):
    con=get_db_con()
    sql='''SELECT material FROM waste_table WHERE city=?'''
    args=(city,)
    #note: when using flask jsonify, it returns a Response object instead
    #with content-type header 'application/json' which may be more useful
    #for the frontend?
    #return json.dumps([tuple(row) for row in con.execute(sql,args).fetchall()])
    return con.execute(sql,args).fetchall()

#function querying the database on city data and a partial string
def query_db(city: str, partial:str):
    con=get_db_con() #typically, we call matlist_db() first, so the connection
                     #is already open
    #partial should be escaped already
    if partial=='': #make sure there is at least one character
        answer=None
    else:
        if partial[-1]==u"\u2063": #user selected from suggestions with invisible separator
            #exact match (case insensitive) after removing invisible character
            sql='''SELECT * FROM waste_table WHERE city=? AND material LIKE ?'''
            args=(city, partial[:-1])#should be safe according to https://bobby-tables.com/python, I think
        else:
            #substring matching
            sql='''SELECT * FROM waste_table WHERE city=? AND material LIKE ?'''
            args=(city,"%"+partial+"%")
        answer=con.execute(sql,args).fetchone()#return just the first match
    if answer is not None:
        result={'material':answer['material'], 'category':answer['category'], 'instructions':Markup(answer['instructions']).unescape()}
    else:
        result=None
    #return json.dumps(result)
    return result
