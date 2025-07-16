from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import sqlite3
import math
import random
import hashlib
import heapq


app = Flask(__name__)
app.secret_key = 'a055b9695803b8412f81833adde61422ed86b4d928ebbd5846b99f8b4f687c78'
start_date = datetime.date(1980, 1, 1)

def generate_id():
    id = ''
    for i in range(8):
        id += random.choices('0123456789abcdef', k=1)[0]
    return id

def get_run_rank(run_id, fullgame, obsolete=False):

    if fullgame:
        category_id = run_query_select(f"SELECT Run.fullgame_category_id FROM Run WHERE Run.run_id = '{run_id}'")
        if obsolete:
            allruns = run_query_select(f"SELECT Run.run_id FROM Run WHERE Run.fullgame_category_id = '{category_id[0][0]}' AND obsolete = 0 ORDER BY Run.time")
        elif obsolete == False:
            allruns = run_query_select(f"SELECT Run.run_id FROM Run WHERE Run.fullgame_category_id = '{category_id[0][0]}' ORDER BY Run.time")
    else:
        category_id = run_query_select(f"SELECT Run.il_id FROM Run WHERE Run.run_id = '{run_id}'")
        if obsolete:
            allruns = run_query_select(f"SELECT Run.run_id FROM Run WHERE Run.il_id = '{category_id[0][0]}' AND obsolete = 0 ORDER BY Run.time")
        elif obsolete == False:
            allruns = run_query_select(f"SELECT Run.run_id FROM Run WHERE Run.il_id = '{category_id[0][0]}' ORDER BY Run.time")

    for index, runinallruns in enumerate(allruns):
        if runinallruns[0] == run_id:
            if (str(index)[-2:] == '10') or (str(index)[-2:] == '11') or (str(index)[-2:] == '12'):
                return f'{index+1}th'
            elif str(index)[-1] == '0':
                return f'{index+1}st'

            elif str(index)[-1] == '1':
                return f'{index+1}nd'

            elif str(index)[-1] == '2':
                return f'{index+1}rd'
            else:
                return f'{index+1}th'
    
    return False

def run_query_select(query):

    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()
    
    cursor.execute(query)
    temp_rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    rows = []

    for i in temp_rows:
        rows.append(list(i))
    return rows

def run_query_insert(query, values):
    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

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

def convert_time_to_seconds(time):
    time = str(time)
    colon_count = 0
    for i in time:
        if i == ':':
            colon_count += 1
    if colon_count == 0:
        return time
    if colon_count == 1:
        minutes, seconds = time.split(':')
        return round(int(minutes)*60 + float(seconds), 3)
    if colon_count == 2:
        hours, minutes, seconds = time.split(':')
        return round(int(hours)*3600 + int(minutes)*60 + float(seconds), 3)
    return False

def seconds_since_1980_to_date(seconds):
    epoch_1980 = datetime.date(1980, 1, 1)
    date = epoch_1980 + datetime.timedelta(seconds=seconds)
    return date.strftime("%d/%m/%Y")

def date_to_seconds_since_1980(date):
    from datetime import datetime

    target_date = datetime(2025, 5, 23)

    base_date = datetime(1980, 1, 1)

    seconds_since_1980 = int((target_date - base_date).total_seconds())

    print(seconds_since_1980)

def check_logged_in():
    if 'username' in session:
        return session['username']
    else:
        return False
    
def check_verifier():
    if not 'username' in session:
        return False
    print(session['username'])
    if len(run_query_select(f"SELECT verifier.verifier_id FROM Verifier JOIN Player on Player.player_id = Verifier.player_id WHERE Player.player_id = '{session['username'][1]}'")) != 0:
        return True

def run_query_update(query):
    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()







