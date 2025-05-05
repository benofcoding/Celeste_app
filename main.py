from flask import Flask, render_template, request
import sqlite3





app = Flask(__name__)

def run_query_select(query):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return rows

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/leaderboard_fullgame/<category_id>/<int:page>')
def leaderboard_fullgame(category_id, page):
    runs = run_query_select(f"SELECT Run.run_id, Run.run_id, Player.name, Player.player_id, Run.time, Run.video_link, Run.date_submitted, Platform.name FROM Run JOIN Player ON Run.player_id = Player.player_id JOIN Platform ON Run.platform_id = Platform.platform_id WHERE Fullgame_category_id = '{category_id}' AND Run.obsolete = 0 AND Run.verifier_id IS NOT NULL ORDER BY Run.time ASC LIMIT 100 OFFSET {page*100}")
    print(runs)
    return render_template('leaderboard_fullgame.html', runs=runs)











if __name__ == '__main__':
    app.run(debug=True)
