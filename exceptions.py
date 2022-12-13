
class UsiLoginException(Exception):

    def __init__(self, login_institution: str=None, *args: object) -> None:
        super().__init__(*args)
        self.login_institution = login_institution
