class BatchReadingError(Exception):
    """Error while doing batch process.

    Attributes:
        last_batch -- last batch where the error occured
        msg  -- explanation of the error
    """

    def __init__(self, last_batch, msg):
        self.last_batch = last_batch
        self.msg = msg