from IdeologyLeader import IdeologyLeader


class CountryLeader():
    def __init__(self, id):
        self.id = id
        self.name = ""
        self.picture = ""
        self.ideologies: dict[str, IdeologyLeader] = dict()

    def __repr__(self):
        return f"{self.name}, {self.picture}, {self.ideologies}"
