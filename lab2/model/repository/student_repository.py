from typing import List
from model.entities.student import Student


class StudentRepository:

    def __init__(self):
        self._students: List[Student] = []

    def add(self, student: Student):
        self._students.append(student)

    def get_all(self) -> List[Student]:
        return list(self._students)

    def clear(self):
        self._students.clear()

    def set_all(self, students: List[Student]):
        self._students = students

    def get_internal_list(self) -> List[Student]:
        return self._students

    def get_all_groups(self) -> List[str]:
        return sorted(set(s.group for s in self._students))

    def get_all_subjects(self) -> List[str]:
        subjects = set()
        for s in self._students:
            for e in s.exams:
                subjects.add(e.subject)
        return sorted(subjects)