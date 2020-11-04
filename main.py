import logging
from ui.mainform import show_main_form

logger = logging.getLogger('main')

formatter = logging.Formatter(
    '%(asctime)s %(module)-12s %(levelname)-8s %(message)s')

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
streamhandler.setLevel(logging.DEBUG)
streamhandler.set_name = 'console'
logger.addHandler(streamhandler)

filehandler = logging.FileHandler('application.log')
filehandler.setFormatter(formatter)
filehandler.setLevel(logging.DEBUG)
filehandler.set_name = 'file'
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.info('===============================================================================================')
    logger.info('Start application')

    start_ui = True

    if start_ui:

        logger.debug('Start ui')
        show_main_form()

    else:
        # TODO load scan data from file
        logger.debug('ui disabled, loading config from file')


