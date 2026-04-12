from model.repository.student_repository import StudentRepository
from model.services.search_service import SearchService
from model.services.delete_service import DeleteService
from model.io.xml_writer import XMLWriter
from model.io.xml_reader import XMLReader

class AppController:

    def __init__(self):
        self.repo = StudentRepository()

    def add_student(self, student):
        self.repo.add(student)

    def get_all_students(self):
        return self.repo.get_all()

    def search_students(self, filters: dict):
        return SearchService.search(
            self.repo.get_all(),
            group=filters.get("group"),
            subject=filters.get("subject"),
            min_avg=filters.get("min_avg"),
            max_avg=filters.get("max_avg"),
            min_score=filters.get("min_score"),
            max_score=filters.get("max_score"),
        )

    def delete_students(self, filters: dict) -> int:
        return DeleteService.delete(
            self.repo.get_internal_list(),
            group=filters.get("group"),
            subject=filters.get("subject"),
            min_avg=filters.get("min_avg"),
            max_avg=filters.get("max_avg"),
            min_score=filters.get("min_score"),
            max_score=filters.get("max_score"),
        )

    def get_groups(self):
        return self.repo.get_all_groups()

    def get_subjects(self):
        return self.repo.get_all_subjects()

    def save_to_file(self, filename):
        writer = XMLWriter()
        writer.save(self.repo.get_all(), filename)

    def load_from_file(self, filename):
        reader = XMLReader()
        students = reader.load(filename)

        self.repo.set_all(students)