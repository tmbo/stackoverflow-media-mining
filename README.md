# Stackoverflow bounty analysis
In this project we aim to analyse the influence of a bounty on a question. We will try to predict whether a question will receive a successful answer if setting a bounty for it. Additionally we predict if this bounty question will receive its winning answer with 2.5 days.

The project contains two parts:
1. A number of scripts to calculated features and train an SVM, which will serve as the knowledge base for the web server.
2. A Web Server to enter questions and receive a prediction as output.

## The Web Server
The project comes with a web server to enter questions and present the prediction results. The server can be used as is to show a simple HTML report or serves all its data via a REST interface.

### Requirements
The Web Server relies on Flask Webframework and a number of other Python libraries. Running the `install.sh` script should install these.


The Web Server relies on four data sources for its calculations:
1. The Stackoverflow REST API (10000 requests / day quota)
2. A Database with X tables contaning pre-calculated statistics on tag usage.
3. Two trained SVM located under `output/svms`, one for the success prediction and one for time interval prediction.
4. Two trained LDAs located under `output/ldas`, one for a topic model trained on the whole dataset and one without verb phrases.

### Launching the Server
Make sure the DB is up and running and the `application.cfg` is set up properly to allow access to the DB.

```sh
python server.py
```

### Routes

The Web Server supports multiple Routes:

HTML Results
```
GET /                 index
GET /:quesiton_id     prediction result & detailed feature report for a SO question
POST /submitQuestion  needs field `question` with a question id
```

REST API
```
/api/predicitons/:question_id     returns only the predicition results as JSON
/api/features/:question_id        returns only the features as JSON
```

### Embedding into a different page
