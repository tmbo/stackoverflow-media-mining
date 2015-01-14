import cherrypy
from cherrypy import NotFound
import requests
import text_features as TextFeatures
import tag_features as TagFeatures

class SimpleREST(object):
  exposed = True

  @cherrypy.tools.accept(media="text/plain")
  @cherrypy.tools.json_out()
  def GET(self, questionId):

    questionRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s?site=stackoverflow&filter=withbody" % questionId)
    answersRequest = requests.get("https://api.stackexchange.com/2.2/questions/%s/answers?site=stackoverflow" % questionId)

    question = questionRequest.json()["items"][0]
    answers = answersRequest.json()["items"]

    features = dict(
      TextFeatures.calcTextFeatures(question["question_id"], question["body"], question["title"]),
      **TagFeatures.calcTagFeatures(question["question_id"], question["tags"])
    )

    return features

  def POST(self):
    raise NotFound()

  def PUT(self):
    raise NotFound()

  def DELETE(self):
    raise NotFound()


if __name__ == "__main__":
  conf = {
    "global" : {
      "server.socket_port": 9000
    },
    "/": {
      "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
      "tools.sessions.on": True,
      "tools.response_headers.on": True,
      "tools.response_headers.headers": [("Content-Type", "text/json")],
    }
  }

  cherrypy.quickstart(SimpleREST(), "/", conf)