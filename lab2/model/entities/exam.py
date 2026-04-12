class Exam:
    def __init__(self, subject: str, score: int):
        self.subject = subject
        self.score = score

    def __repr__(self):
        return f"Exam(subject='{self.subject}', score={self.score})"

    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "score": self.score
        }

    @staticmethod
    def from_dict(data: dict):
        return Exam(
            subject=data["subject"],
            score=data["score"]
        )