class BubblegumError(Exception):
    pass


class UploadFailed(BubblegumError):
    pass


class RehostFailed(BubblegumError):
    pass
