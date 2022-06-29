import sqlite3
from flask import Flask,render_template,request,url_for,redirect,escape
from markupsafe import Markup

#create a new Flask application
app = Flask(__name__)
#app.config['TEMPLATES_AUTO_RELOAD']=True


'''Database functionality should all eventually go into a db.py file---'''

#function connecting to the database
def get_db_con():
    con=sqlite3.connect('cities.db')
    con.row_factory=sqlite3.Row #is that the same as a cursor?
    return con

#function querying the database on all materials in the city's list
def matlist_db(con, city:str):
    sql='''SELECT material FROM waste_table WHERE city=?'''
    args=(city,)
    return con.execute(sql,args).fetchall()

#function querying the database on city data and a partial string
def query_db(con, city: str, partial:str):
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
@app.route('/search/<city>', methods=['POST','GET']) #add GET method allows direct navigation to here
def search(city):
   con=get_db_con() #when does this close? can the connection be reused, look into flask g object
   citylist=matlist_db(con,city)
   if request.method=='POST': #form has been submitted
       partial=escape(request.form['search'])#I think flask escapes automatically
       result=query_db(con,city,partial)
   else:
       result=None
   return render_template('wizard.html', city=city, citylist=citylist, result=result)

app.run(debug=True)
