from sklearn import svm
from sklearn import cross_validation
import numpy as np
from sklearn import preprocessing
import numpy as np
from operator import itemgetter
from sklearn.externals import joblib
import time
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.grid_search import GridSearchCV

name_of_feature_table = "training_features"
database_name = "stackoverflow"
user_name = "root"
password = ""
host = "127.0.0.1"

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
    cursor.execute("Select * From %s Where AnswerDate is not null Or successful = 0" % name_of_feature_table)
    return cursor.fetchall()


def train_to_predict_finish(data):
    # Prediction of success event
    unscaled_X = extract_features(data)
    y = labels_for_finish_prediction(data)

    clf = svm.SVC()  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=1000,
                                                                                           train_size=20000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training to estimate if bounty is going to finish using SVM on trainings data ..."
    clf.fit(X_train, y_train)

    # store_svm(clf, "output/test.pkl")

    prediction = clf.predict(X_test)
    print "Scoring Finish-SVM on TEST data ..."
    print "Finish-Trainings Accuracy: %f F1-score: %f ROC: %f" % (clf.score(X_test, y_test), f1_score(y_test, prediction), roc_auc_score(y_test, prediction))

    prediction_train = clf.predict(X_train)
    print "Scoring Finish-SVM on TRAINING data ..."
    print "Finish-Trainings Accuracy: %f F1-score: %f ROC: %f" % (clf.score(X_train, y_train), f1_score(y_train, prediction_train), roc_auc_score(y_train, prediction_train))

    return clf


def grid_train_to_predict_time(data):
    # Prediction of time event
    filtered_data = filter(lambda x: x[1] == 1, data)

    param_grid = [
        {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
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
    grid_search = GridSearchCV(clf, param_grid=param_grid, refit=True, n_jobs=4)
    grid_search.fit(X_train, y_train)

    print("GridSearchCV for %d candidate parameter settings." % len(grid_search.grid_scores_))
    report(grid_search.grid_scores_)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Time-SVM on test data ..."
    print "Time-Trainings score: %f" % grid_search.score(X_test, y_test)  # f1_score(y_test, clf.predict(X_test))
    return clf


def train_to_predict_time(data):
    # Prediction of time event
    filtered_data = filter(lambda x: x[1] == 1, data)

    y = labels_for_time_prediction(filtered_data)
    unscaled_X = extract_features(filtered_data)

    clf = svm.SVC()  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=1000,
                                                                                           train_size=20000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training SVM on trainings data to estimate answer time..."
    clf.fit(X_train, y_train)

    prediction = clf.predict(X_test)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Time-SVM on test data ..."
    print "Time-Trainings Accuracy: %f F1-score: %f ROC: %f" % (clf.score(X_test, y_test), f1_score(y_test, prediction), roc_auc_score(y_test, prediction))

    prediction_train = clf.predict(X_train)
    print "Scoring Finish-SVM on TRAINING data ..."
    print "Finish-Trainings Accuracy: %f F1-score: %f ROC: %f" % (clf.score(X_train, y_train), f1_score(y_train, prediction_train), roc_auc_score(y_train, prediction_train))
    return clf

def extract_features(data):
    X = []

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        X.append([x for idx, x in enumerate(row) if
                  idx > 6])  # remove the first four elements from the column (id and dates)
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

    # train_to_predict_time(data)
    #
    # train_to_predict_finish(data)

    grid_train_to_predict_time(data)