@app.route('/', methods = ['GET', 'POST'])
def home():
    if 'signup_password_falied' in session:
        del session['signup_passord_falied']
    if 'signup_username_failed' in session:
        del session['signup_username_falied']
    if 'login_failed' in session:
        del session['login_failed']
    if request.method == 'POST':
        del session['username']
    return render_template('home.html', logged_in=check_logged_in(), verifier=check_verifier())

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

    temp_recent_runs = run_query_select(f"SELECT Player.name, Run.player_id, Run.run_id, Run.time FROM Run JOIN Player ON Player.player_id = Run.player_id WHERE Run.fullgame_category_id = '{category_id}' AND Run.verifier_id IS NOT NULL ORDER BY Run.date_submitted DESC LIMIT 15")
    recent_runs = []
    for i in temp_recent_runs:
        i = list(i)
        i[3] = converttime(i[3])
        recent_runs.append(i)




    return render_template('leaderboard_fullgame.html', 
                           runs=real_runs, categories=categories, 
                           category_id=category_id,
                           page=page, maxpage=maxpage,
                           recent_runs=recent_runs, logged_in=check_logged_in()
                           ,verifier=check_verifier())

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

    return render_template('leaderboard_individual_level.html', runs = real_runs, categories=categories, levels=levels, level=level, category=category, maxpage=maxpage, page=page, individual_level_id=individual_level_id, logged_in=check_logged_in(),verifier=check_verifier())

@app.route('/login')
def login():
    if 'submit_run' in session:
        del session['submit_run']
        return render_template('login.html', failed=False, submit_run=True)
    elif 'login_failed' in session:
        del session['login_failed']
        return render_template('login.html', failed=True, submit_run=False)
    else:
        return render_template('login.html', failed=False, submit_run=False)
    
@app.route('/check_valid_login', methods = ['GET', 'POST'])
def check_valid_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        submit_run = request.form['submit_run']
        given_hash = password.encode()
        given_hash = hashlib.sha256(given_hash).hexdigest()
        user_hash = run_query_select(f"SELECT Player.hash FROM Player WHERE Player.name = '{username}'")
        if not user_hash:
            session['login_failed'] = True
            return redirect(url_for('login'))
        user_hash = user_hash[0][0]
        if user_hash != given_hash:
            session['login_failed'] = True
            return redirect(url_for('login'))
        elif submit_run == 'False':
            session['username'] = [username, run_query_select(f"SELECT Player.player_id FROM Player WHERE Player.name = '{username}'")[0][0]]
            return redirect(url_for('home'))
        else:
            session['username'] = [username, run_query_select(f"SELECT Player.player_id FROM Player WHERE Player.name = '{username}'")[0][0]]
            return redirect(url_for('submit_run_fullgame'))

@app.route('/signup')
def signup():
    if 'signup_password_failed' in session:
        del session['signup_password_failed']
        return render_template('signup.html', password_failed=True, username_failed=False)
    elif 'signup_username_failed' in session:
        del session['signup_username_failed']
        return render_template('signup.html', password_failed=False, username_failed=True)
    else:
        return render_template('signup.html', password_failed=False, username_failed=False)

@app.route('/check_valid_signup', methods = ['GET', 'POST'])
def check_valid_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if not password == password_confirm:
            session['signup_password_failed'] = True
            return redirect(url_for('signup'))
        
        hash = password.encode()
        hash = hashlib.sha256(hash).hexdigest()

        if len(run_query_select(f"SELECT Player.name FROM Player WHERE name = '{username}'")) != 0:
            session['signup_username_failed'] = True
            return redirect(url_for('signup'))

        run_query_insert(f"INSERT INTO Player (player_id, name, pfp, hash) VALUES (?, ?, ?, ?)", (generate_id(), username, None, hash))
        return redirect(url_for('home'))

@app.route('/view_fullgame_run/<run_id>')
def view_fullgame_run(run_id):
    run1 = run_query_select(f"SELECT Run.run_id, Run.time, Run.date_submitted, Run.fullgame_category_id, Run.video_link, Run.player_id, Player.name, Fullgame_category.name, Platform.name FROM Run JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id JOIN Fullgame_category on Run.fullgame_category_id = Fullgame_category.fullgame_category_id WHERE Run.run_id = '{run_id}'")
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
    elif 'watch' in video_url:
        video_id = video_url.split("=")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        embed_url = video_url  

    run[4] = embed_url

    run.append(get_run_rank(run_id, True, True))

    if run_query_select(f"SELECT * FROM Run WHERE Run.verifier_id IS NOT NULL AND Run.run_id = '{run_id}'"):
        verifier_id = run_query_select(f"SELECT Run.verifier_id FROM Run WHERE Run.run_id = '{run_id}'")
        verifier = run_query_select(f"SELECT Player.name FROM Verifier JOIN Player ON Verifier.player_id = Player.player_id WHERE Verifier.verifier_id = '{verifier_id[0][0]}'")   
        run.append(verifier[0][0])
    else:
        run.append(False)
    return render_template('view_fullgame_run.html', run=run, logged_in=check_logged_in(), verifier=check_verifier())

