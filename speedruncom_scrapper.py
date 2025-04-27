import srcomapi, srcomapi.datatypes as dt
import sqlite3
import random
import time
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
def individual_levels():
    category_ids = ['3eadb0eb','f49213bb','061a9cce','75f87514','1a682a2a','40ce5c88']
    level_ids = ['75cdc954','91dbb1b1','f993ae32','2abf90d5','68000667','48762587','12768c3f','b1798bf3']

    for i in category_ids:
        for j in level_ids:
            id = generate_id()
            ids_temp = run_query_select('SELECT Individual_level.il_id FROM Individual_level')
            ids = []
            for k in ids_temp:
                ids.append(k[0])
            while id in ids:
                id = generate_id()
            
            run_query_insert('INSERT INTO Individual_level (il_id, level_id, il_category_id) VALUES (?, ?, ?)', (id, j, i))
def get_categories():

    categories = [i['name'] for i in api.get(f'games/{game_id}/categories')]
    
    for i in categories:
        id = generate_id()
        while id in [i[0] for i in run_query_select('SELECT Fullgame_category.fullgame_category_id FROM Fullgame_category')]:
            id = generate_id()
        
        run_query_insert('INSERT INTO Fullgame_category (fullgame_category_id, name) VALUES (?, ?)', (id, i))
def get_platforms():
    platform_ids = [i for i in api.get(f'games/{game_id}')['platforms']]
    platforms = []

    for i in platform_ids:
        platforms.append(api.get(f'platforms/{i}')['name'])

    for i in platforms:
        id = generate_id()
        while id in [i[0] for i in run_query_select('SELECT Platform.platform_id FROM Platform')]:
            id = generate_id()

        run_query_insert('INSERT INTO Platform (platform_id, name) VALUES (?, ?)', (id, i))
def get_users():
    platform_ids = [i for i in api.get(f'games/{game_id}')['platforms']]
    levels = [i['id'] for i in api.get(f'games/{game_id}/levels')]
    print(levels)
    clear = platform_ids[1]
    del platform_ids[1]
    category_ids = [i['id'] for i in api.get(f'games/{game_id}/categories')]
    print(category_ids)
    print(platform_ids)
    runs = []

    for j in category_ids:
        for i in platform_ids:
            offset = 0
            while (offset < 10000):

                if len(a := api.get(f'runs?game={game_id}&max=200&offset={offset}&orderby=date&direction=desc&platform={i}&category={j}')) == 0:
                    break
                else:
                    runs += a
                offset += 200
                print(len(runs))

            offset = 0
            while (offset < 10000):

                if len(a := api.get(f'runs?game={game_id}&max=200&offset={offset}&orderby=date&direction=asc&platform={i}&category={j}')) == 0:
                    break
                else:
                    runs += a
                offset += 200
                print(len(runs))

    for j in levels:
        for i in platform_ids:
            offset = 0
            while (offset < 10000):
                if len(a := api.get(f'runs?game={game_id}&max=200&offset={offset}&orderby=date&direction=desc&platform={i}&category={clear}&level={j}')) == 0:
                    break
                else:
                    runs += a
                offset += 200
                print(len(runs))

            offset = 0
            while (offset < 10000):
                if len(a := api.get(f'runs?game={game_id}&max=200&offset={offset}&orderby=date&direction=asc&platform={i}&category={clear}&level={j}')) == 0:
                    break
                else:
                    runs += a
                offset += 200
                print(len(runs))




    player_ids = set()
    player_names = set()

    for i in runs:
        if len(i['players']) != 0:
            if i['players'][0]['rel'] == 'guest':
                player_names.add(i['players'][0]['name'])
            else:
                player_ids.add(i['players'][0]['id'])

    print(player_names)
def get_users2():



    with open('ids.txt', 'r') as f:
        input_str = f.read()

    a = [s.strip().strip("'") for s in input_str.split(',')]




    countbig = 85
    count = 0
    player_names = set(['Xylex', 'RA.', 'NinjaPear22', 'Witchs_Hex', 'Podz', 'yarniapple', 'Fabi000n', 'TeDeMos', 'Beeb_', 'Ac_143', 'finn_', 'OkaiOkai', 'Ricka', 'AtomicHex', 'Lifuu', 'Frostysnowman', 'Norikokonut', 'B3traya1', 'shredberg', 'JeddOrAlive'])



    while countbig < 90:
        count = 0
        print(countbig*5)
        player_names = set()
        while count < 100:
            print(count)
            c = api.get(f'users/{a[count+(countbig*100)]}')['names']['international']
            time.sleep(0.61)
            count += 1
            id = generate_id()
            while id in [j[0] for j in run_query_select('SELECT Player.player_id FROM Player')]:
                id = generate_id()
            run_query_insert('INSERT INTO Player (player_id, name) VALUES (?, ?)', (id, c))

        countbig += 1





