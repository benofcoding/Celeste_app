from flask import Flask, render_template, request
from datetime import datetime, timedelta
import sqlite3
import math



app = Flask(__name__)

def run_query_select(query):

    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return rows
def converttime(run_time):
    if run_time >= 3600:
        h, remainder = divmod(run_time, 3600)
        m, remainder = divmod(round(remainder, 3), 60)
        s, ms = str(round(remainder, 3)).split('.')
        output = f'{int(h)}h {int(m)}m {int(round(float(s), 3))}s {int(round(float(ms), 3))}ms'
        return output
    else:
        m, remainder = divmod(run_time, 60)
        s, ms = str(round(remainder, 3)).split('.')
        output = f'{int(m)}m {int(round(float(s), 3))}s {int(round(float(ms), 3))}ms'
        return output
def seconds_since_1980_to_date(seconds):
    epoch_1980 = datetime(1980, 1, 1)
    date = epoch_1980 + timedelta(seconds=seconds)
    return date.strftime("%d/%m/%Y")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/leaderboard_fullgame/<category_id>/<int:page>')
def leaderboard_fullgame(category_id, page):
    query = f"""SELECT Run.run_id, Player.name, Player.player_id, Run.time,
    Run.video_link, Run.date_submitted, Platform.name FROM Run 
    JOIN Player ON Run.player_id = Player.player_id 
    JOIN Platform ON Run.platform_id = Platform.platform_id 
    WHERE Fullgame_category_id = '{category_id}' AND Run.verifier_id IS NOT NULL 
    ORDER BY Run.time ASC"""
    
    runs = run_query_select(query)


    
    length = len(runs)
    maxpage = math.floor(length/100)
    print(length)

    real_runs = []
    if page != maxpage:
        for i in range(100):
            real_runs.append(runs[page*100 + i])
    else:
        for i in range(int(str(length)[-2:])):
            real_runs.append(runs[page*100 + i])


    for v, i in enumerate(real_runs):
        real_runs[v] = list(i)
        real_runs[v][3] = converttime(i[3])
        real_runs[v].append(seconds_since_1980_to_date(i[5]))

    categories_temp = run_query_select(f"SELECT fullgame_category_id, name FROM Fullgame_category")
    categories = {}
    for i in categories_temp:
        categories[i[0]] = i[1]

    return render_template('leaderboard_fullgame.html', 
                           runs=real_runs, categories=categories, 
                           category_id=category_id,
                           page=page, maxpage=maxpage)










if __name__ == '__main__':
    app.run(debug=True)
