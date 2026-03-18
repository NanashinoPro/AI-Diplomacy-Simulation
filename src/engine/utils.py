from models import RelationType

class UtilsMixin:
    # ヘルパー関数
    def _get_relation(self, c1: str, c2: str) -> RelationType:
        if c1 not in self.state.relations:
            self.state.relations[c1] = {}
        if c2 not in self.state.relations[c1]:
            self.state.relations[c1][c2] = RelationType.NEUTRAL
        return self.state.relations[c1][c2]

    def _update_relation(self, c1: str, c2: str, rel: RelationType):
        if c1 not in self.state.relations:
            self.state.relations[c1] = {}
        if c2 not in self.state.relations:
            self.state.relations[c2] = {}
        self.state.relations[c1][c2] = rel
        self.state.relations[c2][c1] = rel
