from sklearn import svm
from sklearn import cross_validation
from sklearn import preprocessing
import numpy as np
from operator import itemgetter
from sklearn.externals import joblib
import time
from sklearn.metrics import f1_score, roc_auc_score, precision_recall_fscore_support
from sklearn.grid_search import GridSearchCV
from database import Database
from utils import array_from_sparse, ensure_folder_exists

# Name of the table to grab the data from
name_of_feature_table = "SO_TRAINING_FEATURES"

# Number of entries used for training and testing for both models
train_size = 40000
test_size = 3000

# Decision boundary for time training SVM. Value in hours
time_y_limit = (24 * 2.5)

# Only features categories listed here will be used for training
active_features = [
    # 'text',
    # 'tags',
    # 'comments',
    # 'linguistic',
    # 'bounty',
    'topic'
]

# Mapping of feature categories to the individual columns
featuresets = {
    'text': [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    'tags': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
    'bounty': [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
    'comments': [49, 50, 51, 52, 53],
    'linguistic': [54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
    'topic': []
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


# Save a trained model to file. WARNING: If the source code of the model changes
# loading will not work since this uses PICKEL.
def store_trained_instance(clf, file_name):
    joblib.dump(clf, file_name)


# Restore a trained instance from file
def load_trained_instance(file_name):
    return joblib.load(file_name)


# Convert a date to a timestamp
def convert_date_to_timestamp(str):
    return time.mktime(str.timetuple())

# Calculate Y labels for annotated training. 
def calculate_y_label(duration_in_minutes):
    return 1 if duration_in_minutes / 60 < time_y_limit else 0


# Load the data for training from the DB
def load_data_from_db():
    database = Database.from_config()
    con, cursor = database.cursor()
    cursor.execute(
        "Select * From %s Where AnswerDate is not null Or successful = 0" % name_of_feature_table)
    results = cursor.fetchall()
    con.close()
    return results


# Train an SVM instance on data. Returning the svm and a fitted scaler.
def train_svm(unscaled_X, y, name, expl=""):
    print "Working with %d features on %d examples. Enabled: %s" % (
    len(unscaled_X[0]), len(unscaled_X), active_features)

    clf = svm.SVC(verbose=True, kernel="rbf", C=32, gamma=0.0001220703125)  # probability = True)

    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=test_size,
                                                                                           train_size=train_size,
                                                                                           random_state=42)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Training to %s" % expl
    clf.fit(X_train, y_train)

    prediction = clf.predict(X_test)
    precision, recall, fbeta, support = precision_recall_fscore_support(y_test, prediction)
    print "Scoring Finish-SVM on TEST data ..."
    print "%s-Trainings Accuracy: %f precision: %s recall: %s F1-score: %s support: %s ROC: %f F1: %f" % (
        name, clf.score(X_test, y_test), precision, recall, fbeta, support, roc_auc_score(y_test, prediction), f1_score(y_test, prediction))

    return clf, scaler


# Train a SVM to predict the success of a bounty
def train_to_predict_success(data):
    X = extract_features(data)
    y = labels_for_success_prediction(data)
    return train_svm(X, y, "SUCCESS", "estimate if bounty is going to succeed using SVM on trainings data ...")


# Train a SVM to predict if a bounty will be sucessfull in a given time span (time_y_limit)
def train_to_predict_time(data):
    X = extract_features(data)
    y = labels_for_time_prediction(data)
    return train_svm(X, y, "TIME", "estimate answer time ...")


# Used for hyperparameter optimization. The parameters that work best should be used to train the final classifier
def grid_train_to_predict_time(unscaled_X, y, name):
    # Hyperparameters to optimize for
    param_grid = [
        {'C': map(lambda x: pow(2, x), range(-5, 16, 2)), 'gamma': map(lambda x: pow(2, x), range(-15, 3, 2)),
         'kernel': ['rbf']}
    ]

    clf = svm.SVC()  # probability = True)
    X_train_unscaled, X_test_unscaled, y_train, y_test = cross_validation.train_test_split(unscaled_X, y,
                                                                                           test_size=1000,
                                                                                           train_size=10000,
                                                                                           random_state=0)

    scaler = preprocessing.StandardScaler().fit(X_train_unscaled)

    X_train = scaler.transform(X_train_unscaled)
    X_test = scaler.transform(X_test_unscaled)

    print "Testing hyperparameters for %s-SVM ..." % name
    grid_search = GridSearchCV(clf, param_grid=param_grid, refit=True, n_jobs=6, verbose=2)
    grid_search.fit(X_train, y_train)

    print("GridSearchCV for %d candidate parameter settings." % len(grid_search.grid_scores_))
    report(grid_search.grid_scores_)

    print "Scoring %s-SVM on test data ..." % name
    print "%s-SVM score: %f" % (name, grid_search.score(X_test, y_test))
    return clf, scaler


# Bring the data from DB into a format suitable for SVM training
def extract_features(data):
    X = []

    actives = [c for active in active_features for c in featuresets[active]]

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate, feature1, feature2, feature3, ...
    for row in data:
        # Only use activated feature categories
        features = [x for idx, x in enumerate(row) if
                    idx in actives]  
        # If the topic feature categorie is activated we need to reconstruct an array
        # from the sparse values we get out of the DB
        if 'topic' in active_features:
            topic_features = array_from_sparse(eval(str(row[-2])), 150)
            vp_topic_features = array_from_sparse(eval(str(row[-1])), 100)
            features.extend(topic_features)
            features.extend(vp_topic_features)
        X.append(features)
    return X


# Calculate Y labels for SUCCESS prediction
def labels_for_success_prediction(data):
    y = []

    # Drop the Id field and the y value. This assumes a row looks like this: Id, Finished, StartDate, EndDate ...
    for row in data:
        y.append(row[1])
    return y


# Calculate Y labels for TIME prediction
def labels_for_time_prediction(data):
    y = []

    for row in data:
        y.append(calculate_y_label(row[5]))
    return y


# Run the training and store the results on disk for later usage
if __name__ == "__main__":
    print "Loading data from db ..."

    base_dir = "output/svms"

    ensure_folder_exists(base_dir)

    data = load_data_from_db()

    success_svm, success_scaler = train_to_predict_success(data)
    time_svm, time_scaler = train_to_predict_time(filter(lambda x: x[1] == 1, data))

    store_trained_instance(success_svm, base_dir + "/success_svm.pkl")
    store_trained_instance(success_scaler, base_dir + "/success_scaler.pkl")

    store_trained_instance(time_svm, base_dir + "/time_svm.pkl")
    store_trained_instance(time_scaler, base_dir + "/time_scaler.pkl")

    # grid_train_to_predict_time(data)
