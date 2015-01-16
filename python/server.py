from flask import Flask
from flask import render_template
from flask.json import jsonify
import requests
import text_features as TextFeatures
import tag_features as TagFeatures

app=Flask(__name__)


@app.route("/")
def index():
  return "LOL"


@app.route("/api/<int:questionId>")
def getMetadata(questionId):

  questionRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s?site=stackoverflow&filter=withbody" % questionId)
  answersRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s/answers?site=stackoverflow" % questionId)

  question = questionRequest.json()["items"][0]
  answers = answersRequest.json()["items"]

  features = jsonify(
    TextFeatures.calcTextFeatures(question["question_id"], question["body"], question["title"]),
    **TagFeatures.calcTagFeatures(question["question_id"], question["tags"])
  )

  return features


if __name__ == "__main__":

  app.run(port=9000, debug=True)
