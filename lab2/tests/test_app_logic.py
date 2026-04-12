import tempfile
import unittest
from pathlib import Path

from model.entities.exam import Exam
from model.entities.student import Student
from model.io.xml_reader import XMLReader
from model.io.xml_writer import XMLWriter
from model.services.delete_service import DeleteService
from model.services.search_service import SearchService
from utils.converters import to_float, to_int
from utils.validators import validate_delete_filters, validate_search_filters, validate_student


def build_students():
    return [
        Student(
            "Ivanov Alexey",
            "101",
            [Exam("Mathematics", 9), Exam("Physics", 8)],
        ),
        Student(
            "Petrov Andrey",
            "102",
            [Exam("Mathematics", 6), Exam("Programming", 10)],
        ),
        Student(
            "Sidorova Maria",
            "101",
            [Exam("History", 7), Exam("English", 9)],
        ),
    ]


class SearchServiceTests(unittest.TestCase):
    def test_search_by_group(self):
        students = build_students()

        results = SearchService.search(students, group="101")

        self.assertEqual(2, len(results))

    def test_search_by_subject_and_score_range(self):
        students = build_students()

        results = SearchService.search(
            students,
            subject="Mathematics",
            min_score=8,
            max_score=10,
        )

        self.assertEqual(["Ivanov Alexey"], [student.name for student in results])


class DeleteServiceTests(unittest.TestCase):
    def test_delete_by_group(self):
        students = build_students()

        deleted = DeleteService.delete(students, group="102")

        self.assertEqual(1, deleted)
        self.assertEqual(["Ivanov Alexey", "Sidorova Maria"], [student.name for student in students])


class XmlIoTests(unittest.TestCase):
    def test_xml_roundtrip(self):
        students = build_students()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "students.xml"

            XMLWriter().save(students, str(file_path))
            loaded = XMLReader().load(str(file_path))

        self.assertEqual(
            [student.to_dict() for student in students],
            [student.to_dict() for student in loaded],
        )


class ValidatorTests(unittest.TestCase):
    def test_search_requires_subject_for_score_filter(self):
        with self.assertRaises(ValueError):
            validate_search_filters({"min_score": 7, "max_score": None})

    def test_delete_requires_at_least_one_filter(self):
        with self.assertRaises(ValueError):
            validate_delete_filters({})

    def test_student_rejects_duplicate_subjects(self):
        with self.assertRaises(ValueError):
            validate_student(
                "Ivanov Alexey",
                "101",
                [Exam("Mathematics", 8), Exam("Mathematics", 9)],
            )


class ConverterTests(unittest.TestCase):
    def test_to_int_rejects_invalid_string(self):
        with self.assertRaises(ValueError):
            to_int("abc")

    def test_to_float_accepts_comma_separator(self):
        self.assertEqual(7.5, to_float("7,5"))


if __name__ == "__main__":
    unittest.main()
