import logging
from UI.mainform import show_main_form

logger = logging.getLogger('main')

formatter = logging.Formatter(
    '%(asctime)s %(module)-12s %(levelname)-8s %(message)s')

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
streamhandler.setLevel(logging.DEBUG)
streamhandler.set_name = 'Console'
logger.addHandler(streamhandler)

filehandler = logging.FileHandler('Application.log')
filehandler.setFormatter(formatter)
filehandler.setLevel(logging.DEBUG)
filehandler.set_name = 'File'
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.info('===============================================================================================')
    logger.info('Start application')

    start_ui = True

    if start_ui:

        logger.debug('Start UI')
        show_main_form()

    else:
        # TODO load scan data from file
        logger.debug('UI disabled, loading config from file')


