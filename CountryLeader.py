from IdeologyLeader import IdeologyLeader


class CountryLeader():
    id = ""
    name = ""
    picture = ""
    ideologies: dict[str, IdeologyLeader] = dict()

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"{self.name}, {self.picture}, {self.ideologies}"
