from sklearn.model_selection import train_test_split
import pandas as pd


def fetch_csv_data(url, separator):
    """
    This functions fetch the CSV data from a given path (or url) and returns a Pandas DataFrame.
    :param url: a string containing the address of the data (local path, url ...)
    :param separator: an optional separator to override the default separator (comma)
    :return: a Pandas Dataframe containing the loaded data
    """
    try:
        if separator:
            return pd.read_csv(url, sep=separator)
        else:
            return pd.read_csv(url)
    except Exception as e:
        raise Exception(f'Error while fetching data at url {url}: {e}')
    
def build_train_test_sets(data, label_col, train_size):
    """
    A function to split the data into training and test sets.

    :param data: a pandas dataframe
    :param label_col: the label column name
    :param train_size: flaot. The fraction of the whole dataset used for training.
    :return: a Dictionary of key (string) - value (tuple of pandas dataframes) containing training and test data.
    Dictionary keys:
        - train: contains (X_train, y_train)
        - test: contains (X_test, y_test)
    """
    try:
        X = data.drop(label_col, axis=1)
        y = data[label_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_size)

        return dict(train=(X_train, y_train), test=(X_test, y_test))
    
    except Exception as e:
        raise Exception(f'Error while splitting data: {e}')