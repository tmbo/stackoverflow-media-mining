# Stackoverflow bounty analysis
In this project we aim to analyze the influence of a bounty on a question. We will try to predict whether a question will receive a successful answer after setting a bounty for it or not. Additionally, we predict if this bounty question will receive its winning answer within 2.5 days after creation of the bounty.

The project consists of several parts:
 
1. Scripts (Python / SQL) to import the Stackoverflow dump into a HANA database. The SO dump, given as XML data will get evaluated and inserted into the DB. 
2. SQL scripts to calculate additional tables that provide easy access to deeper knowledge, e.g. about tags on a question. 
3. Code to calculated features and train a topic model (LDA) and a SVM, which will serve as the knowledge base for the web server.
4. A Web Server to enter questions and receive a prediction as output.

Content of the repository:

| Path                  |                                                                                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_cleansing/`     | SQL scripts to clean the SO dump from inconsistencies. Furthermore, create additional tables with condensed information.                                                |
| `data_converter/`     | Python scripts to read XML data dumps and yield them as batched rows.                                                                                                   |
| `data_crawling/`      | Scala script to request timestamps from the SO API that are not contained in the original data dump. The training process needs the data to be as accurate as possible. |
| `feature_analysis/`   | R scripts to analyze the data and generate plots.                                                                                                                       |
| `hana_nodejs_import/` | Deprecated HANA nodejs importer. This script got replaced by `insert_data`                                                                                              |
| `insert_data/`        | Python script to bulk write `INSERT` statements to HANA.                                                                                                                |
| `prediction/`         | Python code to calculate features, train topic models and train a SVM classifier                                                                                        |
| `web_server/`         | Python web server that uses a trained SVM to do live predictions.                                                                                                       |

## Setup and prediction Training

### 0. Requirements
Pre-Requirements that should be installed before running any installer / scripts:

   - java > 1.7
   - python >= 2.7
   - easy_install / pip for python
   - HANA server
   - LAPACK compatible OS
   
### 1. Installation
   
There is an installer script `install.sh` located in the root of the project. It will install all necessary python packages, sbt for scala and some needed system libraries. It is written to be executed on SUSE SE 11 but should be easily adoptable to other OS. 

System packages: 

    gcc-fortran, p7zip, lapack

Necessary python packages: 

    nltk, numpy, scipy, gensim, dateutil, scikit-learn, 
    flask, requests, ordereddict, flask-cors 

The python driver for HANA needs to be manually installed. Follow  [connect-to-sap-hana-in-python](http://scn.sap.com/community/developer-center/hana/blog/2014/05/02/connect-to-sap-hana-in-python) to do so.

### 2. Configuration
There are two configuration files, `application.cfg` and `stackoverflow_data.cfg`

| **application.cfg**        | **default**                       |                                            |
|----------------------------|-----------------------------------|--------------------------------------------|
| [DB]                       |                                   |                                            |
| user                       | root                              | User with access to the database           |
| password                   |                                   | Password of the DB user                    |
| host                       | localhost                         | Host address of the server running the DB  |
| port                       | 1337                              | Port of the running DB server              |
| typ                        | mysql                             | DB type, should be either `hana`or `mysql` |
| database                   | stackoverflow                     | Name of the database to work on            |
| &nbsp;                     |                                   |                                            |
| **stackoverflow_data.cfg** | **example**                       |                                            |
| [`<TABLENAME>`]            |                                   |                                            |
| input                      | Votes.xml                         | Name of the input XML file in the SO dump  |
| table                      | SO_VOTES                          | Name of the table in the DB                |
| columns                    | Id CreationDate PostId VoteTypeId | Columns to transfer from XML to DB         |
| timestamps                 | CreationDate                      | Columns that need timestamp reformatting   |

The `stackoverflow_data.cfg` should contain one section for each `<TABLENAME>` containing the attributes described above.

### 3. Getting the data
There is a script called `run.sh` this script will download the most recent stack overflow dump from the archive. After that the data will get unzipped and inserted int to the database. All scripts will use the `output/` directory as a working directory. Please make sure it is writable.

After insertion the runner will execute a crawler to download timestamps that are missing from the dump.

### 4. Cleansing of the data and table generation
There are multiple scripts in the folder `data_cleansing/`. Those need to be executed against the SO data that got inserted into the database. They should be executed in order of their prefixing indices. This will create additional tables like `SO_TAGS` containing all tags that got annotated at least once.

### 5. Feature calculation and model training
After you ran the data cleansing scripts you should execute `train.sh`. There are several python scripts that will be called. They are used to calculate various features needed to train the classifiers. All features are collected in the table `SO_TRAINING_FEATURES`.

At the end the script will train two topic models (one on the whole SO question corpus and another one on a smaller sample only using verb phrases `VP`). When the LDA's are trained the final training for the two SVMs is started.

## The Web Server
The project comes with a web server to enter questions and present the prediction results. The server can be used as is to show a simple HTML report or serves all its data via a REST interface.

### 0. Requirements
The Web Server relies on Flask Webframework and a number of other Python libraries. Running the `install.sh` script should install these.


The Web Server relies on four data sources for its calculations:
1. The Stackoverflow REST API (10000 requests / day quota)
2. A Database with X tables contaning pre-calculated statistics on tag usage.
3. Two trained SVM located under `output/svms`, one for the success prediction and one for time interval prediction.
4. Two trained LDAs located under `output/ldas`, one for a topic model trained on the whole dataset and one without verb phrases.

### 1. Launching the Server
Make sure the DB is up and running and the `application.cfg` is set up properly to allow access to the DB.

```sh
python server.py
```

### 2. Routes

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

### 3. Embedding into a different page
