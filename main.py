from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import math
import hashlib

app = Flask(__name__)
app.secret_key = 'a055b9695803b8412f81833adde61422ed86b4d928ebbd5846b99f8b4f687c78'


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
        m = str(int(m))
        if len(m) == 1:
            m = '0' + m
        s, ms = str(round(remainder, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s
        for i in range(3-len(ms)):
            ms = ms + '0'
        output = f'{int(h)}h {m}m {s}s {ms}ms'
        return output
    elif run_time >= 60:
        m, remainder = divmod(run_time, 60)
        s, ms = str(round(remainder, 3)).split('.')
        m = str(int(m))
        if len(m) == 1:
            m = '0' + m
        s, ms = str(round(remainder, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s
        for i in range(3-len(ms)):
            ms = ms + '0'
        output = f'{m}m {s}s {ms}ms'
        return output
    else:
        s, ms = str(round(run_time, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s
        for i in range(3-len(ms)):
            ms = ms + '0'
        output = f'{s}s {ms}ms'
        return output

def seconds_since_1980_to_date(seconds):
    epoch_1980 = datetime(1980, 1, 1)
    date = epoch_1980 + timedelta(seconds=seconds)
    return date.strftime("%d/%m/%Y")

def check_logged_in():
    if 'username' in session:
        return session['username']
    else:
        return False
    

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        del session['username']
    return render_template('home.html', logged_in=check_logged_in())


@app.route('/leaderboard_fullgame/<category_id>/<int:page>')
def leaderboard_fullgame(category_id, page):
    query = f"""SELECT Run.run_id, Player.name, Player.player_id, Run.time,
    Run.video_link, Run.date_submitted, Platform.name FROM Run 
    JOIN Player ON Run.player_id = Player.player_id 
    JOIN Platform ON Run.platform_id = Platform.platform_id 
    WHERE Fullgame_category_id = '{category_id}' AND Run.verifier_id IS NOT NULL AND Run.obsolete = 0
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

    temp_recent_runs = run_query_select(f"SELECT Player.name, Run.player_id, Run.run_id, Run.time FROM Run JOIN Player ON Player.player_id = Run.player_id WHERE Run.fullgame_category_id = '{category_id}' ORDER BY Run.date_submitted DESC LIMIT 15")
    recent_runs = []
    for i in temp_recent_runs:
        i = list(i)
        i[3] = converttime(i[3])
        recent_runs.append(i)




    return render_template('leaderboard_fullgame.html', 
                           runs=real_runs, categories=categories, 
                           category_id=category_id,
                           page=page, maxpage=maxpage,
                           recent_runs=recent_runs, logged_in=check_logged_in())


@app.route('/leaderboard_individual_level/<individual_level_id>/<int:page>')
def individual_level_leaderboard(individual_level_id, page):
    query = f"""SELECT Run.run_id, Player.name, Player.player_id, Run.time,
    Run.video_link, Run.date_submitted, Platform.name FROM Run 
    JOIN Player ON Run.player_id = Player.player_id 
    JOIN Platform ON Run.platform_id = Platform.platform_id 
    WHERE il_id = '{individual_level_id}' AND Run.verifier_id IS NOT NULL AND Run.obsolete = 0
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

    level = run_query_select(f"SELECT Level.name, Level.level_id FROM Individual_level JOIN Level ON Individual_level.level_id = Level.level_id WHERE Individual_level.il_id = '{individual_level_id}'")[0]
    category = run_query_select(f"SELECT IL_category.name, IL_category.il_category_id FROM Individual_level JOIN IL_category ON Individual_level.il_category_id = IL_category.il_category_id WHERE Individual_level.il_id = '{individual_level_id}'")[0]

    levels_temp = run_query_select(f"SELECT level_id, name FROM Level")
    levels = {}
    for i in levels_temp:
        levels[i[0]] = [i[1], run_query_select(f"SELECT Individual_level.il_id from Individual_level WHERE level_id = '{i[0]}' AND il_category_id = '40ce5c88'")[0][0]]

    categories_temp = run_query_select(f"SELECT IL_category.il_category_id, IL_category.name FROM Individual_level JOIN IL_category ON Individual_level.il_category_id = IL_category.il_category_id WHERE level_id = '{level[1]}'")
    categories = {}
    for i in categories_temp:
        categories[i[0]] = [i[1], run_query_select(f"SELECT Individual_level.il_id from Individual_level WHERE level_id = '{level[1]}' AND il_category_id = '{i[0]}'")[0][0]]

    return render_template('leaderboard_individual_level.html', runs = real_runs, categories=categories, levels=levels, level=level, category=category, maxpage=maxpage, page=page, individual_level_id=individual_level_id, logged_in=check_logged_in())



@app.route('/login')
def login():
    if session['login_failed']:
        failed=session['login_failed']  
        session['login_failed'] = False
        return render_template('login.html', failed=failed)
    else:
        return render_template('login.html', failed=False)


@app.route('/check_valid_login', methods = ['GET', 'POST'])
def check_valid_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        given_hash = password.encode()
        given_hash = hashlib.sha256(given_hash).hexdigest()
        user_hash = run_query_select(f"SELECT Player.hash FROM Player WHERE Player.name = '{username}'")
        if not user_hash:
            session['login_failed'] = True
            return redirect(url_for('login'))
        user_hash = user_hash[0][0]
        if user_hash == given_hash:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            session['login_failed'] = True
            return redirect(url_for('login'))
        











@app.route('/view_fullgame_run/<run_id>')
def view_fullgame_run(run_id):
    query = f"SELECT Run.run_id, Run.time, Run.date_submitted, Run.fullgame_category_id, Run.video_link, Run.player_id, Player.name, Fullgame_category.name, Verifier.player_id, Platform.name FROM Run JOIN Verifier ON Run.verifier_id = Verifier.verifier_id JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id JOIN Fullgame_category on Run.fullgame_category_id = Fullgame_category.fullgame_category_id WHERE Run.run_id = '{run_id}'"
    run1 = run_query_select(query)
    run_temp = run1[0]

    run = []
    for i in run_temp:
        run.append(i)

    run[1] = converttime(run[1])
    video_url = run[4]
    run[2] = seconds_since_1980_to_date(run[2])
    print(run)
    if "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        embed_url = video_url  

    run[4] = embed_url
    allruns = run_query_select(f"SELECT Run.run_id FROM Run WHERE Run.fullgame_category_id = '{run[3]}' ORDER BY Run.time")
    for index, runinallruns in enumerate(allruns):
        if runinallruns[0] == run[0]:
            if (str(index)[-2:] == '10') or (str(index)[-2:] == '11') or (str(index)[-2:] == '12'):
                run.append(f'{index+1}th')
                break
            elif str(index)[-1] == '0':
                run.append(f'{index+1}st')
                break
            elif str(index)[-1] == '1':
                run.append(f'{index+1}nd')
                break
            elif str(index)[-1] == '2':
                run.append(f'{index+1}rd')
                break
            else:
                run.append(f'{index+1}th')
                break


    return render_template('view_fullgame_run.html', run=run)




if __name__ == '__main__':
    app.run(debug=True)
