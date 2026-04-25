from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


#----------DATABASE---------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)''')
c.execute('''CREATE TABLE IF NOT EXISTS predictions ( id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    game TEXT,
    prediction TEXT,
    result TEXT,
    points INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

    init_db()

    #---------SAMPLE GAMES---------

games = [
    "Hawks vs Knicks",
    "Braves vs phillies",
    "Lakers vs Rockets",
    "Dodgers vs Giants"
]
#--------HOME---------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("home.html", user=session["user"], games=games)

#--------LOGIN---------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        conn = get_db()
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        except:
            pass
        conn.commit()
        conn.close()

        session["user"] = username
        return redirect("/")

    return render_template("login.html")

    #-------LOGOUT---------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


#--------MAKE PREDICTION---------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/login")

    game = request.form["game"]
    prediction = request.form["prediction"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO predictions (user, game, prediction) VALUES (?, ?, ?)", (session["user"], game, prediction))
    conn.commit()
    conn.close()

    return redirect("/")

    #--------SET RESULTS---------
@app.route("/set_results", methods=["GET","POST"])
def set_results():
    if request.method == "POST":
        game = request.form["game"]
        result = request.form["result"]

        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE predictions SET result = ? WHERE game = ?", (result, game))
        c.execute("SELECT id, prediction FROM predictions WHERE game = ?", (game,))
        rows = c.fetchall()

        for pid, pred in rows:
            points = 10 if pred.lower() == result.lower else 0
            c.execute("UPDATE predictions SET points = ? WHERE id = ?", (points, pid))
        conn.commit()
        conn.close()

        return redirect("/leaderboard")
    return render_template("set_results.html", games=games)

    #--------LEADERBOARD---------
@app.route("/leaderboard")
def leaderboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT user, SUM(points) as total
        FROM predictions
        GROUP BY user
        ORDER BY total DESC
        """)

        data = c.fetchall()
        conn.close()

        return render_template("leaderboard.html", data=data)

        #-------RUN APP---------
if __name__ == "__main__":
    app.run(debug=True)
    

      

