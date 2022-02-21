"""################# Custom Exceptions #######################"""


class CustomVoucherBusinessException(Exception):
    """Exception Raised when there is an error in business logic layer in the implementation """

    def __init__(self, message="Voucher Business Exception"):
        self.message = message
        super().__init__(self.message)


class CustomDatabaseException(Exception):
    """Exception Raised when there is an error in business logic layer in the implementation """

    def __init__(self, message="Database Exception"):
        self.message = message
        super().__init__(self.message)
