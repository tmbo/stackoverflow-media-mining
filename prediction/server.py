from flask import * #Flask, render_template, request, flash, redirect
from flask.json import jsonify
import requests
import text_features as TextFeatures
import tag_features as TagFeatures
import comment_features as CommentFeatures
import re
import random

app=Flask(__name__)
RE_QEUSTIONID = re.compile("(\d+)")

predictionDict = {}

# ----- Routes ----------

@app.route("/")
def index():
  return render_template("index.html")


@app.route("/submitQuestion", methods=["POST"])
def submitQuestion():
  question = request.form["question"]
  if question:
    questionId = RE_QEUSTIONID.search(question).group()
    return redirect(url_for("questionDetailsPage", questionId=questionId))
  else:
    flash("Unable to find this question.")
    return redirect(url_for("index"))


@app.route("/<int:questionId>")
def questionDetailsPage(questionId):
  # Return an HTML Page listing all features and predicitions for a question
  stats = getFeatures(questionId)
  prediction = getPrediction(questionId)
  print prediction
  return render_template("details.html", stats=stats, questionId=questionId, prediction=prediction)


@app.route("/api/features/<int:questionId>")
def jsonFeatures(questionId):
  return jsonify(getFeatures(questionId))


@app.route("/api/predictions/<int:questionId>")
def jsonPrediction(questionId):
  return jsonify(getPrediction(questionId))


# -------- Prediction & Features --------
def getFeatures(questionId):

  question, answers, comments = queryStackoverflow(questionId)
  return calcFeatures(question, comments)


# Fetch the question and answer from the SO API
def queryStackoverflow(questionId):

  questionRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s?site=stackoverflow&filter=withbody" % questionId)
  answersRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s/answers?site=stackoverflow" % questionId)
  commentRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s/comments?site=stackoverflow&filter=withbody" % questionId)

  question = questionRequest.json()["items"][0]
  answers = answersRequest.json()["items"]
  comments = commentRequest.json()["items"]

  return question, answers, comments


# Calculate all text, tag and XYZ features for the SVM
def calcFeatures(question, comments):

  return {
    "textFeatures" : TextFeatures.calcTextFeatures(question["question_id"], question["body"], question["title"]),
    "tagFeatures" : TagFeatures.calcTagFeatures(question["tags"]),
    "commentFeatures" : CommentFeatures.calcCommentFeatures(comments)
  }


def getPrediction(questionId):

  if questionId in predictionDict:
    print predictionDict
    print "I was here "
    return predictionDict[questionId]
  else:
    predictionDict[questionId] = {
      "success" : random.choice([True, False]),
      "withinTimeInterval" : random.choice([True, False])
    }
    return predictionDict[questionId]


if __name__ == "__main__":
  # Start the server
  app.config.update(
    DEBUG=True,
    SECRET_KEY="asassdfs"
  )
  app.run(port=9000)
  url_for('static', filename='style.css')
