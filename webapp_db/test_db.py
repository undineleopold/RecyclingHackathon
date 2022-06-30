#test db.py functionality

from db import *

close_db()

get_db_con()

cities=['Smallville', 'Tinytown', 'Metropolis', 'Paris']

print('We try to retrieve material lists for the following cities in order: ',cities)
for city in cities:
    print('materials in list for ', city)
    for material in matlist_db(city):
        print(material[0])
print('done')

city='Smallville'
small_list=matlist_db(city)
print('Recycling in Smallville: ')
for material in small_list:
    print(material[0], ' is: ')
    result=query_db(city,material[0])
    print (result['category']+': '+result['material'])
    print ('instructions: ', result['instructions'])