@app.route('/view_individual_level_run/<run_id>')
def view_individual_level_run(run_id):
    run1 = run_query_select(f"SELECT Run.run_id, Run.time, Run.date_submitted, Run.il_id, Run.video_link, Run.player_id, Player.name, Platform.name FROM Run JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id WHERE Run.run_id = '{run_id}'")
    run_temp = run1[0]

    run = []
    for i in run_temp:
        run.append(i)

    level_category = run_query_select(f"SELECT Individual_level.il_id, IL_category.name, IL_category.il_category_id, Level.name, Level.level_id FROM Individual_level JOIN IL_category ON Individual_level.il_category_id = IL_category.il_category_id JOIN Level ON Individual_level.level_id = Level.level_id WHERE Individual_level.il_id = '{run[3]}'")

    run[3] = level_category[0]

    run[1] = converttime(run[1])
    video_url = run[4]
    run[2] = seconds_since_1980_to_date(run[2])
    print(run)
    if "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif 'watch' in video_url:
        video_id = video_url.split("=")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        embed_url = video_url  

    run[4] = embed_url

    run.append(get_run_rank(run_id, False, True))

    if run_query_select(f"SELECT * FROM Run WHERE Run.verifier_id IS NOT NULL AND Run.run_id = '{run_id}'"):
        verifier_id = run_query_select(f"SELECT Run.verifier_id FROM Run WHERE Run.run_id = '{run_id}'")
        verifier = run_query_select(f"SELECT Player.name FROM Verifier JOIN Player ON Verifier.player_id = Player.player_id WHERE Verifier.verifier_id = '{verifier_id[0][0]}'")   
        run.append(verifier[0][0])
    else:
        run.append(False)
    return render_template('view_individual_level_run.html', run=run, logged_in=check_logged_in(), verifier=check_verifier())

@app.route('/player_account_fullgame/<player_id>')
def player_account_fullgame(player_id):
    temp_categories = run_query_select(f"SELECT fullgame_category_id, name FROM Fullgame_category")
    runs = {}
    for i in temp_categories:
        temp_runs = run_query_select(f"SELECT Run.run_id, Run.time, Run.date_submitted, Platform.name, Run.video_link FROM Run JOIN Platform ON Run.platform_id = Platform.platform_id WHERE Run.fullgame_category_id = '{i[0]}' AND Run.player_id = '{player_id}' AND Run.verifier_id IS NOT NULL ORDER BY Run.time ASC")
        if temp_runs:
            temp_runs_three = []
            for j in temp_runs:
                temp_runs_two = list(j)
                temp_runs_two[1] = converttime(temp_runs_two[1])
                temp_runs_two[2] = seconds_since_1980_to_date(temp_runs_two[2])
                temp_runs_three.append(temp_runs_two)
            runs[i[0]] = temp_runs_three
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    for i in runs:
        for j in runs[i]:
            j.append(get_run_rank(j[0], True, False))
            video_url = j[4]
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1]
                embed_url = f"https://www.youtube.com/embed/{video_id}"
            else:
                embed_url = video_url
            j[4] = embed_url

    return render_template('player_account_fullgame.html',player_id=player_id, runs=runs, categories=categories, logged_in=check_logged_in(), verifier=check_verifier())

