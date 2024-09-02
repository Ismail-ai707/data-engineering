import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

def compute_model_metrics(model, x, y):
    """
    This function computes the performance metrics of a given model and returns them as a dictionary.
    :param model: The machine learning model, as a Scikit Learn pipeline.
    :param x: The features, as a Pandas DataFrame.
    :param y: The response data, as a Pandas DataFrame.
    :return: A dictionary, containing 2 key-values:
        - rmse: the root mean square error
        - r2: the r2 score
    """
    predictions = model.predict(X=x)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)
    return dict(rmse=rmse, r2=r2)