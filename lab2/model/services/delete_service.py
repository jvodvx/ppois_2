from typing import List
from model.entities.student import Student
from model.services.search_service import SearchService


class DeleteService:

    @staticmethod
    def delete(
        students: List[Student],
        group: str = None,
        subject: str = None,
        min_avg: float = None,
        max_avg: float = None,
        min_score: int = None,
        max_score: int = None,
    ) -> int:

        to_delete = SearchService.search(
            students,
            group,
            subject,
            min_avg,
            max_avg,
            min_score,
            max_score
        )

        count = len(to_delete)

        # удаляем
        students[:] = [s for s in students if s not in to_delete]

        return count