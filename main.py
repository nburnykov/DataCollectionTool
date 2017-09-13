import logging
from UI.mainform import showmainform
from io import StringIO


logger = logging.getLogger('main')

formatter = logging.Formatter(
    '%(asctime)s %(module)-12s %(levelname)-8s %(message)s')

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
streamhandler.setLevel(logging.DEBUG)
logger.addHandler(streamhandler)

vstream = StringIO()
vstreamhandler = logging.StreamHandler(vstream)
vstreamhandler.setFormatter(formatter)
vstreamhandler.setLevel(logging.DEBUG)
logger.addHandler(vstreamhandler)

filehandler = logging.FileHandler('Application.log')
filehandler.setFormatter(formatter)
filehandler.setLevel(logging.DEBUG)
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.info('===============================================================================================')
    logger.info('Start application')

    start_ui = True

    if start_ui:

        logger.debug('Start UI')
        showmainform()

    else:
        # TODO load scan data from file
        logger.debug('UI disabled, loading config from file')
        pass

