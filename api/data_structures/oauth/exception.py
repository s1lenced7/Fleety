from misc.exceptions import EmbeddedException


class OAuthException(EmbeddedException):
    """"""


class OAuthRefreshException(EmbeddedException):

    def __init__(self, *args, status_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code