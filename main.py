from flask import (Flask, render_template, request,
                   session, redirect, url_for, abort)
import datetime
import sqlite3
import math
import random
import hashlib

app = Flask(__name__)
app.secret_key = 'a055b9695803b8412f81833adde61422ed86b4d928ebbdb99f8b4f687c78'
start_date = datetime.date(1980, 1, 1)


def generate_id():
    """this function generates random ids for things like runs or
    users, needed to make player ids more random incase i want to
    add private acounts later, same with runs, future proofing"""

    # choose 8 random characters out of 0123456789abcdef
    id = ''
    for i in range(8):
        id += random.choices('0123456789abcdef', k=1)[0]
    return id


def get_run_rank(run_id, fullgame, obsolete=False):
    """this function gets the placement on the leaderboardfor a given run,
    given the run id, whether its fullgame or an il run, and whether you want
    to include obsolete runs or not. needed to display the
    rank of each run for the player account page"""

    # check if fullgame or il
    if fullgame:

        # if fullgame get the fullgame category id
        category_id = run_query_select("""SELECT Run.fullgame_category_id FROM
                                       Run WHERE Run.run_id = ?""", (run_id,))

        # depending on whether it should include obsolete runs
        # or not get all the runs with that category id sorted by time
        if obsolete:
            allruns = run_query_select("""SELECT Run.run_id FROM Run
                                       WHERE Run.fullgame_category_id = ?
                                       AND obsolete = 0 ORDER BY Run.time""",
                                       (category_id[0][0],))
        elif not obsolete:
            allruns = run_query_select("""SELECT Run.run_id FROM Run
                                       WHERE Run.fullgame_category_id =
                                       ? ORDER BY Run.time""",
                                       (category_id[0][0],))
    else:

        # if il get the il category id
        category_id = run_query_select("""SELECT Run.il_id FROM Run
                                       WHERE Run.run_id = ?""", (run_id,))

        # depending on whether it should include obsolete runs
        # or not get all the runs with that category id sorted by time
        if obsolete:
            allruns = run_query_select("""SELECT Run.run_id FROM Run
                                       WHERE Run.il_id = ? AND obsolete = 0
                                       ORDER BY Run.time""",
                                       (category_id[0][0],))
        elif not obsolete:
            allruns = run_query_select("""SELECT Run.run_id FROM Run
                                       WHERE Run.il_id = ? ORDER BY
                                       Run.time""", (category_id[0][0],))

    # enumerate through all the runs until you find the one with your run id
    for index, runinallruns in enumerate(allruns):
        if runinallruns[0] == run_id:

            # once you find the run placement format the number
            # with suffixes and return final placement
            if ((str(index)[-2:] == '10') or
                    (str(index)[-2:] == '11') or
                    (str(index)[-2:] == '12')):
                return f'{index+1}th'
            elif str(index)[-1] == '0':
                return f'{index+1}st'
            elif str(index)[-1] == '1':
                return f'{index+1}nd'
            elif str(index)[-1] == '2':
                return f'{index+1}rd'
            else:
                return f'{index+1}th'

    # incase it cant find the run return false
    return False


def run_query_select(query, values):
    """this function runs a select query given the query
    string and the parameter values."""

    # run the query with given values
    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()

    cursor.execute(query, values)
    temp_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    rows = []

    # turns all the tuples in the output into lists, this is here becuase lists
    # are a lot easier to manipluate then tuples as tuples are
    # unchangeable so it makes changing the data later easier
    for i in temp_rows:
        rows.append(list(i))
    return rows


def run_query_insert(query, values):
    """this function runs an insert query given
    the query and the parameter values"""

    # run the insert query with given values
    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()


def run_query_update(query, values):
    """this function runs an update query
    given the query and the parameter values"""

    # run the update query with the given value
    conn = sqlite3.connect('database_new.db')
    cursor = conn.cursor()

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()


