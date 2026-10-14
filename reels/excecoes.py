class ErroReel(Exception):
    """Base dos erros ao processar um reel."""


class ErroDownload(ErroReel):
    pass


class ErroAnalise(ErroReel):
    pass
