from typing import List
from model.entities.exam import Exam


class Student:
    def __init__(self, name: str, group: str, exams: List[Exam]):
        self.name = name
        self.group = group
        self.exams = exams

    def average_score(self) -> float:
        if not self.exams:
            return 0.0
        return sum(e.score for e in self.exams) / len(self.exams)

    def has_subject(self, subject: str) -> bool:
        return any(e.subject == subject for e in self.exams)

    def get_exam(self, subject: str):
        for e in self.exams:
            if e.subject == subject:
                return e
        return None

    def get_score_by_subject(self, subject: str):
        exam = self.get_exam(subject)
        return exam.score if exam else None

    def __repr__(self):
        return (
            f"Student(name='{self.name}', "
            f"group='{self.group}', "
            f"avg={self.average_score():.2f})"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "group": self.group,
            "exams": [e.to_dict() for e in self.exams]
        }

    @staticmethod
    def from_dict(data: dict):
        exams = [Exam.from_dict(e) for e in data.get("exams", [])]
        return Student(
            name=data["name"],
            group=data["group"],
            exams=exams
        )