import xml.sax
from model.entities.student import Student


class StudentHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.students = []

        self.current_data = ""
        self.current_student = None
        self.current_exam = None
        self.current_text = []

    # --- начало элемента ---
    def startElement(self, tag, attributes):
        self.current_data = tag
        self.current_text = []

        if tag == "student":
            self.current_student = {"exams": []}

        elif tag == "exam":
            self.current_exam = {}

    # --- конец элемента ---
    def endElement(self, tag):
        value = "".join(self.current_text).strip()

        if tag == "name" and self.current_student is not None:
            self.current_student["name"] = value

        elif tag == "group" and self.current_student is not None:
            self.current_student["group"] = value

        elif tag == "subject" and self.current_exam is not None:
            self.current_exam["subject"] = value

        elif tag == "score" and self.current_exam is not None:
            self.current_exam["score"] = int(value)

        elif tag == "exam":
            self.current_student["exams"].append(self.current_exam)
            self.current_exam = None

        elif tag == "student":
            student = Student.from_dict(self.current_student)
            self.students.append(student)
            self.current_student = None

        self.current_data = ""
        self.current_text = []

    # --- содержимое ---
    def characters(self, content):
        if self.current_data in {"name", "group", "subject", "score"}:
            self.current_text.append(content)


class XMLReader:

    def load(self, filename: str):
        handler = StudentHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filename)

        return handler.students
