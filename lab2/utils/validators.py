def validate_student(name: str, group: str, exams: list):
    if not name:
        raise ValueError("Введите ФИО")

    if not group:
        raise ValueError("Введите группу")

    if not exams:
        raise ValueError("Добавьте хотя бы один экзамен")

    subjects = [exam.subject.strip().lower() for exam in exams]
    if len(subjects) != len(set(subjects)):
        raise ValueError("У студента не должно быть повторяющихся предметов")


def validate_exam(subject: str, score: int, row: int):
    if not subject:
        raise ValueError(f"Пустой предмет в строке {row}")

    if score is None:
        raise ValueError(f"Пустой балл в строке {row}")

    if score < 0 or score > 10:
        raise ValueError(f"Балл должен быть 0-10 (строка {row})")


def validate_search_filters(filters: dict):
    _validate_filters(filters, require_filter=False)


def validate_delete_filters(filters: dict):
    _validate_filters(filters, require_filter=True)


def _validate_filters(filters: dict, require_filter: bool):
    group = filters.get("group")
    subject = filters.get("subject")
    min_avg = filters.get("min_avg")
    max_avg = filters.get("max_avg")
    min_score = filters.get("min_score")
    max_score = filters.get("max_score")

    _validate_range(min_avg, max_avg, "Средний балл")
    _validate_range(min_score, max_score, "Балл по предмету")

    if min_avg is not None and not 0 <= min_avg <= 10:
        raise ValueError("Средний балл должен быть в диапазоне 0-10")

    if max_avg is not None and not 0 <= max_avg <= 10:
        raise ValueError("Средний балл должен быть в диапазоне 0-10")

    if min_score is not None and not 0 <= min_score <= 10:
        raise ValueError("Балл по предмету должен быть в диапазоне 0-10")

    if max_score is not None and not 0 <= max_score <= 10:
        raise ValueError("Балл по предмету должен быть в диапазоне 0-10")

    if (min_score is not None or max_score is not None) and not subject:
        raise ValueError("Для фильтрации по баллу укажите предмет")

    if require_filter and not any(
        value is not None and value != ""
        for value in (group, subject, min_avg, max_avg, min_score, max_score)
    ):
        raise ValueError("Укажите хотя бы одно условие удаления")


def _validate_range(min_value, max_value, label: str):
    if min_value is not None and max_value is not None and min_value > max_value:
        raise ValueError(f"{label}: нижняя граница не может быть больше верхней")
