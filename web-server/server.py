# System imports
import sys, os, re, requests
from flask import *
from flask.json import jsonify
from ordereddict import OrderedDict


# Local predicition modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'prediction')) #find modules in parent_folder/predictions
import text_features
import tag_features
import comment_features
import bounty_features
from sklearn.externals import joblib
from extended_text_features import TopicModel
from text_statistics import TextStatistics
from utils import *

app = Flask(__name__)
RE_QUESTIONID = re.compile("(\d+)")


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
            return redirect(url_for("question_details_page", question_id=question_id))

    flash("Unable to find this question.")
    return redirect(url_for("index"))


@app.route("/<int:question_id>")
def question_details_page(question_id):
    # Return an HTML Page listing all features and predicitions for a question
    features = get_features(question_id)
    prediction = get_prediction(features)
    return render_template("details.html", features=features, questionId=question_id, prediction=prediction)


@app.route("/api/features/<int:question_id>")
def json_features(question_id):
    return jsonify(get_features(question_id))


@app.route("/api/predictions/<int:question_id>")
def json_prediction(question_id):
    features = get_features(question_id)
    prediction = get_prediction(features)
    print prediction
    return jsonify(prediction)


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
    processed_body = remove_tags(remove_code(question["body"]))

    features = OrderedDict()
    features["textFeatures"] = text_features.calculate_text_features(question["question_id"], question["body"], question["title"])
    features["tagFeatures"] = tag_features.calculate_tag_features(question["tags"])
    features["bountyFeatures"] = bounty_features.calculate_bounty_features(question)
    features["commentFeatures"] = comment_features.calculate_comment_features(comments)
    features["shallowLinguisticFeatures"] = TextStatistics(processed_body).calculate_shallow_text_features()
    features["topicWholeFeatures"] = {
        "topics" : array_from_sparse(topic_model.predict_whole_topics(processed_body.lower()), 150)
    }
    features["topicVPFeatures"] = {
        "topics" : array_from_sparse(topic_model.predict_vp_topics(processed_body.lower()), 100)
    }

    return features


def get_prediction(features):

    i = 0
    for category, feature in features.items():
        for value in feature.values():
            if isinstance(value, list):
                values.extend(value) # arrays
            else:
                values.append(value) # single Integers, Floats
            i+= 1

    X_success = success_scaler.transform(values)
    X_time = time_scaler.transform(values)

    return {
        "success" : success_svm.predict(X_success)[0],
        "time" : time_svm.predict(X_time)[0]
    }


if __name__ == "__main__":
    # Start the server
    app.config.update(
        DEBUG=True,
        SECRET_KEY="asassdfs"
    )

    # Load LDA Topic Model from Disk and train chunker
    topic_model = TopicModel()

    # Load the trained SVM from disk
    svm_dir = os.path.dirname(os.path.realpath(__file__))
    svm_dir = os.path.join(svm_dir, "..", "output", "svms")

    success_svm = joblib.load(os.path.join(svm_dir, "success_svm.pkl"))
    success_scaler = joblib.load(os.path.join(svm_dir, "success_scaler.pkl"))

    time_svm = joblib.load(os.path.join(svm_dir, "time_svm.pkl"))
    time_scaler = joblib.load(os.path.join(svm_dir, "time_scaler.pkl"))

    # Start the Flask app
    app.run(port=9000)


