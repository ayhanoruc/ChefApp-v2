import sys 
from src.logger import AppLogger
import logging


class CustomException(Exception):

    def __init__(self, error, error_detail:sys): # these args will come from sys exception.
        super().__init__(error)
        self.error = error 
        self.error_detail = error_detail
        self.error_message = self.get_error_message()

    def __str__(self):
        return self.error_message 


    def get_error_message(self,):
        _, _, exc_tb = self.error_detail.exc_info() # execution traceback
        file_name = exc_tb.tb_frame.f_code.co_filename # extract relevant information
        error_line = exc_tb.tb_lineno
        #construct custom error_message
        error_message = f"Error occured at [{file_name}] at line number [{error_line}]  error message: [{self.error}] "  # customized error message

        return error_message

def handle_exceptions(func):
    """
    our custom exception logic is implemented here, and should be called in any file.
    will work as decorator for any function to catch any exceptions and log them
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            exc = CustomException(e, sys)# this will trigger __str__ of CustomException
            args[0].log_writer.handle_logging(exc, level=logging.ERROR)
            raise exc

    return wrapper


"""if __name__ == "__main__":
    
    class Test:
        def __init__(self):
            
            self.log_writer = AppLogger("TEST CLASS")

        @handle_exceptions
        def test(self,):
            print(1/0)


    obj = Test()
    obj.test()"""
    
