import sqlite3
from flask import Flask,g,render_template,request,url_for,redirect,escape
from markupsafe import Markup

#create a new Flask application
app = Flask(__name__)
#app.config['TEMPLATES_AUTO_RELOAD']=True


'''Database functionality should all eventually go into a db.py file---'''

#function connecting to the database
def get_db_con():
    if 'db' not in g: #create database connection if not in application context
                      #store in g object, this avoids passing the connection as
                      #argument between functions in the same context
        g.db=sqlite3.connect('cities.db')
        g.db.row_factory=sqlite3.Row #is that the same as a cursor?
    return g.db

#what happens when request/app context is done
@app.teardown_appcontext
def close_db(e): #why does this function need an argument?
    db=g.pop('db',None) #remove from g object if present
    if db is not None:
        db.close() #close the database connection

#function querying the database on all materials in the city's list
def matlist_db(city:str):
    con=get_db_con()
    sql='''SELECT material FROM waste_table WHERE city=?'''
    args=(city,)
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
    return result

'''------------------------------------------------------'''

'''This is the frontend part ----------------------------'''
#index page functionality
@app.route('/', methods=['GET'])
def index():
    #note: Calgary has no entries in the db yet
    return render_template('home.html', cities=["Boston","Calgary","Toronto"])

#handle selections on index page
@app.route('/handle_data', methods=['POST'])
def handle_data():
    city = request.form['city']
    action= request.form['action']
    if action=="wizard":
        return redirect(url_for('search', city=city))
    else:
        return render_template('questions.html', city=city)

#handle redirect to wizard and wizard inputs for city
@app.route('/search/<city>', methods=['POST','GET']) #GET method allows direct navigation to here
def search(city):
   citylist=matlist_db(city) #after each request is finished, the db connection is closed
   if request.method=='POST': #form has been submitted
       partial=escape(request.form['search'])#I think flask escapes automatically
       result=query_db(city,partial) #look into SQLalchemy for extensive query functionality
   else:
       result=None
   return render_template('wizard.html', city=city, citylist=citylist, result=result)

app.run(debug=True)
