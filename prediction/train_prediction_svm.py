from sklearn import svm
from sklearn import cross_validation
import numpy as np
from sklearn import preprocessing
import numpy as np
from operator import itemgetter
from sklearn.externals import joblib
import time
from sklearn.metrics import f1_score, roc_auc_score, precision_recall_fscore_support
from sklearn.grid_search import GridSearchCV

name_of_feature_table = "training_features"
database_name = "stackoverflow"
user_name = "root"
password = ""
host = "127.0.0.1"

train_size = 20000
test_size = 1000

active_features = [
    'text',
    'tags',
    'comments',
    'linguistic',
    'bounty',
    'topic'
]

featuresets = {
    'text': [8, 9, 10, 11, 12, 13, 14, 15, 52, 53, 54, 55, 56],
    'tags': [16, 17, 18, 19, 20, 21, 22, 23, 24, 37, 38, 57, 58, 59, 60, 61, 62],
    'comments': [31, 32, 34, 70, 71],
    'linguistic': [46, 47, 48, 49, 50, 51, 63, 64, 65, 66, 67],
    'bounty': [25, 26, 27, 28, 29, 30, 33, 35, 36, 39, 68, 69, 72, 73],
    'topic': [40, 41, 42, 43, 44, 45]
}


# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
            score.mean_validation_score,
            np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")


def store_svm(clf, file_name):
    joblib.dump(clf, file_name)


def load_svm(file_name):
    return joblib.load(file_name)


def convert_date_to_timestamp(str):
    return time.mktime(str.timetuple())


def calculate_y(durationInMinutes):
    return 1 if durationInMinutes / 60 < (24 * 2.5) else 0


def load_data_from_db():
    import mysql.connector

    cnx = mysql.connector.connect(user=user_name, password=password,
                                  database=database_name,
                                  host=host)
    cursor = cnx.cursor()
    cursor.execute("Select * From %s Where (AnswerDate is not null Or successful = 0) and num_answers_bounty = 0" % name_of_feature_table)
    return cursor.fetchall()


def train_to_predict_finish(data):
    # Prediction of success event
    unscaled_X = extract_features(data)
    print "Working with %d features on %d examples. Enabled: %s" % (len(unscaled_X[0]), len(unscaled_X), active_features)
    y = labels_for_finish_prediction(data)

    clf = svm.SVC(verbose=True, kernel="rbf", C=32, gamma=0.0001220703125)  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=test_size,
                                                                                           train_size=train_size,
                                                                                           random_state=42)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training to estimate if bounty is going to finish using SVM on trainings data ..."
    clf.fit(X_train, y_train)

    # store_svm(clf, "output/test.pkl")

    prediction = clf.predict(X_test)
    precision, recall, fbeta, support = precision_recall_fscore_support(y_test, prediction)
    print "Scoring Finish-SVM on TEST data ..."
    print "Finish-Trainings Accuracy: %f precision: %s recall: %s F1-score: %s support: %s ROC: %f" % (
    clf.score(X_test, y_test), precision, recall, fbeta, support, roc_auc_score(y_test, prediction))

    # prediction_train = clf.predict(X_train)
    # print "Scoring Finish-SVM on TRAINING data ..."
    # print "Finish-Trainings Accuracy: %f F1-score: %f ROC: %f" % (
    # clf.score(X_train, y_train), f1_score(y_train, prediction_train), roc_auc_score(y_train, prediction_train))

    return clf


def train_to_predict_time(data):
    # Prediction of time event
    filtered_data = filter(lambda x: x[1] == 1, data)

    y = labels_for_time_prediction(filtered_data)
    unscaled_X = extract_features(filtered_data)

    print "Working with %d features on %d examples. Enabled: %s" % (len(unscaled_X[0]), len(unscaled_X), active_features)

    clf = svm.SVC(verbose=True, kernel="rbf", C=32, gamma=0.0001220703125)  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=test_size,
                                                                                           train_size=train_size,
                                                                                           random_state=42)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training SVM on trainings data to estimate answer time..."
    clf.fit(X_train, y_train)

    prediction = clf.predict(X_test)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Time-SVM on test data ..."
    print "Time-Trainings Accuracy: %f F1-score: %f ROC: %f" % (
    clf.score(X_test, y_test), f1_score(y_test, prediction), roc_auc_score(y_test, prediction))

    # prediction_train = clf.predict(X_train)
    # print "Scoring Time-SVM on TRAINING data ..."
    # print "Time-Trainings Accuracy: %f F1-score: %f ROC: %f" % (
    # clf.score(X_train, y_train), f1_score(y_train, prediction_train), roc_auc_score(y_train, prediction_train))
    return clf


def grid_train_to_predict_time(data):
    # Prediction of time event
    filtered_data = filter(lambda x: x[1] == 1, data)

    param_grid = [
        {'C': map(lambda x: pow(2, x), range(-5, 16, 2)), 'gamma': map(lambda x: pow(2, x), range(-15, 3, 2)),
         'kernel': ['rbf']}
    ]

    y = labels_for_time_prediction(filtered_data)
    unscaled_X = extract_features(filtered_data)

    clf = svm.SVC()  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=1000,
                                                                                           train_size=10000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training SVM on trainings data to estimate answer time..."
    grid_search = GridSearchCV(clf, param_grid=param_grid, refit=True, n_jobs=6, verbose=2)
    grid_search.fit(X_train, y_train)

    print("GridSearchCV for %d candidate parameter settings." % len(grid_search.grid_scores_))
    report(grid_search.grid_scores_)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Time-SVM on test data ..."
    print "Time-Trainings score: %f" % grid_search.score(X_test, y_test)  # f1_score(y_test, clf.predict(X_test))
    return clf

def array_from_sparse(els, size):
    r = [0.0] * size
    for idx, value in els:
        r[idx] = value
    return r


def extract_features(data):
    X = []

    actives = [c for active in active_features for c in featuresets[active]]

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        features = [x for idx, x in enumerate(row) if idx in actives]  # remove the first four elements from the column (id and dates)
        if 'topic' in active_features:
            topic_features = array_from_sparse(eval(str(row[-2])), 100)
            vp_topic_features = array_from_sparse(eval(str(row[-1])), 100)
            features.extend(topic_features)
            features.extend(vp_topic_features)
        X.append(features)
    return X


def labels_for_finish_prediction(data):
    y = []

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        y.append(row[1])
    return y


def labels_for_time_prediction(data):
    y = []

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        y.append(calculate_y(row[5]))
    return y


if __name__ == "__main__":
    print "Loading data from db ..."

    data = load_data_from_db()

    train_to_predict_finish(data)
    train_to_predict_time(data)
    #

    # grid_train_to_predict_time(data)
