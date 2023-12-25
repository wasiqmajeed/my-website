from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from questions import Questions
import os
import gunicorn

questions = Questions().questions
name_user = None
print(gunicorn.__version__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///score-count.db")
db = SQLAlchemy()
db.init_app(app)


class Score(db.Model):
    rank = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=True)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/aboutme')
def about_me():
    return render_template("about-me.html")


@app.route('/education')
def education():
    return render_template('my-education.html')


@app.route('/details', methods=["GET","POST"])
def enter_details():

    return render_template("user-details.html")


@app.route('/quiz', methods=["GET", "POST"])
def quiz():
    global name_user
    user_name = request.form.get("name")
    name_user = user_name
    if request.method == "POST":
        user_details = Score(
            name=request.form.get("name"),
            age=request.form.get("age"),
            score=0
        )
        db.session.add(user_details)
        db.session.commit()
    return render_template("quiz.html", question=questions)


@app.route('/result', methods=['GET','POST',"PATCH"])
def user_result():
    k_score = 0
    global name_user
    for idx in range(len(questions)):
        count = "count" + str(idx + 1)
        if request.form.get(count) == questions[idx]["answer"]:
            k_score += 1
    score_to_update = db.session.execute(db.select(Score).where(Score.name == name_user)).scalar()
    score_to_update.score = k_score
    db.session.commit()

    return render_template("results.html", score=k_score)

if __name__ == "__main__":
    app.run(debug=True)