import srcomapi, srcomapi.datatypes as dt
import sqlite3
import random
api = srcomapi.SpeedrunCom(); api.debug = 1


def generate_id():
    id = ''
    for i in range(8):
        id += random.choices('0123456789abcdef', k=1)[0]
    return id
def run_query_select(query):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return rows
def run_query_insert(query, values):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
def run_query_update(query):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()


game = api.search(srcomapi.datatypes.Game, {"name": "Celeste"})[0]
game_id = game.id



def insert_levels():


    levels = api.get(f'games/{game_id}/levels')
    level = []

    for i in levels:
        level = i['name']
        ids = run_query_select('SELECT Level.level_id FROM Level')
        id = generate_id()
        while id in ids:
            id = generate_id()
        run_query_insert('INSERT INTO Level (level_id, name) VALUES (?, ?)', (id, level))



def id_il_categories():
    categories_temp = run_query_select('SELECT Il_category.name FROM Il_category')
    categories = []

    for i in categories_temp:
        categories.append(i[0])
    print(categories)


    for i in categories:
        id = generate_id()
        ids_temp = run_query_select('SELECT Il_category.il_category_id FROM Il_category')
        ids = []
        for j in ids_temp:
            ids.append(j[0])
        while id in ids:
            id = generate_id()
        query = f"UPDATE Il_category SET il_category_id = '{id}' WHERE Il_category.name = '{i}'"
        print(query)
        run_query_update(query)

id_il_categories()