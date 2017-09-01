from sklearn.datasets import fetch_mldata
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
from sklearn.neural_network import MLPClassifier

def learn():
    mnist = fetch_mldata("MNIST original")

    X, y = mnist.data / 255., mnist.target
    list_hog_fd = []
    for feature in X:
        fd = hog(feature.reshape((28, 28)), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                 visualise=False)
        list_hog_fd.append(fd)
    hog_features = np.array(list_hog_fd, 'float64')

    X = hog_features

    X_train = X[0:60000]
    X_test = X[60000:len(X)]
    y_train = y[0:60000]
    y_test = y[60000:len(y)]

    print(X_train.shape, ",", X_test.shape)

    mlp = MLPClassifier(hidden_layer_sizes=(100, 150), max_iter=300, alpha=1e-2,
                             solver='sgd', verbose=1, tol=1e-4, random_state=1,
                             learning_rate_init=.1, shuffle=True)

    mlp.fit(X_train, y_train)
    joblib.dump(mlp, "digits_cls_with_hog.pkl", compress=3)
    print("Training set score: %f" % mlp.score(X_train, y_train))
    print("Test set score: %f" % mlp.score(X_test, y_test))


if __name__ == "__main__":
    learn()
