from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from model.entities.exam import Exam
from model.entities.student import Student
from model.io.xml_writer import XMLWriter


MALE_FIRST_NAMES = [
    "Алексей", "Андрей", "Иван", "Дмитрий", "Егор",
    "Игорь", "Никита", "Павел", "Сергей", "Максим",
]

FEMALE_FIRST_NAMES = [
    "Анна", "Дарья", "Елена", "Ирина", "Мария",
    "Наталья", "Ольга", "Светлана", "Татьяна", "Юлия",
]

PATRONYMICS = [
    ("Александрович", "Александровна"),
    ("Андреевич", "Андреевна"),
    ("Викторович", "Викторовна"),
    ("Дмитриевич", "Дмитриевна"),
    ("Игоревич", "Игоревна"),
    ("Максимович", "Максимовна"),
    ("Николаевич", "Николаевна"),
    ("Павлович", "Павловна"),
    ("Сергеевич", "Сергеевна"),
    ("Юрьевич", "Юрьевна"),
]

SURNAMES = [
    ("Иванов", "Иванова"),
    ("Петров", "Петрова"),
    ("Сидоров", "Сидорова"),
    ("Смирнов", "Смирнова"),
    ("Козлов", "Козлова"),
    ("Орлов", "Орлова"),
    ("Павлов", "Павлова"),
    ("Новиков", "Новикова"),
    ("Федоров", "Федорова"),
    ("Попов", "Попова"),
]

GROUPS = ["101", "102", "103", "104", "105", "201", "202", "203", "204", "205"]

SUBJECTS_SET_A = [
    "Математика", "Физика", "Программирование",
    "История", "Экономика", "Английский язык",
]
SUBJECTS_SET_B = [
    "Алгебра", "Базы данных", "Компьютерные сети",
    "Статистика", "Философия", "Менеджмент",
]


def build_group_subjects(groups: list[str], subjects: list[str], offset: int) -> dict[str, list[str]]:
    group_subjects = {}

    for index, group in enumerate(groups):
        start = (index + offset) % len(subjects)
        exam_count = 3 + (index % 3)
        group_subjects[group] = [
            subjects[(start + subject_index) % len(subjects)]
            for subject_index in range(exam_count)
        ]

    return group_subjects


def build_students(subjects: list[str], offset: int) -> list[Student]:
    students = []
    group_subjects = build_group_subjects(GROUPS, subjects, offset)

    for index in range(50):
        is_female = index % 2 == 1
        person_index = index // 2

        first_names = FEMALE_FIRST_NAMES if is_female else MALE_FIRST_NAMES
        first_name = first_names[person_index % len(first_names)]

        surname_pair = SURNAMES[(person_index // len(first_names) + offset) % len(SURNAMES)]
        patronymic_pair = PATRONYMICS[(person_index // 5 + offset) % len(PATRONYMICS)]

        last_name = surname_pair[1] if is_female else surname_pair[0]
        patronymic = patronymic_pair[1] if is_female else patronymic_pair[0]
        group = GROUPS[(index + offset) % len(GROUPS)]
        subjects_for_group = group_subjects[group]

        exams = []
        for exam_index, subject in enumerate(subjects_for_group):
            score = 6 + ((person_index + exam_index + offset) % 5)
            exams.append(Exam(subject, score))

        students.append(Student(f"{last_name} {first_name} {patronymic}", group, exams))

    return students


def main():
    output_dir = Path(__file__).resolve().parent
    writer = XMLWriter()

    datasets = {
        "demo_set_a.xml": build_students(SUBJECTS_SET_A, offset=0),
        "demo_set_b.xml": build_students(SUBJECTS_SET_B, offset=3),
    }

    for filename, students in datasets.items():
        writer.save(students, str(output_dir / filename))


if __name__ == "__main__":
    main()