@app.route('/player_account_individual_level/<player_id>')
def player_account_individual_level(player_id):
    temp_categories = run_query_select(f"SELECT IL_category_id, name FROM IL_category")
    temp_levels = run_query_select(f"SELECT level_id, name FROM Level")
    runs = {}
    for i in temp_levels:
        runs[i[0]] = {}

    for i in temp_categories:
        for c in temp_levels:
            il_id = run_query_select(f"SELECT il_id FROM Individual_level WHERE level_id = '{c[0]}' AND IL_category_id = '{i[0]}'")
            if not il_id:
                continue
            temp_runs = run_query_select(f"SELECT Run.run_id, Run.time, Run.date_submitted, Platform.name, Run.video_link FROM Run JOIN Platform ON Run.platform_id = Platform.platform_id WHERE Run.il_id = '{il_id[0][0]}' AND Run.player_id = '{player_id}' AND Run.verifier_id IS NOT NULL ORDER BY Run.time ASC")
            if temp_runs:
                temp_runs_three = []
                for j in temp_runs:
                    temp_runs_two = list(j)
                    temp_runs_two[1] = converttime(temp_runs_two[1])
                    temp_runs_two[2] = seconds_since_1980_to_date(temp_runs_two[2])
                    temp_runs_three.append(temp_runs_two)
                runs[c[0]][i[0]] = temp_runs_three
    

    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    levels = {}
    for i in temp_levels:
        levels[i[0]] = i[1]

    to_be_deleted = []

    for i in runs:
        if len(runs[i]) == 0:
            to_be_deleted.append(i)
        for j in runs[i]:
            for c in runs[i][j]:
                c.append(get_run_rank(c[0], False, False))
                video_url = c[4]
                if "youtu.be" in video_url:
                    video_id = video_url.split("/")[-1]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                else:
                    embed_url = video_url
                c[4] = embed_url

    for i in to_be_deleted:
        del runs[i]



    return render_template('player_account_individual_level.html',player_id=player_id, runs=runs, categories=categories, levels=levels, logged_in=check_logged_in(), verifier=check_verifier())

@app.route('/submit_run_fullgame')
def submit_run_fullgame():
    temp_categories = run_query_select(f"SELECT fullgame_category_id, name FROM Fullgame_category")
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    temp_platforms = run_query_select(f"SELECT platform_id, name FROM Platform")
    platforms = {}
    for i in temp_platforms:
        platforms[i[0]] = i[1]

    if check_logged_in():
        return render_template('submit_run_fullgame.html',categories=categories, platforms=platforms, logged_in=check_logged_in(), verifier=check_verifier())
    else:
        session['submit_run'] = True
        return redirect(url_for('login'))
    
@app.route('/submit_run_individual_level')
def submit_run_individual_level():
    temp_categories = run_query_select(f"SELECT il_category_id, name FROM IL_category")
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    temp_platforms = run_query_select(f"SELECT platform_id, name FROM Platform")
    platforms = {}
    for i in temp_platforms:
        platforms[i[0]] = i[1]

    temp_levels = run_query_select(f"SELECT level_id, name FROM Level")
    levels = {}
    for i in temp_levels:
        levels[i[0]] = i[1]

    if check_logged_in():
        return render_template('submit_run_individual_level.html',categories=categories, platforms=platforms, levels=levels, logged_in=check_logged_in(), verifier=check_verifier())
    else:
        return render_template('login.html')

