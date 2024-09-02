import sys
import logging

from wqp.ml import build_wine_predictor_model
from wqp.evaluation import compute_model_metrics
from wqp.data_access import fetch_csv_data, build_train_test_sets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wqp.main')


def model_training_workflow(data_path):
    """
    This functions orchestrates the whole training script, as distinct steps:
    - fetching input data
    - splitting them into train and test datasets
    - defining the model
    - fitting the model on the training data
    - evaluating the model on the test data
    :param data_path: a string containing the location of the training data

    """

    logger.info('Starting wine quality predictor training...')

    try:
        logger.info('Fetching data...')
        data = fetch_csv_data(url=data_path, separator=';')

        logger.info('Building train and test datasets...')
        label_column = 'quality'
        train_test_data = build_train_test_sets(data=data, label_col=label_column, train_size=0.8)

        logger.info('Fitting model...')
        model_definition = build_wine_predictor_model()
        x_train, y_train = train_test_data['train']
        model = model_definition.fit(X=x_train, y=y_train)

        logger.info('Evaluating model...')
        x_test, y_test = train_test_data['test']
        evaluation_metrics = compute_model_metrics(model=model, x=x_test, y=y_test)

        logger.info(f'Finished model evaluation. Metrics: {evaluation_metrics}')

    except Exception as e:
        logger.error(e)
        sys.exit(1)