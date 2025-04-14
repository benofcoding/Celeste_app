import srcomapi, srcomapi.datatypes as dt
import sqlite3
import random
api = srcomapi.SpeedrunCom(); api.debug = 1


def generate_id():
    id = ''
    for i in range(8):
        id += random.choices('0123456789abcdef', k=1)[0]
    return id


print(generate_id())

game = api.search(srcomapi.datatypes.Game, {"name": "Celeste"})[0]
game_id = game.id

def run_query(query):
    try:
        conn = sqlite3.connect('DB NAME')
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return rows
    except sqlite3.Error as e:
        return None

def get_levels():

    levels = api.get(f'games/{game_id}/levels')
    level = []

    for i in levels:
        level.append(i['name'])