# Task - copy SoftSVM module

from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

class SoftSVM(BaseEstimator, ClassifierMixin):
    """
    Custom C-Support Vector Classification.
    """
    def __init__(self, C: float, lr: float = 1e-5, batch_size = 32):
        """
        Initialize an instance of this class.
        ** Do not edit this method **

        :param C: inverse strength of regularization. Must be strictly positive.
        :param lr: the SGD learning rate (step size)
        """
        self.C = C
        self.lr = lr
        self.batch_size = batch_size
        self.w = None
        self.b = 0.0

    # Initialize a random weight vector
    def init_solution(self, n_features: int):
        """
        Randomize an initial solution (weight vector)
        ** Do not edit this method **

        :param n_features:
        """
        self.w = np.random.randn(n_features)
        self.b = 0.0

    @staticmethod
    def loss(w, b: float, C: float, X, y):
        y = y.values
        X = X.values
        """
        Compute the SVM objective loss.

        :param w: weight vector for linear classification; array of shape (n_features,)
        :param b: bias scalar for linear classification
        :param C: inverse strength of regularization. Must be strictly positive.
        :param X: samples for loss computation; array of shape (n_samples, n_features)
        :param y: targets for loss computation; array of shape (n_samples,)
        :return: the Soft SVM objective loss (float scalar)
        """
        # margins = { (w^T)(x_i)+b | x_i in X )
        margins = (X.dot(w) + b).reshape(-1, 1)
        # hinge_inputs = { (y_i)[(w^T)(x_i)+b] | x_i in X, y_i in y  }
        hinge_inputs = np.multiply(margins, y.reshape(-1, 1))
        # hinge_losses = max{0, 1-hinge_inputs} ={ max{0, 1 - (y_i)[(w^T)(x_i)+b]} | x_i in X, y_i in y  } }
        hinge_losses = np.maximum(0, 1-hinge_inputs)

        hinge_losses_sum = np.sum(hinge_losses)

        norm = np.linalg.norm(w)

        # TODO: complete the loss calculation, and return it
        loss = norm**2 + C*hinge_losses_sum
        return loss

    def f(num):
         return -1 if num < 1 else 0

    @staticmethod
    def subgradient(w, b: float, C: float, X, y):
        y = y.values
        X = X.values
        """
        Compute the (analytical) SVM objective sub-gradient.

        :param w: weight vector for linear classification; array of shape (n_features,)
        :param b: bias scalar for linear classification
        :param C: inverse strength of regularization. Must be strictly positive.
        :param X: samples for loss computation; array of shape (n_samples, n_features)
        :param y: targets for loss computation; array of shape (n_samples,)
        :return: a tuple with (the gradient of the weights, the gradient of the bias)
        """
        # TODO: calculate the analytical sub-gradient of soft-SVM w.r.t w and b

        # Calculate common element: f((y_i)[(w^T)(x_i)+b]) * (y_i):
        # margins = { (w^T)(x_i)+b | x_i in X )
        margins = (X.dot(w) + b).reshape(-1, 1)
        # hinge_inputs = { (y_i)[(w^T)(x_i)+b] | x_i in X, y_i in y  }
        hinge_inputs = np.multiply(margins, y.reshape(-1, 1))
        # Make the f function vectorwise
        vectorized_f = np.vectorize(SoftSVM.f)
        # Apply f to the hinge inputs.
        # hinge_inputs = { f((y_i)[(w^T)(x_i)+b]) | x_i in X, y_i in y  }
        hinge_inputs = vectorized_f(hinge_inputs)
        # Multiply each element by y_i and get the commong elements of the form: f((y_i)[(w^T)(x_i)+b]) * (y_i)
        common_factors = np.multiply(hinge_inputs, y.reshape(-1, 1))

        # Calculate analytical sub-gradient w.r.t w:
        g_w = 2*w + C*np.sum(common_factors * X, axis=0)

        # Calculate analytical sub-gradient w.r.t b:
        g_b = C*np.sum(common_factors, axis=0)

        return g_w, g_b

    def fit_with_logs(self, X, y, max_iter: int = 2000, keep_losses: bool = True):
        """
        Fit the model according to the given training data.

        :param X: training samples; array of shape (n_samples, n_features)
        :param y: training targets (+1 and -1); array of shape (n_samples,)
        :param max_iter: number of SGD iterations
        :param keep_losses:
        :return: the training losses and accuracies during training
        """
        # Initialize learned parameters
        self.init_solution(X.shape[1])

        losses = []
        accuracies = []

        if keep_losses:
            losses.append(self.loss(self.w, self.b, self.C, X, y))
            accuracies.append(self.score(X, y))

        permutation = np.random.permutation(len(y))
        X = X[permutation, :]
        y = y[permutation]

        # Iterate over batches
        for iter in range(0, max_iter):
            start_idx = (iter * self.batch_size) % X.shape[0]
            end_idx = min(X.shape[0], start_idx + self.batch_size)
            batch_X = X[start_idx:end_idx, :]
            batch_y = y[start_idx:end_idx]

            # TODO: Compute the (sub)gradient of the current *batch*

            g_w, g_b = self.subgradient(self.w, self.b, self.C, batch_X, batch_y)

            # Perform a (sub)gradient step
            # TODO: update the learned parameters correctly
            self.w = self.w - self.lr*g_w
            self.b = self.b - self.lr*g_b

            if keep_losses:
                losses.append(self.loss(self.w, self.b, self.C, X, y))
                accuracies.append(self.score(X, y))

        return losses, accuracies

    def fit(self, X, y, max_iter: int = 2000):
        """
        Fit the model according to the given training data.
        ** Do not edit this method **

        :param X: training samples; array of shape (n_samples, n_features)
        :param y: training targets (+1 and -1); array of shape (n_samples,)
        :param max_iter: number of SGD iterations
        """
        self.fit_with_logs(X, y, max_iter=max_iter, keep_losses=False)

        return self

    def predict(self, X):
        """
        Perform classification on samples in X.

        :param X: samples for prediction; array of shape (n_samples, n_features)
        :return: Predicted class labels for samples in X; array of shape (n_samples,)
                 NOTE: the labels must be either +1 or -1
        """
        # TODO: compute the predicted labels (+1 or -1)
        # Take each x in X and set it's y value as: sign((w^T)x + b)
        y_pred = np.sign(X.dot(self.w) + self.b)
        # Little problem: if x==0 then np.sign(x)==0. We want x==0  ->  y==1.
        y_pred[y_pred == 0] = 1
        return y_pred
