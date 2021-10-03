class EmbeddedException(Exception):

    def __str__(self):
        return f"{type(self)}: {super().__str__()}\n" \
               f"       Embedded: {self._exception}"

    def __init__(self, *args, exception: Exception = None):
        super().__init__(*args)
        self._exception = exception