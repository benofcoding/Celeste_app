import srcomapi, srcomapi.datatypes as dt
import sqlite3
import random
import time
from datetime import datetime

def time_since_1980_iso(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    ref_date = datetime(1980, 1, 1)
    delta = dt - ref_date
    return delta.total_seconds()


import hashlib
api = srcomapi.SpeedrunCom(); api.debug = 1


fullgame = { 
'7kjpl1gk':'Any%',
'jdz8oprd':'All Red Berries',
'zdn0m372':'True Ending',
'q2517ggd':'All Cassettes',
'q2550mw2':'Bny%',
'xd1718wd':'All Hearts',
'xk9ry6xk':'100%',
'jdrvgy02':'202 Berries',
'z27rpe5d':'All Chapters',
'zd365jyd':'All A-Sides',
'zd36mqyd':'All B-Sides',
'xd1ex5r2':'All C-Sides'}

platforms = {'nzelkr6q': 'PlayStation 4', 'o7e2mx6w': 'Xbox One', '8gej2n93': 'PC', '7m6ylw9p': 'Switch', '4p9z0r6r': 'Xbox One X', 'o064j163': 'Xbox One S', 'o064z1e3': 'Google Stadia', '4p9zjrer': 'PlayStation 5', 'nzelyv9q': 'Xbox Series X', 'o7e2xj9w': 'Xbox Series S'}

levels = {'ywe5zq7w': 'Forsaken City', '69z2m8g9': 'Old Site', 'r9g4k7p9': 'Celestial Resort', 'o9x7mxpd': 'Golden Ridge', '4955vm39': 'Mirror Temple', 'rdq76n29': 'Reflection', '5d746x6d': 'The Summit', 'kwjzo679': 'Core', '5wknr4qw': 'Farewell'}

categorys = {'7dgr144k': 'Clear', 'mkezwq9k': 'Collectibles', '5dw5q7gd': 'B-Side', 'wk67rved': 'C-Side'}



def time_since_1980(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    ref_date = datetime(1980, 1, 1)
    delta = dt - ref_date
    return delta.total_seconds()
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

categories = api.get(f'games/{game_id}/categories')






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














# for j in fullgame:
#     runs = []
#     pagnation = api.get(f'leaderboards/{game_id}/category/{j}')
#     for i in pagnation['runs']:
#         runs.append(i['run'])
#         print(len(runs))

#     for i in runs:
#         verified = True
#         if 'id' in i['players'][0]:
#             user = i['players'][0]['id']
#             if (a := len(run_query_select(f"SELECT name FROM Player WHERE name = '{user}'"))) == 0:
#                 run_query_insert('INSERT INTO Player (player_id, name) VALUES (?, ?)', (generate_id(), user))
#             run_idd = generate_id()
#             verifier_idd = run_query_select(f"SELECT verifier_id FROM Verifier JOIN Player On Verifier.player_id = Player.player_id WHERE Player.name = '{i['status']['examiner']}'")
#             if len(verifier_idd) == 0:
#                 verified = False
#             else:
#                 verifier_idd = verifier_idd[0][0]
#             user_idd = run_query_select(f"SELECT player_id FROM Player WHERE name = '{i['players'][0]['id']}'")[0][0]
#             fullgame_category_idd = run_query_select(f"SELECT fullgame_category_id FROM Fullgame_category WHERE name = '{fullgame[j]}'")[0][0]
#             platform_idd = run_query_select(f"SELECT platform_id FROM Platform WHERE name = '{platforms[i['system']['platform']]}'")[0][0]
#             timee = i['times']['primary_t']
#             datesubmittedd = time_since_1980(i['submitted'])
#             if 'links' in i['videos']:
#                 linkk = i['videos']['links'][0]['uri']
#             else:
#                 linkk = False

#             if linkk:
#                 if verified:
#                     run_query_insert('INSERT INTO Run (run_id, verifier_id, player_id, fullgame_category_id, platform_id, time, date_submitted, video_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (generate_id(), verifier_idd, user_idd, fullgame_category_idd, platform_idd, timee, datesubmittedd, linkk))
#                 else:
#                     run_query_insert('INSERT INTO Run (run_id, player_id, fullgame_category_id, platform_id, time, date_submitted, video_link) VALUES (?, ?, ?, ?, ?, ?, ?)', (generate_id(), user_idd, fullgame_category_idd, platform_idd, timee, datesubmittedd, linkk))









































# for i in run_query_select('SELECT player_id, name FROM Player'):
#     i = i[1]
#     print(i)
#     i = i.encode()
#     i = hashlib.sha256(i).hexdigest()
#     print(i)



































# for i in fullgame:
#     pagnation = api.get(f'leaderboards/{game_id}/category/{i}?embed=players')
#     players = pagnation['players']['data']
#     for i in players:
#         print(i)
#         if i['rel'] == 'guest':
#             continue
#         player = i['id']
#         if len(run_query_select(f'SELECT name FROM Player WHERE name = "{player}"')) == 0:
#             run_query_insert(f'INSERT INTO Player (player_id, name) VALUES (?, ?)', (generate_id(), player))

# for i in levels:
#     for j in categorys:
#         pagnation = api.get(f'leaderboards/{game_id}/level/{i}/{j}?embed=players')
#         players = pagnation['players']['data']
#         for v in players:
#             print(v)
#             if v['rel'] == 'guest':
#                 continue
#             player = v['id']
#             if len(run_query_select(f'SELECT name FROM Player WHERE name = "{player}"')) == 0:
#                 run_query_insert(f'INSERT INTO Player (player_id, name) VALUES (?, ?)', (generate_id(), player))
verified = True
users = run_query_select('SELECT name FROM Player')
count = 1
for j in users:
    print(count)
    print(j[0])
    j = j[0]
    runs = api.get(f'runs?user={j}&game={game_id}')
    print(runs)

    for i in runs:
        verified = True
        if i['level'] == None:
            if i['status']['status'] == 'new':
                verified = False
            else:
                verifier_idd = run_query_select(f"SELECT verifier_id FROM Verifier JOIN Player On Verifier.player_id = Player.player_id WHERE Player.name = '{i['status']['examiner']}'")
            if len(verifier_idd) == 0:
                verified = False
            else:
                verifier_idd = verifier_idd[0][0]
            user_idd = run_query_select(f"SELECT player_id FROM Player WHERE name = '{i['players'][0]['id']}'")[0][0]
            fullgame_category_idd = run_query_select(f"SELECT fullgame_category_id FROM Fullgame_category WHERE name = '{fullgame[i['category']]}'")[0][0]
            platform_idd = run_query_select(f"SELECT platform_id FROM Platform WHERE name = '{platforms[i['system']['platform']]}'")[0][0]
            timee = i['times']['primary_t']
            datesubmittedd = time_since_1980(i['submitted'])
            if 'links' in i['videos']:
                linkk = i['videos']['links'][0]['uri']
            else:
                linkk = False

            if linkk:
                if verified:
                    run_query_insert('INSERT INTO Run (run_id, verifier_id, player_id, fullgame_category_id, platform_id, time, date_submitted, video_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (generate_id(), verifier_idd, user_idd, fullgame_category_idd, platform_idd, timee, datesubmittedd, linkk))
                else:
                    run_query_insert('INSERT INTO Run (run_id, player_id, fullgame_category_id, platform_id, time, date_submitted, video_link) VALUES (?, ?, ?, ?, ?, ?, ?)', (generate_id(), user_idd, fullgame_category_idd, platform_idd, timee, datesubmittedd, linkk))
    count += 1