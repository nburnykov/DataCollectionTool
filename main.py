import logging
from UI.mainform import showmainform

logger = logging.getLogger('main')

formatter = logging.Formatter(
    '%(asctime)s %(module)-12s %(levelname)-8s %(message)s')

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
streamhandler.setLevel(logging.DEBUG)
logger.addHandler(streamhandler)

filehandler = logging.FileHandler('Application.log')
filehandler.setFormatter(formatter)
filehandler.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.info('===============================================================================================')
    logger.info('Starting application')

    start_ui = True

    if start_ui:

        logger.debug('Starting UI')
        showmainform()

    else:
        # TODO load scan data from file
        logger.debug('UI disabled, loading config from file')
        pass

