from typing import List
from model.entities.student import Student


class SearchService:

    @staticmethod
    def search(
        students: List[Student],
        group: str = None,
        subject: str = None,
        min_avg: float = None,
        max_avg: float = None,
        min_score: int = None,
        max_score: int = None,
    ) -> List[Student]:

        result = []

        for student in students:

            # --- фильтр по группе ---
            if group and student.group != group:
                continue

            # --- фильтр по среднему баллу ---
            avg = student.average_score()

            if min_avg is not None and avg < min_avg:
                continue

            if max_avg is not None and avg > max_avg:
                continue

            if subject:
                exam = next((e for e in student.exams if e.subject == subject), None)

                if not exam:
                    continue

                if min_score is not None and exam.score < min_score:
                    continue

                if max_score is not None and exam.score > max_score:
                    continue

            result.append(student)

        return result