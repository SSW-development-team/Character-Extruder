class IdeologyLeader():

    def __init__(self, ideology):
        self.ideology = ideology
        self.expire = ""
        self.traits: list[str] = []

    def __repr__(self):
        return f"[{self.expire}, {self.traits}]"
