from flask import * #Flask, render_template, request, flash, redirect
from flask.json import jsonify
import requests
import text_features as TextFeatures
import tag_features as TagFeatures
import re

app=Flask(__name__)
RE_QEUSTIONID = re.compile("(\d+)")

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
  stats = getMetadata(questionId)
  return render_template("details.html", stats=stats, questionId=questionId)


@app.route("/api/<int:questionId>")
def jsonMetadata(questionId):
  return jsonify(getMetadata(questionId))


# -------- Prediction & Features --------
def getMetadata(questionId):

  question, answers = queryStackoverflow(questionId)
  return calcFeatures(question)


# Fetch the question and answer from the SO API
def queryStackoverflow(questionId):

  questionRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s?site=stackoverflow&filter=withbody" % questionId)
  answersRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s/answers?site=stackoverflow" % questionId)

  question = questionRequest.json()["items"][0]
  answers = answersRequest.json()["items"]

  return question, answers


# Calculate all text, tag and XYZ features for the SVM
def calcFeatures(question):

  return {
    "textFeatures" : TextFeatures.calcTextFeatures(question["question_id"], question["body"], question["title"]),
    "tagFeatures" : TagFeatures.calcTagFeatures(question["question_id"], question["tags"])
  }


# do the prediction
def doSuccessPrediction():
  calcFeatures()
  return


if __name__ == "__main__":
  # Start the server
  app.config.update(
    DEBUG=True,
    SECRET_KEY="asassdfs"
  )
  app.run(port=9000)
  url_for('static', filename='style.css')
