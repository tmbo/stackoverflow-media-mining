from flask import *
from flask.json import jsonify
import requests
import text_features
import tag_features
import comment_features
from text_statistics import TextStatistics
import bounty_features
from utils import *
import re
import random

app = Flask(__name__)
RE_QUESTIONID = re.compile("(\d+)")

prediction_dict = dict()

# ----- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submitQuestion", methods=["POST"])
def submit_question():
    question = request.form["question"]
    if question:
        question_id = RE_QUESTIONID.search(question).group()
        return redirect(url_for("questionDetailsPage", questionId=question_id))
    else:
        flash("Unable to find this question.")
        return redirect(url_for("index"))


@app.route("/<int:question_id>")
def question_details_page(question_id):
    # Return an HTML Page listing all features and predicitions for a question
    stats = get_features(question_id)
    prediction = get_prediction(question_id)
    print prediction
    return render_template("details.html", stats=stats, questionId=question_id, prediction=prediction)


@app.route("/api/features/<int:question_id>")
def json_features(question_id):
    return jsonify(get_features(question_id))


@app.route("/api/predictions/<int:question_id>")
def json_prediction(question_id):
    return jsonify(get_prediction(question_id))


# -------- Prediction & Features --------
def get_features(question_id):
    question, answers, comments = query_stackoverflow(question_id)
    return calculate_features(question, comments)


# Fetch the question and answer from the SO API
def query_stackoverflow(question_id):
    question_request = requests.get(
        "https://api.stackexchange.com/2.2/questions/%s?site=stackoverflow&filter=withbody" % question_id)
    answers_request = requests.get(
        "https://api.stackexchange.com/2.2/questions/%s/answers?site=stackoverflow" % question_id)
    comment_request = requests.get(
        "https://api.stackexchange.com/2.2/questions/%s/comments?site=stackoverflow&filter=withbody" % question_id)

    question = question_request.json()["items"][0]
    answers = answers_request.json()["items"]
    comments = comment_request.json()["items"]

    return question, answers, comments


# Calculate all text, tag and XYZ features for the SVM
def calculate_features(question, comments):
    text = remove_tags(remove_code(question["body"]))

    return {
        "textFeatures": text_features.calcTextFeatures(question["question_id"], question["body"], question["title"]),
        "tagFeatures": tag_features.calcTagFeatures(question["tags"]),
        "commentFeatures": comment_features.calcCommentFeatures(comments),
        "shallowLinguisticFeatures": TextStatistics(text).calcShallowTextFeatures(),
        "bountyFeatures": bounty_features.calcBountyFeatures(question)
    }


def get_prediction(question_id):
    if question_id in prediction_dict:
        return prediction_dict[question_id]
    else:
        prediction_dict[question_id] = {
            "success": random.choice([True, False]),
            "withinTimeInterval": random.choice([True, False])
        }
        return prediction_dict[question_id]


if __name__ == "__main__":
    # Start the server
    app.config.update(
        DEBUG=True,
        SECRET_KEY="asassdfs"
    )
    app.run(port=9000)
    url_for('static/img', filename="apple-touch-icon.png")