def converttime(run_time):
    """this function takes a float for the number of seconds eg 1223.456 and
    turns it into a formated time like 20m 23s 456ms, needed because
    run times are stored as floats of seconds in the database
    becuase its much easier to store and easier to sort"""

    # if run time greater than one hour (3600 seconds)
    if run_time >= 3600:

        # get the hours, minutes, seconds, and milliseconds
        # then combine them into one large string
        h, remainder = divmod(run_time, 3600)
        m, remainder = divmod(round(remainder, 3), 60)
        m = str(int(m))
        if len(m) == 1:
            m = '0' + m
        s, ms = str(round(remainder, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s

        # depending on how many digits in the milliseconds,
        # add the right amount of trailing zero's
        for i in range(3-len(ms)):
            ms = '0' + ms
        output = f'{int(h)}h {m}m {s}s {ms}ms'
        return output

    # if run time greater than one minute (60 seconds)
    elif run_time >= 60:

        # get the minutes, seconds, and milliseconds
        # then combine them into one large string
        m, remainder = divmod(run_time, 60)
        s, ms = str(round(remainder, 3)).split('.')
        m = str(int(m))
        if len(m) == 1:
            m = '0' + m
        s, ms = str(round(remainder, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s

        # depending on how many digits in the milliseconds,
        # add the right amount of trailing zero's
        for i in range(3-len(ms)):
            ms = '0' + ms
        output = f'{m}m {s}s {ms}ms'
        return output

    # if the run time is less than one minute
    else:

        # get the seconds and milliseconds
        # then combine them into one large string
        s, ms = str(round(run_time, 3)).split('.')
        s = str(int(s))
        if len(s) == 1:
            s = '0' + s

        # depending on how many digits in the milliseconds,
        # add the right amount of trailing zero's
        for i in range(3-len(ms)):
            ms = '0' + ms
        output = f'{s}s {ms}ms'
        return output


def convert_time_to_seconds(time):
    """this function takes a formated time eg 20m 23s 456ms and turns
    it into a float of seconds like 1223.456, needed because
    run times are stored as floats of seconds in the database
    becuase its much easier to store and easier to sort"""

    time = str(time)
    colon_count = 0

    # get amount of colons in string to determine if the
    # time is in hours, minutes, or seconds
    for i in time:
        if i == ':':
            colon_count += 1

    # if no colons time is already in seconds
    if colon_count == 0:
        return time

    # if one colon time is in minutes, minutes get x60 then added to seconds
    if colon_count == 1:
        minutes, seconds = time.split(':')
        return round(int(minutes)*60 + float(seconds), 3)

    # if two colons time is in hours, hours get x3600,
    # minutes get x60 then added to seconds
    if colon_count == 2:
        hours, minutes, seconds = time.split(':')
        return round(int(hours)*3600 + int(minutes)*60 + float(seconds), 3)\

    return False


def check_valid_time_hours(hours):
    """this function checks if given a string for number of hours, checks if it
    meet the valid critera, integer and 1-2 digits, needed to
    make sure the times that users submit are valid"""

    # check if its integer
    if not hours.isdigit():
        return False

    # check if its too large
    if int(hours) > 99:
        return False
    return True


def check_valid_time_seconds(seconds):
    """this function checks if given a string for number of seconds, checks if
    it meet the valid critera, integer and between 0 and 59 inclusive,
    needed to make sure the times that users submit are valid"""

    # check if its integer
    if not seconds.isdigit():
        return False

    # check if its too large
    if int(seconds) > 59:
        return False
    return True


def check_valid_time_minutes(minutes):
    """this function checks if given a string for number of minutes, checks if
    it meet the valid critera, integer and between 0 and 59 inclusive,
    needed to make sure the times that users submit are valid"""

    # check if its integer
    if not minutes.isdigit():
        return False

    # check if its too large
    if int(minutes) > 59:
        return False
    return True


def check_valid_time_milliseconds(milliseconds):
    """this function checks if given a string for number of hours, checks if it
    meet the valid critera, integer and 1-3 digits, needed to
    make sure the times that users submit are valid"""

    # check if its integet
    if not milliseconds.isdigit():
        return False

    # check if its too large
    if len(str(int(milliseconds))) > 999:
        return False
    return True


def seconds_since_1980_to_date(seconds):
    """takes a number of seconds since 1980 january 1st 00:00.000 and
    turns it into a date, needed because the dates in the database
    are stored as floats as seconds since 1980 becuase its
    easier to sort and store as consistant numbers"""

    # get special format for time at 1980 january 1st 00:00.000
    date_1980 = datetime.date(1980, 1, 1)

    # take the number of seconds, turn it into a
    # date, then add it to the 1980 date
    date = date_1980 + datetime.timedelta(seconds=seconds)

    # format the date
    return date.strftime("%d/%m/%Y")


def check_logged_in():
    """checks if the user is logged in or not, needed becuase the navbar
    needs to know if the user is logged in to display the right things
    and submit run page needs to know if logged in to allow you to enter"""

    if 'username' in session:
        return session['username']
    else:
        return False


def check_verifier():
    """checks if the user is logged in as a verifier because the navbar
    needs to know to display the right thing and the view run
    page needs to know to display verify and deny buttons"""

    if 'username' not in session:
        return False

    # check to see if the logged in user is a verifier by getting
    #  verifier id from player id, if it comes up
    # with at least 1 result then must be verifier
    if len(run_query_select("""SELECT verifier.verifier_id FROM Verifier
                            JOIN Player on Player.player_id =
                            Verifier.player_id WHERE Player.player_id = ?""",
                            (session['username'][1],))) != 0:
        return True


@app.route('/', methods=['GET', 'POST'])
def home():
    """this route only serves the purpose of imediatly redirecting to the
    leaderboard fullgame page which is the home page, it is needed
    because an empty url is the first thing that opens when you
    run the app so its needed to redirect to the real home page"""

    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/leaderboard_fullgame/<category_id>/<page>', methods=['GET', 'POST'])
def leaderboard_fullgame(category_id, page):
    """this route is the leaderboard page for fullgame runs, it shows
    all the runs for a given category and page number, it also serves
    as the home page becuase for any new user it makes logical sense
    that they see the page that shows the top 100 times for the
    most speedrun category aswell as i dont have any
    information that i would want to put on a home page"""

    # clear anything that could be in the session that needs
    # to be removed after redirecting to this page
    if 'signup_password_falied' in session:
        del session['signup_passord_falied']
    if 'signup_username_taken' in session:
        del session['signup_username_taken']
    if 'signup_username_length_invalid' in session:
        del session['signup_username_length_invalid']
    if 'signup_username_spaces_invalid' in session:
        del session['signup_username_spaces_invalid']
    if 'signup_username_special_characters_invalid' in session:
        del session['signup_username_special_characters_invalid']
    if 'login_failed' in session:
        del session['login_failed']

    # if the user clicked logout button remove them from session
    if request.method == 'POST':
        del session['username']

    valid_category = False

    # get fullgame category ids
    category_ids = run_query_select("""SELECT Fullgame_category.fullgame_category_id
                                    FROM Fullgame_category""", ())

    # if category id doesn't match any of the ones in
    # the above list then 404, needed to make sure
    # the category id given in the url was a valid category id
    for i in category_ids:
        if i[0] == category_id:
            valid_category = True

    if not valid_category:
        abort(404)

    # make sure page number is an integer, if not
    # then just redirect to self with page as 0
    if not page.isdigit():
        return redirect(url_for('leaderboard_fullgame',
                                category_id=category_id, page=0))

    page = int(page)

    # get all the fullgame runs with the specific category id,
    # get bascally all the information about each
    # run, dont include obsolete runs and unverifed runs
    # join player and platform on run to get those values instead of id's
    all_runs = run_query_select("""SELECT Run.run_id, Player.name,
                            Player.player_id, Run.time,Run.video_link,
                            Run.date_submitted, Platform.name FROM Run
                            JOIN Player ON Run.player_id = Player.player_id
                            JOIN Platform ON Run.platform_id = Platform.platform_id
                            WHERE Fullgame_category_id = ?
                            AND Run.verifier_id IS NOT NULL
                            AND Run.obsolete = 0 ORDER BY Run.time ASC""",
                            (category_id,))

    length = len(all_runs)
    max_page = math.floor(length/100)

    # if page is greater then max possible page then not
    # possible so redirect to self with page = max page
    if max_page < page:
        return redirect(url_for('leaderboard_fullgame',
                                category_id=category_id, page=max_page))

    runs = []

    # get the correct set of runs bassed on the page number
    if page != max_page:
        for i in range(100):
            runs.append(all_runs[page*100 + i])
    else:
        for i in range(int(str(length)[-2:])):
            runs.append(all_runs[page*100 + i])

    # convert the time and date of all the runs
    for v, i in enumerate(runs):
        runs[v][3] = converttime(i[3])
        runs[v].append(seconds_since_1980_to_date(i[5]))

    categories_temp = run_query_select("""SELECT fullgame_category_id, name
                                       FROM Fullgame_category""", ())

    # make category dict, needed for dropdown
    categories = {}
    for i in categories_temp:
        categories[i[0]] = i[1]

    # get all the runs done recently for the
    # category id, with the same params as before
    # join player on run to get player name instead of player id
    temp_recent_runs = run_query_select("""SELECT Player.name, Run.player_id,
                                        Run.run_id, Run.time FROM Run
                                        JOIN Player ON 
                                        Player.player_id = Run.player_id
                                        WHERE Run.fullgame_category_id = ?
                                        AND Run.verifier_id IS NOT NULL
                                        ORDER BY Run.date_submitted
                                        DESC LIMIT 15""", (category_id,))
    recent_runs = []

    # convert the times and make the recent run list
    for i in temp_recent_runs:
        i[3] = converttime(i[3])
        recent_runs.append(i)

    # get the rules of the category from the database
    rules = run_query_select("""SELECT Fullgame_category.rules
                             FROM Fullgame_category WHERE
                             Fullgame_category.fullgame_category_id = ?""",
                             (category_id,))[0][0]

    return render_template('leaderboard_fullgame.html',
                           runs=runs, categories=categories,
                           category_id=category_id, rules=rules,
                           page=page, max_page=max_page,
                           recent_runs=recent_runs,
                           logged_in=check_logged_in(),
                           verifier=check_verifier())


@app.route('/leaderboard_individual_level/<individual_level_id>/<page>')
def individual_level_leaderboard(individual_level_id, page):
    """this route is the leaderboard page for individual level runs, it shows
    all the runs for a given level, category and page number"""

    valid_individual_level_id = False

    # get all individual level ids
    individual_level_ids = run_query_select("""SELECT Individual_level.il_id
                                            FROM Individual_level""", ())

    # if il id doesn't match any of the ones in
    # the above list then 404, needed to make sure
    # the il id given in the url was a valid il id
    for i in individual_level_ids:
        if i[0] == individual_level_id:
            valid_individual_level_id = True

    if not valid_individual_level_id:
        abort(404)

    # make sure page number is an integer, if not
    # then just redirect to self with page as 0
    if not page.isdigit():
        return redirect(url_for('individual_level_leaderboard',
                                individual_level_id=individual_level_id,
                                page=0))

    page = int(page)

    # get all the fullgame runs with the specific il id,
    # get bascally all the information about each
    # run, dont include obsolete runs and unverifed runs
    # join player and platform on run to get those values instead of id's
    all_runs = run_query_select("""SELECT Run.run_id, Player.name,
                            Player.player_id, Run.time,Run.video_link,
                            Run.date_submitted, Platform.name FROM Run
                            JOIN Player ON Run.player_id = Player.player_id
                            JOIN Platform ON Run.platform_id = Platform.platform_id
                            WHERE il_id = ? AND Run.verifier_id IS NOT NULL
                            AND Run.obsolete = 0
                            ORDER BY Run.time ASC""", (individual_level_id,))

    length = len(all_runs)
    max_page = math.floor(length/100)

    # if page is greater then max possible page then not
    # possible so redirect to self with page = max page
    if max_page < page:
        return redirect(url_for('individual_level_leaderboard',
                                individual_level_id=individual_level_id,
                                page=max_page))

    runs = []

    # get the correct set of runs bassed on the page number
    if page != max_page:
        for i in range(100):
            runs.append(all_runs[page*100 + i])
    else:
        for i in range(int(str(length)[-2:])):
            runs.append(all_runs[page*100 + i])

    # convert the time and date of all the runs
    for v, i in enumerate(runs):
        runs[v][3] = converttime(i[3])
        runs[v].append(seconds_since_1980_to_date(i[5]))

    # get the level, needed for dropdown
    # join level on individual level to get level name instead of level id
    level = run_query_select("""SELECT Level.name, Level.level_id
                             FROM Individual_level JOIN Level ON
                             Individual_level.level_id = Level.level_id
                             WHERE Individual_level.il_id = ?""",
                             (individual_level_id,))[0]

    # get the category, needed for category buttons diff colour
    # join il caetgory on indidual level to get il category
    # name instead of il category id
    category = run_query_select("""SELECT IL_category.name,
                                IL_category.il_category_id
                                FROM Individual_level JOIN IL_category ON
                                Individual_level.il_category_id =
                                IL_category.il_category_id
                                WHERE Individual_level.il_id = ?""",
                                (individual_level_id,))[0]

    # create levels dictionart where the il id is each level and
    # category is always clear, needed for dropdown buttons
    levels_temp = run_query_select("SELECT level_id, name FROM Level", ())
    levels = {}
    for i in levels_temp:
        levels[i[0]] = [
            i[1],
            run_query_select("""SELECT Individual_level.il_id
                             FROM Individual_level
                             WHERE level_id = ? AND
                             il_category_id = '40ce5c88'""", (i[0],))[0][0]
            ]

    # create categories dict, needed for category buttons
    # join il category on run to get il category name instead of il category id
    categories_temp = run_query_select("""SELECT IL_category.il_category_id,
                                       IL_category.name FROM Individual_level
                                       JOIN IL_category ON
                                       Individual_level.il_category_id =
                                       IL_category.il_category_id
                                       WHERE level_id = ?""", (level[1],))
    categories = {}
    for i in categories_temp:
        categories[i[0]] = [
            i[1],
            run_query_select("""SELECT Individual_level.il_id
                             FROM Individual_level
                             WHERE level_id = ?
                             AND il_category_id = ?""",
                             (level[1], i[0]))[0][0]
            ]

    # get recent runs for the il id, same params as before
    # join player on run to get player name instead of player id
    temp_recent_runs = run_query_select("""SELECT Player.name, Run.player_id,
                                        Run.run_id, Run.time FROM Run
                                        JOIN Player ON Player.player_id = Run.player_id
                                        WHERE Run.il_id = ?
                                        AND Run.verifier_id IS NOT NULL
                                        ORDER BY Run.date_submitted
                                        DESC LIMIT 15""",
                                        (individual_level_id,))

    # convert time and compile all recent runs
    recent_runs = []
    for i in temp_recent_runs:
        i[3] = converttime(i[3])
        recent_runs.append(i)

    # get rules for category from database
    rules = run_query_select("""SELECT IL_category.rules
                             FROM IL_category WHERE
                             IL_category.il_category_id = ?""",
                             (category[1],))[0][0]

    # replace the placeholder in rule with actuall level name
    rules = rules.replace('THELEVEL', f"'{level[0]}'")

    return render_template('leaderboard_individual_level.html', runs=runs,
                           categories=categories, levels=levels, level=level,
                           category=category, max_page=max_page, page=page,
                           individual_level_id=individual_level_id,
                           recent_runs=recent_runs, rules=rules,
                           logged_in=check_logged_in(),
                           verifier=check_verifier())


@app.route('/login')
def login():
    """this route is the login page, it is needed so that users can login
    and interact with things that require an account"""

    # if submit run in session, means that they tried to
    # submit but wernt logged in so got sent here,
    # needed to display the error message
    if 'submit_run' in session:
        del session['submit_run']
        return render_template('login.html', failed=False, submit_run=True)

    # if login failed then they already tried to
    # login but failed, needed to display error message
    elif 'login_failed' in session:
        del session['login_failed']
        return render_template('login.html', failed=True, submit_run=False)
    else:
        return render_template('login.html', failed=False, submit_run=False)


@app.route('/check_valid_login', methods=['GET', 'POST'])
def check_valid_login():
    """this route checks when a user tries to login to see
    whether they inputed valid credentials or not, if
    they didn't then it sends them back to the login page"""

    # makes sure we were actually sent here and not just typd into url
    if request.method == 'POST':

        # get the users login data
        username = request.form['username']
        password = request.form['password']
        submit_run = request.form['submit_run']

        # hash the password given
        given_hash = password.encode()
        given_hash = hashlib.sha256(given_hash).hexdigest()

        # get hash from database with username
        user_hash = run_query_select("""SELECT Player.hash FROM Player
                                     WHERE Player.name = ?""", (username,))

        # if there was no hash returned then the player musn't exist
        if not user_hash:
            session['login_failed'] = True
            return redirect(url_for('login'))
        user_hash = user_hash[0][0]

        # if hashes dont match password must be wrong
        if user_hash != given_hash:
            session['login_failed'] = True
            return redirect(url_for('login'))

        # if submit run is false then the user gets
        # logged into the session and sent to the home page, else if submit
        # run was true they get sent to the submit run page, also logged in
        elif submit_run == 'False':
            session['username'] = [
                username,
                run_query_select("""SELECT Player.player_id FROM Player
                                 WHERE Player.name = ?""", (username,))[0][0]
                ]
            return redirect(url_for('leaderboard_fullgame',
                                    category_id='30831e37', page='0'))
        else:
            session['username'] = [
                username,
                run_query_select("""SELECT Player.player_id FROM Player
                                 WHERE Player.name = ?""", (username,))[0][0]
                ]
            return redirect(url_for('submit_run_fullgame'))

    # incase method not post go to home page
    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/signup')
def signup():
    """this route is the signup page, it is needed so that new users can
    create an accout to interact with things that require an account"""

    error_message_dict = {
        'signup_username_taken': False,
        'signup_password_failed': False,
        'signup_username_length_invalid': False,
        'signup_username_spaces_invalid': False,
        'signup_username_special_characters_invalid': False
    }

    # iterate through all possible error
    # messages and check if they are in session
    # to display correct error message on page
    for error_message in error_message_dict.keys():
        if error_message in session:
            del session[error_message]
            error_message_dict[error_message] = True

    return render_template('signup.html',
                           error_message_dict=error_message_dict)


@app.route('/check_valid_signup', methods=['GET', 'POST'])
def check_valid_signup():
    """this route checks when a user tries to signup to see
    whether they inputed valid credentials or not, if
    they didn't then it sends them back to the signup page"""

    # dict of all allowed characters for usernames
    normal_characters = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_'
    ]

    username = request.form['username']

    # chek that username is within length constraints,
    # needed for validating inputs so that the
    # usernames arent able to be 100 milion characters long
    if (len(username) < 3) or (len(username) > 20):
        session['signup_username_length_invalid'] = True
        return redirect(url_for('signup'))

    # check if usernae contains spaces, if so thats not allowed
    if ' ' in username:
        session['signup_username_spaces_invalid'] = True
        return redirect(url_for('signup'))

    # check if player name already exists in database, if so thats not allowed
    if len(run_query_select("""SELECT Player.name FROM Player
                            WHERE name = ?""", (username,))) != 0:
        session['signup_username_taken'] = True
        return redirect(url_for('signup'))

    # check that every character in username is in allowed
    # characters dict, if not then thats not allowed
    for i in username:
        if i not in normal_characters:
            session['signup_username_special_characters_invalid'] = True
            return redirect(url_for('signup'))

    password = request.form['password']
    password_confirm = request.form['password_confirm']

    # check that the password matches the password
    # confirm, if not thats not allowed
    if not password == password_confirm:
        session['signup_password_failed'] = True
        return redirect(url_for('signup'))

    # hash the password for the database
    hash = password.encode()
    hash = hashlib.sha256(hash).hexdigest()

    new_user_id = generate_id()

    # insert new player data into the database
    run_query_insert("""INSERT INTO Player (player_id, name, pfp, hash)
                     VALUES (?, ?, ?, ?)""",
                     (new_user_id, username, None, hash))

    # add new player as logged in to the session so the
    # rest of the website knows they are logged in
    session['username'] = [username, new_user_id]

    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/view_fullgame_run/<run_id>')
def view_fullgame_run(run_id):
    """this route is the view fullgame run page, it displays
    information about a single fullgame run given the run id"""

    # check that a fullgame run exists in the database with that id,
    # if not then run 404 page becasuse invalid run id
    run_checker = run_query_select("""SELECT Run.fullgame_category_id
                                   FROM Run WHERE Run.run_id = ?""", (run_id,))

    if (len((run_checker)) == 0) or (run_checker[0][0] is None):
        abort(404)

    # get all the information about the individual run, using the
    # run id, join the platform table, player table, and fullgame
    # category table onto run table to get those values instead of id's
    run = run_query_select("""SELECT Run.run_id, Run.time,
                            Run.date_submitted, Run.fullgame_category_id,
                            Run.video_link, Run.player_id, Player.name,
                            Fullgame_category.name, Platform.name FROM Run
                            JOIN Player ON Run.player_id = Player.player_id
                            JOIN Platform ON Run.platform_id = Platform.platform_id
                            JOIN Fullgame_category ON Run.fullgame_category_id =
                            Fullgame_category.fullgame_category_id
                            WHERE Run.run_id = ?""", (run_id,))[0]

    # convert the time and date
    run[1] = converttime(run[1])
    run[2] = seconds_since_1980_to_date(run[2])

    video_url = run[4]

    # check all possible link formats to see if the link fits one of them, if
    # it does format it into a embed link for either yt or twitch else make
    # embed link false so the html can play error image instead of video
    if "youtu.be/" in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif 'youtube.com/watch?v=' in video_url:
        video_id = video_url.split("=")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif 'youtube.com/embed/' in video_url:
        embed_url = video_url
    elif 'twitch.tv/videos/' in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://player.twitch.tv/?video={video_id}&parent=127.0.0.1"
    elif 'twitch.tv/channelname/video/' in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://player.twitch.tv/?video={video_id}&parent=127.0.0.1"
    else:
        embed_url = False

    run[4] = embed_url

    # get the placement of the ruun
    run.append(get_run_rank(run_id, True, True))

    # chech whether the run have been verifier,
    # if so then get verifier's inforation else append
    # false so the html knows its not verifier
    if run_query_select("""SELECT * FROM Run WHERE Run.verifier_id IS NOT NULL
                        AND Run.run_id = ?""", (run_id,)):
        verifier_id = run_query_select("""SELECT Run.verifier_id FROM Run
                                       WHERE Run.run_id = ?""", (run_id,))
        verifier = run_query_select("""SELECT Player.name FROM Verifier
                                    JOIN Player ON Verifier.player_id =
                                    Player.player_id WHERE
                                    Verifier.verifier_id = ?""",
                                    (verifier_id[0][0],))
        run.append(verifier[0][0])
    else:
        run.append(False)

    return render_template('view_fullgame_run.html', run=run,
                           logged_in=check_logged_in(),
                           verifier=check_verifier())


@app.route('/view_individual_level_run/<run_id>')
def view_individual_level_run(run_id):
    """this route is the view individual level run page, it displays
    information about a single individual level run given the run id"""

    # check that a il run exists in the database with that id,
    # if not then run 404 page becasuse invalid run id
    run_checker = run_query_select("""SELECT Run.il_id FROM Run
                                   WHERE Run.run_id = ?""", (run_id,))

    if (len(run_checker) == 0) or (run_checker[0][0] is None):
        abort(404)

    # get all the information about the individual run, using the
    # run id, join the platform table, player table,
    # onto run table to get those values instead of id's
    run = run_query_select("""SELECT Run.run_id, Run.time,
                            Run.date_submitted, Run.il_id, Run.video_link,
                            Run.player_id, Player.name, Platform.name FROM Run
                            JOIN Player ON Run.player_id = Player.player_id
                            JOIN Platform ON Run.platform_id = Platform.platform_id
                            WHERE Run.run_id = ?""", (run_id,))[0]

    # get the level and category given the il_id
    level_category = run_query_select("""SELECT Individual_level.il_id,
                                      IL_category.name,
                                      IL_category.il_category_id, Level.name,
                                      Level.level_id FROM Individual_level
                                      JOIN IL_category ON
                                      Individual_level.il_category_id =
                                      IL_category.il_category_id
                                      JOIN Level ON Individual_level.level_id =
                                      Level.level_id WHERE
                                      Individual_level.il_id = ?""", (run[3],))

    # conver time and date and add category and level
    run[1] = converttime(run[1])
    run[2] = seconds_since_1980_to_date(run[2])
    run[3] = level_category[0]

    video_url = run[4]

    # check all possible link formats to see if the link fits one of them, if
    # it does format it into a embed link for either yt or twitch else make
    # embed link false so the html can play error image instead of video
    if "youtu.be/" in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif 'youtube.com/watch?v=' in video_url:
        video_id = video_url.split("=")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif 'youtube.com/embed/' in video_url:
        embed_url = video_url
    elif 'twitch.tv/videos/' in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://player.twitch.tv/?video={video_id}&parent=127.0.0.1"
    elif 'twitch.tv/channelname/video/' in video_url:
        video_id = video_url.split("/")[-1]
        embed_url = f"https://player.twitch.tv/?video={video_id}&parent=127.0.0.1"
    else:
        embed_url = False

    run[4] = embed_url

    # get run placement
    run.append(get_run_rank(run_id, False, True))

    # chech whether the run have been verifier,
    # if so then get verifier's inforation else append
    # false so the html knows its not verifier
    if run_query_select("""SELECT * FROM Run WHERE Run.verifier_id IS NOT NULL
                        AND Run.run_id = ?""", (run_id,)):
        verifier_id = run_query_select("""SELECT Run.verifier_id FROM Run
                                       WHERE Run.run_id = ?""", (run_id,))
        verifier = run_query_select("""SELECT Player.name FROM Verifier
                                    JOIN Player ON Verifier.player_id =
                                    Player.player_id
                                    WHERE Verifier.verifier_id = ?""",
                                    (verifier_id[0][0],))
        run.append(verifier[0][0])
    else:
        run.append(False)
    return render_template('view_individual_level_run.html', run=run,
                           logged_in=check_logged_in(),
                           verifier=check_verifier())


@app.route('/player_account_fullgame/<player_id>', methods=['GET', 'POST'])
def player_account_fullgame(player_id):
    """this route is the view player fullgame page, it shows all the
    fullgame runs a player has done given their player id"""

    # check if player exists given player id, if not 404
    if len(run_query_select("""SELECT Player.player_id FROM Player
                            WHERE Player.player_id = ?""", (player_id,))) == 0:
        abort(404)

    # get all fullgame categories and interate throguh them
    categories = run_query_select("""SELECT fullgame_category_id,
                                       name FROM Fullgame_category""", ())
    runs = {}
    for i in categories:
        # get all the information about all user runs from each category
        temp_runs = run_query_select("""SELECT Run.run_id, Run.time,
                                     Run.date_submitted, Platform.name,
                                     Run.video_link FROM Run JOIN Platform
                                     ON Run.platform_id = Platform.platform_id
                                     WHERE Run.fullgame_category_id = ?
                                     AND Run.player_id = ?
                                     AND Run.verifier_id IS NOT NULL
                                     ORDER BY Run.time ASC""",
                                     (i[0], player_id))

    # if atleast 1 run exists
        if temp_runs:
            category_run_set = []

            # iterate through all the runs in that category and converter their
            # time and dates, then append the run to
            # the category run list, nd get run placement
            for j in temp_runs:
                run = list(j)
                run[1] = converttime(run[1])
                run[2] = seconds_since_1980_to_date(run[2])
                run.append(get_run_rank(run[0], True, False))
                category_run_set.append(run)

            # add the category run set to the runs dict with categry id as key
            runs[i[0]] = category_run_set

    # make category dict
    categories_dict = {}
    for i in categories:
        categories_dict[i[0]] = i[1]

    player_name = run_query_select("""SELECT Player.name FROM Player WHERE
                                   Player.player_id = ?""", (player_id,))[0][0]

    own_account = False

    if check_logged_in():
        user_name = check_logged_in()[0]
        if player_name == user_name:
            own_account = True

    print(own_account)

    return render_template('player_account_fullgame.html', player_id=player_id,
                           runs=runs, categories=categories_dict,
                           logged_in=check_logged_in(),
                           verifier=check_verifier(), player_name=player_name,
                           own_account=own_account)


@app.route('/player_account_individual_level/<player_id>')
def player_account_individual_level(player_id):
    """this route is the view player individual level page, it shows all the
    individual level runs a player has done given their player id"""

    # check if player exists given player id, if not 404
    if len(run_query_select("""SELECT Player.player_id FROM Player
                            WHERE Player.player_id = ?""",
                            (player_id, ))) == 0:
        abort(404)

    # get list of categoies
    temp_categories = run_query_select("""SELECT IL_category_id, name
                                       FROM IL_category""", ())

    # get list of levels
    temp_levels = run_query_select("SELECT level_id, name FROM Level", ())
    runs = {}

    # make database have key for each level id
    for i in temp_levels:
        runs[i[0]] = {}

    # iterate thtough all categories
    for category in temp_categories:

        # iterate through all levels
        for level in temp_levels:

            # check that the level category pair is a valid il, if not continue
            il_id = run_query_select("""SELECT il_id FROM Individual_level
                                     WHERE level_id = ?
                                     AND IL_category_id = ?""",
                                     (level[0], category[0]))
            if not il_id:
                continue

            # get all user runs for that level category pari
            temp_runs = run_query_select("""SELECT Run.run_id, Run.time,
                                         Run.date_submitted, Platform.name,
                                         Run.video_link FROM Run
                                         JOIN Platform ON Run.platform_id =
                                         Platform.platform_id WHERE Run.il_id =
                                         ? AND Run.player_id = ?
                                         AND Run.verifier_id IS NOT NULL
                                         ORDER BY Run.time ASC""",
                                         (il_id[0][0], player_id))

            # if atleast 1 run exists
            if temp_runs:
                run_il_set = []

                # for each run convert time and date and get run placement,
                # then append the run to the il run list
                for j in temp_runs:
                    run = list(j)
                    run[1] = converttime(run[1])
                    run[2] = seconds_since_1980_to_date(run[2])
                    run.append(get_run_rank(run[0], False, False))
                    run_il_set.append(run)

                # add the il run set to dictionary,
                # with key as level and then cateogry id
                runs[level[0]][category[0]] = run_il_set

    # make categories dict
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    # make leveles dict
    levels = {}
    for i in temp_levels:
        levels[i[0]] = i[1]

    # goes through each level in the run dictionary
    # and if it contains no runs deletes it from dict so instead
    # of showing header on page it just doesnt exist, also deletes the
    # level from levels so that the level button doesnt show up on the page

    print(levels)

    to_be_deleted = []
    for i in runs:
        if len(runs[i]) == 0:
            to_be_deleted.append(i)

    for i in to_be_deleted:
        del runs[i]
        del levels[i]

    player_name = run_query_select("""SELECT Player.name FROM Player WHERE
                                   Player.player_id = ?""", (player_id,))[0][0]

    own_account = False

    if check_logged_in():
        user_name = check_logged_in()[0]
        if player_name == user_name:
            own_account = True

    return render_template('player_account_individual_level.html',
                           player_id=player_id, runs=runs, 
                           categories=categories, levels=levels,
                           logged_in=check_logged_in(),
                           verifier=check_verifier(), player_name=player_name,
                           own_account=own_account)


@app.route('/submit_run_fullgame')
def submit_run_fullgame():
    """this is the submit run fullgame page, it allows the user
    to submit a fullgame run to the database for
    it to be verified and then added to the leaderboards"""

    # get categories
    temp_categories = run_query_select("""SELECT fullgame_category_id, name
                                       FROM Fullgame_category""", ())

    # make category dict
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    # get platforms
    temp_platforms = run_query_select("""SELECT platform_id, name
                                      FROM Platform""", ())

    # make platform dict
    platforms = {}
    for i in temp_platforms:
        platforms[i[0]] = i[1]

    error_message_dict = {'submit_run_link_invalid': False,
                          'submit_run_category_invalid': False,
                          'submit_run_platform_invalid': False,
                          'submit_run_time_invalid': False}

    # if user isnt logged in they need to be redirected to log in page
    if not check_logged_in():
        session['submit_run'] = True
        return redirect(url_for('login'))

    # check if any error messages have been added to session, if so that means
    # the user tred to submit run but failed so error message needs to be shown
    for error_message in error_message_dict.keys():
        if error_message in session:
            del session[error_message]
            error_message_dict[error_message] = True

    return render_template('submit_run_fullgame.html', categories=categories,
                           platforms=platforms, logged_in=check_logged_in(),
                           verifier=check_verifier(),
                           error_message_dict=error_message_dict)


@app.route('/submit_run_individual_level')
def submit_run_individual_level():
    """this is the submit run individual level page, it allows the user
    to submit a individual level run to the database for
    it to be verified and then added to the leaderboards"""

    # get categories list
    temp_categories = run_query_select("""SELECT il_category_id, name
                                       FROM IL_category""", ())

    # make categories dict
    categories = {}
    for i in temp_categories:
        categories[i[0]] = i[1]

    # get platforms
    temp_platforms = run_query_select("""SELECT platform_id, name
                                      FROM Platform""", ())

    # make platform dict
    platforms = {}
    for i in temp_platforms:
        platforms[i[0]] = i[1]

    # get levels
    temp_levels = run_query_select("SELECT level_id, name FROM Level", ())

    # make levels dict
    levels = {}
    for i in temp_levels:
        levels[i[0]] = i[1]

    error_message_dict = {'submit_run_link_invalid': False,
                          'submit_run_category_invalid': False,
                          'submit_run_platform_invalid': False,
                          'submit_run_time_invalid': False,
                          'submit_run_level_invalid': False,
                          'submit_run_level_category_pair_invalid': False}

    # if user isnt logged in they need to be redirected to log in page
    if not check_logged_in():
        session['submit_run'] = True
        return redirect(url_for('login'))

    # check if any error messages have been added to session, if so that means
    # the user tred to submit run but failed so error message needs to be shown
    for error_message in error_message_dict.keys():
        if error_message in session:
            del session[error_message]
            error_message_dict[error_message] = True

    return render_template('submit_run_individual_level.html', levels=levels,
                           categories=categories, platforms=platforms,
                           logged_in=check_logged_in(),
                           verifier=check_verifier(),
                           error_message_dict=error_message_dict)


@app.route('/process_run_fullgame', methods=['GET', 'POST'])
def process_run_fullgame():
    """this route validates all the data that a user submited for a fullgame
    run before it gets added to the database, if the data doesn't meet the
    correct format or crieria then it doesnt get submitted and
    the user gets sent back to the submit run fullgame page"""

    valid_link_formats = ['youtube.com/watch?v=', 'youtube.com/embed/',
                          'twitch.tv/videos/', 'twitch.tv/channelname/video/',
                          'youtu.be/']

    # check that the link submitted meets the valid link formats, if it doesnt
    # meet any of them then go back to fullgame with error message in session
    link = request.form['submit_run_link']
    valid_link = False
    for format in valid_link_formats:
        if format in link:
            valid_link = True
    if not valid_link:
        session['submit_run_link_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    # check that category id submitted is in the list of all category ids,
    # if not go back to submit page and show error message
    category = request.form['submit_run_category_dropwdown']
    valid_category = False
    category_ids = run_query_select("""SELECT Fullgame_category.fullgame_category_id
                                    FROM Fullgame_category""", ())
    for i in category_ids:
        if category == i[0]:
            valid_category = True
    if not valid_category:
        session['submit_run_category_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    # check that platform id submitted is in the list of all platform ids,
    # if not go back to submit page and show error message
    platform = request.form['platforms']
    valid_platform = False
    platform_ids = run_query_select("SELECT platform_id FROM Platform", ())
    for i in platform_ids:
        if platform == i[0]:
            valid_platform = True
    if not valid_platform:
        session['submit_run_platform_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    # check that each value for the time
    # submitted meets the crietea it needs to, eg minutes less than 60
    time_hours = request.form['time-hours'] or '0'
    if not check_valid_time_hours(time_hours):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    time_seconds = request.form['time-seconds'] or '0'
    if not check_valid_time_seconds(time_seconds):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    time_minutes = request.form['time-minutes'] or '0'
    if not check_valid_time_minutes(time_minutes):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    time_milliseconds = request.form['time-milliseconds'] or '0'
    if not check_valid_time_milliseconds(time_milliseconds):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_fullgame'))

    # format the time string then convert it
    # to seconds before adding it into database
    time = time_hours + ':' + time_minutes + ':' + time_seconds + '.' + time_milliseconds
    time = convert_time_to_seconds(time)

    # get date submiteed and convert it to seconds
    today = datetime.date.today()
    date_submitted = int((today - start_date).total_seconds())

    # insert the run into database with verified as none and obsolete as none
    run_query_insert("""INSERT INTO Run (run_id, fullgame_category_id, il_id,
                     verifier_id, time, date_submitted, player_id, platform_id,
                     video_link, obsolete)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (generate_id(), category, None, None, time, date_submitted,
                      session['username'][1], platform, link, None))

    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/process_run_individual_level', methods=['GET', 'POST'])
def process_run_individual_level():
    """this route validates all the data that a user submited for a individual
    level run before it gets added to the database, if the data doesn't meet
    the correct format or crieria then it doesnt get submitted and
    the user gets sent back to the submit run individual level page"""

    # check that the link submitted meets the valid link formats, if it doesnt
    # meet any of them then go back to fullgame with error message in session
    link = request.form['submit_run_link']
    valid_link_formats = ['youtube.com/watch?v=', 'youtube.com/embed/',
                          'twitch.tv/videos/', 'twitch.tv/channelname/video/',
                          'youtu.be/']
    valid_link = False
    for format in valid_link_formats:
        if format in link:
            valid_link = True
    if not valid_link:
        session['submit_run_link_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # check that category id submitted is in the list of all category ids,
    # if not go back to submit page and show error message
    category = request.form['submit_run_category_dropwdown']
    valid_category = False
    category_ids = run_query_select("""SELECT IL_category.il_category_id
                                    FROM IL_category""", ())
    for i in category_ids:
        if category == i[0]:
            valid_category = True
    if not valid_category:
        session['submit_run_category_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # check that level id submitted is in the list of all level ids,
    # if not go back to submit page and show error message
    level = request.form['submit_run_level_dropwdown']
    valid_level = False
    level_ids = run_query_select("SELECT Level.level_id FROM Level", ())
    for i in level_ids:
        if level == i[0]:
            valid_level = True
    if not valid_level:
        session['submit_run_level_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # check if the level and category pair make a valid il, if
    # not then go back to submit run page and show error message
    level_category_pair = run_query_select("""SELECT il_id
                                           FROM Individual_level
                                           WHERE level_id = ?
                                           AND il_category_id = ?""",
                                           (level, category))
    if len(level_category_pair) == 0:
        session['submit_run_level_category_pair_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # check that platform id submitted is in the list of all platform ids,
    # if not go back to submit page and show error message
    platform = request.form['platforms']
    valid_platform = False
    platform_ids = run_query_select("""SELECT Platform.platform_id
                                    FROM Platform""", ())
    for i in platform_ids:
        if platform == i[0]:
            valid_platform = True
    if not valid_platform:
        session['submit_run_platform_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # check that each value for the time
    # submitted meets the crietea it needs to, eg minutes less than 60
    time_hours = request.form['time-hours'] or '0'
    if not check_valid_time_hours(time_hours):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    time_seconds = request.form['time-seconds'] or '0'
    if not check_valid_time_seconds(time_seconds):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    time_minutes = request.form['time-minutes'] or '0'
    if not check_valid_time_minutes(time_minutes):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    time_milliseconds = request.form['time-milliseconds'] or '0'
    if not check_valid_time_milliseconds(time_milliseconds):
        session['submit_run_time_invalid'] = True
        return redirect(url_for('submit_run_individual_level'))

    # format the time string then convert it
    # to seconds before adding it into database
    time = time_hours + ':' + time_minutes + ':' + time_seconds + '.' + time_milliseconds
    time = convert_time_to_seconds(time)

    # get date submiteed and convert it to seconds
    today = datetime.date.today()
    date_submitted = int((today - start_date).total_seconds())

    # insert the run into database with verified as none and obsolete as none
    run_query_insert("""INSERT INTO Run (run_id, fullgame_category_id, il_id,
                     verifier_id, time, date_submitted, player_id, platform_id,
                     video_link, obsolete)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (generate_id(), None, level_category_pair[0][0],
                      None, time, date_submitted,
                      session['username'][1], platform, link, None))
    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/verify_runs')
def verify_runs():
    """this route is the verify runs page, it is only used by verifiers
    to see all the runs that need to be verified, they can
    then click on any of them and check over them to verify them"""

    # get all the information about all the fullgame runs where
    # verifier id is None, aka not verified and sort by date submitted
    fullgame_runs = run_query_select("""SELECT Run.date_submitted, Run.run_id,
                                     Player.name, Run.time,
                                     Platform.platform_id,
                                     Fullgame_category.name FROM Run
                                     JOIN Player ON Run.player_id =
                                     Player.player_id
                                     JOIN Platform ON Run.platform_id =
                                     Platform.platform_id
                                     JOIN Fullgame_category ON
                                     Run.fullgame_category_id =
                                     Fullgame_category.fullgame_category_id
                                     WHERE Run.verifier_id IS NULL
                                     AND Run.il_id IS NULL
                                     ORDER BY Run.date_submitted DESC""", ())

    # get all the information about all the individual level runs where
    # verifier id is None, aka not verified, and sort by date submitted
    il_runs = run_query_select("""SELECT Run.date_submitted, Run.run_id,
                               Player.name, Run.time, Platform.platform_id,
                               Run.il_id FROM Run
                               JOIN Player ON Run.player_id = Player.player_id
                               JOIN Platform ON Run.platform_id =
                               Platform.platform_id
                               JOIN Individual_level ON Run.il_id =
                               Individual_level.il_id
                               WHERE Run.verifier_id IS NULL
                               AND Run.fullgame_category_id IS NULL
                               ORDER BY Run.date_submitted DESC""", ())

    # append 0 to all fullgame runs to show that they are fullgame
    for v, i in enumerate(fullgame_runs):
        fullgame_runs[v].append(0)

    # append the category and level to all il
    # runs and then apend 1 to show they are il runs
    for v, i in enumerate(il_runs):
        il_id = i[5]

        # get the category and level from the il id
        category_level = run_query_select("""SELECT Level.name,
                                          Il_category.name
                                          FROM Individual_level
                                          JOIN Level ON
                                          Individual_level.level_id =
                                          Level.level_id
                                          JOIN Il_category ON
                                          Individual_level.il_category_id =
                                          Il_category.il_category_id
                                          WHERE Individual_level.il_id =
                                          ?""", (il_id,))
        il_runs[v].append(category_level[0][0])
        il_runs[v].append(category_level[0][1])
        il_runs[v].append(1)

    # combine both lists
    runs = fullgame_runs + il_runs

    # sort the runs by oldest first so the oldest
    # runs get verified first, first in first out
    runs = sorted(runs, key=lambda x: x[0])

    # for each run convert time and date
    for v, i in enumerate(runs):
        runs[v][0] = seconds_since_1980_to_date(i[0])
        runs[v][3] = converttime(i[3])

    return render_template('verify_runs.html', runs=runs,
                           logged_in=check_logged_in(),
                           verifier=check_verifier())


@app.route('/verify_run',  methods=['GET', 'POST'])
def verify_run():
    """this route handles the back end of verifiyin a run,
    it changes the verifed status from pending to verified
    and it checks to see it this beats a previous pb, if
    so it changes the pb from obsolete = 0 to obsoltet = 1"""

    # get button information from verifying the run
    verify_deny = request.form['verify_deny']
    run_id = request.form['verify_run']

    # if the run was denied delete it from the database
    if verify_deny == 'deny':
        run_query_update("DELETE FROM Run WHERE run_id = ?", (run_id,))
        return redirect(url_for('verify_runs'))

    # if the run is an il run
    if run_query_select("""SELECT * FROM Run WHERE Run.run_id = ?
                        AND Run.il_id IS NOT NULL""", (run_id,)):

        # get run informaion
        il_id = run_query_select("""SELECT Run.il_id FROM Run
                                 WHERE Run.run_id = ?""", (run_id,))[0][0]
        player_id = run_query_select("""SELECT Run.player_id FROM Run
                                     WHERE Run.run_id = ?""", (run_id,))[0][0]
        run_time = run_query_select("""SELECT Run.time FROM Run
                                    WHERE Run.run_id = ?""", (run_id,))[0][0]
        pb = run_query_select("""SELECT Run.run_id, Run.time FROM Run
                              WHERE Run.il_id = ? AND Run.obsolete = 0
                              AND Run.player_id = ?""", (il_id, player_id))

        # if there was a previous pb and the new run is now faster than
        # it then change the pv to being obsolete and this
        # run wiil not be obsolete, if not the this run is obsolete
        obsolete = 1
        if pb:
            if run_time <= pb[0][1]:
                obsolete = 0
                run_query_update("""UPDATE Run SET obsolete = 1
                                 WHERE run_id = ?""", (pb[0][0],))
        else:
            obsolete = 0
    else:

        # if run was fullgame then get run information
        category_id = run_query_select("""SELECT Run.fullgame_category_id
                                       FROM Run WHERE
                                       Run.run_id = ?""", (run_id,))[0][0]
        player_id = run_query_select("""SELECT Run.player_id FROM Run
                                     WHERE Run.run_id = ?""", (run_id,))[0][0]
        run_time = run_query_select("""SELECT Run.time FROM Run
                                    WHERE Run.run_id = ?""", (run_id,))[0][0]
        pb = run_query_select("""SELECT Run.run_id, Run.time FROM Run
                              WHERE Run.fullgame_category_id = ?
                              AND Run.obsolete = 0
                              AND Run.player_id = ?""",
                              (category_id, player_id))

        # if there was a previous pb and the new run is now faster than
        # it then change the pv to being obsolete and this
        # run wiil not be obsolete, if not the this run is obsolete
        obsolete = 1
        if pb:
            if run_time <= pb[0][1]:
                obsolete = 0
                run_query_update("""UPDATE Run SET obsolete = 1
                                 WHERE run_id = ?""", (pb[0][0],))
        else:
            obsolete = 0

    # get verifier id
    verifier_id = run_query_select("""SELECT Verifier.verifier_id
                                   FROM Verifier WHERE Verifier.player_id = ?
                                   """, (session['username'][1],))[0][0]

    # update the run to being verified with the verifier
    # id and set it te either obsolete or not
    run_query_update("""UPDATE Run SET verifier_id = ?, obsolete = ?
                      WHERE run_id = ?""", (verifier_id, obsolete, run_id))

    return redirect(url_for('verify_runs'))


@app.route('/process_player_search', methods=['GET', 'POST'])
def process_player_search():
    """this route process the search that a user can do to search for
    a specufic player and either redirects to that player if a valid
    name is inouted or redirects to home page if invalid name submitted"""

    player_name = request.form['searchs']

    # get player id from player name because player
    # account fullgame page needs player id
    player_id = run_query_select("""SELECT Player.player_id FROM Player
                                 WHERE Player.name = ?""", (player_name,))

    # if player id exists then go to player account fullgame for that player
    if player_id:
        return redirect(url_for('player_account_fullgame',
                                player_id=player_id[0][0]))

    # else go to home page because player isn't real
    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.route('/delete_run', methods=['GET', 'POST'])
def delete_run():
    """this route deletes a run when sent here from the player account page"""

    # check was sent here properly
    if not request.method == 'POST':
        abort(404)

    #check if run id is a valid id
    run_id = request.form['delete_run']
    check_run_id = run_query_select("""SELECT Run.run_id FROM Run WHERE
                                    Run.run_id =?""", (run_id,))

    if not check_run_id:
        abort(404)

    player_id = run_query_select("""SELECT Run.player_id FROM Run
                                 WHERE Run.run_id = ?""", (run_id,))[0][0]

    run_query_update("DELETE FROM Run WHERE run_id = ?", (run_id,))

    # redirect to either fullgame or il based on where you came from
    page = request.form['page']

    if page == 'fullgame':
        return redirect(url_for('player_account_fullgame',
                        player_id=player_id))
    elif page == 'individual_level':
        return redirect(url_for('player_account_individual_level',
                        player_id=player_id))

    return redirect(url_for('leaderboard_fullgame',
                            category_id='30831e37', page='0'))


@app.errorhandler(404)
def page_not_found(i):
    """this route is the 404 page incase the user tries to break something"""

    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=False)
