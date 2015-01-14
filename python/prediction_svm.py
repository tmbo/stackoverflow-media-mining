from sklearn import svm
from sklearn import cross_validation
import numpy as np
from sklearn import preprocessing
import numpy as np
from sklearn.externals import joblib
import time
from sklearn.metrics import f1_score

name_of_feature_table = "training_features"
database_name = "stackoverflow"
user_name = "root"
password = "password"
host = "192.168.2.100"


def store_svm(clf, file_name):
    joblib.dump(clf, file_name)


def load_svm(file_name):
    return joblib.load(file_name)


def convert_date_to_timestamp(str):
    return time.mktime(str.timetuple())


def calculate_y(start_date_str, end_date_str):
    start_date = convert_date_to_timestamp(start_date_str)
    end_date = convert_date_to_timestamp(end_date_str)
    return 1 if int(end_date - start_date) / 60 / 60 < (24 * 6.5) else 0


def load_data_from_db():
    import mysql.connector

    cnx = mysql.connector.connect(user=user_name, password=password,
                                  database=database_name,
                                  host=host)
    cursor = cnx.cursor()
    cursor.execute("Select * From %s" % name_of_feature_table)
    return cursor.fetchall()


def train_to_predict_finish(data):
    # Prediction of success event
    unscaled_X = extract_features(data)
    y = labels_for_finish_prediction(data)

    clf = svm.SVC()  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=2000,
                                                                                           train_size=20000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training to estimate if bounty is going to finish using SVM on trainings data ..."
    clf.fit(X_train, y_train)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Finish-SVM on test data ..."
    print "Finish-Trainings score: %f" % clf.score(X_test, y_test)  # f1_score(y_test, clf.predict(X_test))
    return clf


def train_to_predict_time(data):
    # Prediction of time event
    filtered_data = filter(lambda x: x[1] == 1, data)

    y = labels_for_time_prediction(filtered_data)
    unscaled_X = extract_features(filtered_data)

    clf = svm.SVC()  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=2000,
                                                                                           train_size=20000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training SVM on trainings data to estimate answer time..."
    clf.fit(X_train, y_train)

    # store_svm(clf, "output/test.pkl")

    print "Scoring Time-SVM on test data ..."
    print "Time-Trainings score: %f" % clf.score(X_test, y_test)  # f1_score(y_test, clf.predict(X_test))
    return clf


def extract_features(data):
    X = []

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        X.append([x for idx, x in enumerate(row) if
                  idx > 3])  # remove the first three elements from the column (id and dates)
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
        y.append(calculate_y(row[2], row[3]))
    return y


if __name__ == "__main__":
    print "Loading data from db ..."

    data = load_data_from_db()

    train_to_predict_time(data)

    train_to_predict_finish(data)
