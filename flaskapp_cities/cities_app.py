import sqlite3
from flask import Flask, Response, render_template, request,escape
from markupsafe import Markup

#create a new Flask application
app = Flask(__name__)
#app.config['TEMPLATES_AUTO_RELOAD']=True


'''This should all eventually go into a app_db.py file---'''

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
def query_db(con, city: str, partial:str ):
    #make sure input is sanitized
    sql='''SELECT * FROM waste_table WHERE city=? AND material LIKE ?'''
    args=(city,"%"+partial+"%")#should be safe according to https://bobby-tables.com/python, I think
    answer=con.execute(sql,args).fetchone()
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

#handle inputs on index page
@app.route('/handle_data', methods=['POST'])
def handle_data():
    city = request.form['city']
    action= request.form['action']
    if action=="wizard":
        con=get_db_con() #when does this close? can the connection be reused
        citylist=matlist_db(con,city)
        return render_template('wizard.html', city=city, citylist=citylist, result=None)
    else:
        return render_template('questions.html', city=city)

#@app.route('/_autocomplete', methods=['GET'])
#def autocomplete():
#    materials=
#    return Response(json.dumps(materials), mimetype='application/json')

#handle wizard inputs
@app.route('/search/<city>', methods=['POST']) #add GET method to allow direct access via browser
def search(city):
   con=get_db_con() #when does this close? can the connection be reused, look into flask g object
   citylist=matlist_db(con,city)
   result=query_db(con,city,escape(request.form['search']))
   return render_template('wizard.html', city=city, citylist=citylist, result=result)

app.run(debug=True)
