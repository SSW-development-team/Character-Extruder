class IdeologyLeader():
    ideology = ""
    expire = ""
    traits: list[str] = []

    def __init__(self, ideology):
        self.ideology = ideology

    def __repr__(self):
        return f"[{self.expire}, {self.traits}]"
