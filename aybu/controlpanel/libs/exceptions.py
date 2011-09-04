
class ValidationError(Exception):

    def __init__(self, message, *args):
        super(ValidationError, self).__init__(message, *args)

    def __repr__(self):

        if len(self.args) > 1:
            return self.args[0] % self.args

        return self.args[0]

