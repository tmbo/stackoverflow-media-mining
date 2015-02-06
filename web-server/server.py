# System imports
import sys, os
import re
import random
from flask import *
from flask.json import jsonify
import requests

# Local predicition modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'prediction')) #find modules in parent_folder/predictions
import text_features
import tag_features
import comment_features
import bounty_features
from text_statistics import TextStatistics
from utils import *

app = Flask(__name__)
RE_QUESTIONID = re.compile("(\d+)")

prediction_dict = dict()

# ----- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submitQuestion", methods=["POST"])
def submitQuestion():
    question = request.form["question"]
    if question:
        regex_result = RE_QUESTIONID.search(question)
        if regex_result:
            question_id = regex_result.group()
            return redirect(url_for("rofl", question_id=question_id))

    flash("Unable to find this question.")
    return redirect(url_for("index"))


@app.route("/<int:question_id>")
def question_details_page(question_id):
    # Return an HTML Page listing all features and predicitions for a question
    stats = get_features(question_id)
    prediction = get_prediction(question_id)
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
    print
    return {
        "textFeatures": text_features.calculate_text_features(question["question_id"], question["body"], question["title"]),
        "tagFeatures": tag_features.calculate_tag_features(question["tags"]),
        "commentFeatures": comment_features.calculate_comment_features(comments),
        "shallowLinguisticFeatures": TextStatistics(remove_tags(remove_code(question["body"]))).calculate_shallow_text_features(),
        "bountyFeatures": bounty_features.calculate_bounty_features(question)
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