@app.route('/process_run_fullgame', methods=['GET', 'POST'])
def process_run_fullgame():
    link = request.form['submit_run_link']
    category = request.form['submit_run_category_dropwdown']
    time_hours = request.form['time-hours'] or '0'
    time_seconds = request.form['time-seconds'] or '0'
    time_minutes = request.form['time-minutes'] or '0'
    time_milliseconds = request.form['time-milliseconds'] or '0'
    platform = request.form['platforms']


    time = time_hours + ':' + time_minutes + ':' + time_seconds + '.' + time_milliseconds
    time = convert_time_to_seconds(time)




    today = datetime.date.today()
    date_submitted = int((today - start_date).total_seconds())



    run_query_insert("INSERT INTO Run (run_id, fullgame_category_id, il_id, verifier_id, time, date_submitted, player_id, platform_id, video_link, obsolete) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (generate_id(), category, None, None, time, date_submitted, session['username'][1], platform, link, None))
    return redirect(url_for('home'))

@app.route('/process_run_individual_level', methods=['GET', 'POST'])
def process_run_individual_level():
    link = request.form['submit_run_link']
    category = request.form['submit_run_category_dropwdown']
    level = request.form['submit_run_level_dropwdown']
    time_hours = request.form['time-hours'] or '0'
    time_seconds = request.form['time-seconds'] or '0'
    time_minutes = request.form['time-minutes'] or '0'
    time_milliseconds = request.form['time-milliseconds'] or '0'
    platform = request.form['platforms']


    time = time_hours + ':' + time_minutes + ':' + time_seconds + '.' + time_milliseconds
    time = convert_time_to_seconds(time)


    il_id = run_query_select(f"SELECT il_id from Individual_level WHERE level_id = '{level}' AND il_category_id = '{category}'")
    if len(il_id) == 0:
        return redirect(url_for('submit_run_individual_level'))


    today = datetime.date.today()
    date_submitted = int((today - start_date).total_seconds())



    run_query_insert("INSERT INTO Run (run_id, fullgame_category_id, il_id, verifier_id, time, date_submitted, player_id, platform_id, video_link, obsolete) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (generate_id(), None, il_id[0][0], None, time, date_submitted, session['username'][1], platform, link, None))
    return redirect(url_for('home'))

@app.route('/verify_runs')
def verify_runs():
    fullgame_runs = run_query_select("SELECT Run.date_submitted, Run.run_id, Player.name, Run.time, Platform.platform_id, Fullgame_category.name FROM Run JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id JOIN Fullgame_category ON Run.fullgame_category_id = Fullgame_category.fullgame_category_id WHERE Run.verifier_id IS NULL AND Run.il_id IS NULL ORDER BY Run.date_submitted DESC")
    il_runs = run_query_select("SELECT Run.date_submitted, Run.run_id, Player.name, Run.time, Platform.platform_id, Run.il_id FROM Run JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id JOIN Individual_level ON Run.il_id = Individual_level.il_id WHERE Run.verifier_id IS NULL AND Run.fullgame_category_id IS NULL ORDER BY Run.date_submitted DESC")

    for v, i in enumerate(fullgame_runs):
        fullgame_runs[v].append(0)

    for v, i in enumerate(il_runs):
        il_id = i[5]
        category_level = run_query_select(f"SELECT Level.name, Il_category.name FROM Individual_level JOIN Level ON Individual_level.level_id = Level.level_id JOIN Il_category ON Individual_level.il_category_id = Il_category.il_category_id WHERE Individual_level.il_id = '{il_id}'")
        il_runs[v].append(category_level[0][0])
        il_runs[v].append(category_level[0][1])
        il_runs[v].append(1)


    runs = fullgame_runs + il_runs

    runs = sorted(runs, key=lambda x: x[0])


    for v, i in enumerate(runs):
        runs[v][0] = seconds_since_1980_to_date(i[0])
        runs[v][3] = converttime(i[3])


    return render_template('verify_runs.html', runs=runs, logged_in=check_logged_in(), verifier=check_verifier())

@app.route('/verify_run',  methods=['GET', 'POST'])
def verify_run():
    verify_deny = request.form['verify_deny']
    run_id = request.form['verify_run']
    if verify_deny == 'deny':
        run_query_update(f"DELETE FROM Run WHERE run_id = '{run_id}'")
        return redirect(url_for('home'))
    if run_query_select(f"SELECT * FROM Run WHERE Run.run_id = '{run_id}' AND Run.il_id IS NOT NULL"):
        il_id = run_query_select(f"SELECT Run.il_id FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        player_id = run_query_select(f"SELECT Run.player_id FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        run_time = run_query_select(f"SELECT Run.time FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        pb = run_query_select(f"SELECT Run.run_id, Run.time FROM Run WHERE Run.il_id = '{il_id}' AND Run.obsolete = 0 AND Run.player_id = '{player_id}'")
        obsolete = 1
        if pb:
            if run_time <= pb[0][1]:
                obsolete = 0
    else:
        category_id = run_query_select(f"SELECT Run.fullgame_category_id FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        player_id = run_query_select(f"SELECT Run.player_id FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        run_time = run_query_select(f"SELECT Run.time FROM Run WHERE Run.run_id = '{run_id}'")[0][0]
        pb = run_query_select(f"SELECT Run.run_id, Run.time FROM Run WHERE Run.fullgame_category_id = '{category_id}' AND Run.obsolete = 0 AND Run.player_id = '{player_id}'")
        obsolete = 1
        if pb:
            if run_time <= pb[0][1]:
                obsolete = 0
                run_query_update(f"UPDATE Run SET obsolete = 1 WHERE run_id = '{pb[0][0]}'")

    run_query_update(f"UPDATE Run SET verifier_id = '{run_query_select(f"SELECT Verifier.verifier_id FROM Verifier WHERE Verifier.player_id = '{session['username'][1]}'")[0][0]}', obsolete = '{obsolete}' WHERE run_id = '{run_id}'")

    return redirect(url_for('home'))






if __name__ == '__main__':
    app.run(debug=True)
