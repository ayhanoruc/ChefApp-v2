import logging 
import os 
from datetime import datetime 
from src.constants import pipeline_constants


class AppLogger:

    """
    A class for handling custom logging operations.

    Attributes:
        phase_name (str): The name of the current process name.
        logs_path (str): The base directory for log files.
        logger: The logger object for this process.
    """

    def __init__(self,phase_name):
        
        self.phase_name = phase_name
        self.logs_path = pipeline_constants.LOGS_DIR
        os.makedirs(self.logs_path, exist_ok=True)
        self.logger = self._configure_logger()
    
    def _configure_logger(self)->logging.Logger:
        """
        configurations for custom logger object.
        Returns:
            logging.Logger: A configured logger instance.
        """
        logger = logging.getLogger(self.phase_name)  # logger initalization
        logger.setLevel(logging.INFO)  # for common use

        formatter = logging.Formatter(
            "[%(asctime)s -Process: %(name)s --Level: %(levelname)s --Message: %(message)s]"
        )
        #get current datetime, include only day to collect logs in daily basis
        #use strftime to format datetime
        current_dt = datetime.now()
        LOG_FILE_NAME = f"{current_dt.strftime('%d-%m-%Y')}.log"
        log_file_path = os.path.join(self.logs_path, LOG_FILE_NAME)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def handle_logging(self, message:str, level=logging.INFO):
        """
        A method for handling custom logging operations.
        Args:
            message (str): The message to be logged.
            level (logging.level, optional): The logging level. Defaults to logging.INFO.

        """
        self.logger.log(level=level, msg=message)
    

    
"""if __name__ == "__main__":
    logger = AppLogger("test")
    logger.handle_logging("error occured at line 4", level=logging.ERROR)"""
