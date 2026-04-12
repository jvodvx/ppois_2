from xml.dom.minidom import Document


class XMLWriter:

    def save(self, students, filename: str):
        doc = Document()

        root = doc.createElement("students")
        doc.appendChild(root)

        for student in students:
            student_el = doc.createElement("student")

            # имя
            name_el = doc.createElement("name")
            name_text = doc.createTextNode(student.name)
            name_el.appendChild(name_text)

            # группа
            group_el = doc.createElement("group")
            group_text = doc.createTextNode(student.group)
            group_el.appendChild(group_text)

            # экзамены
            exams_el = doc.createElement("exams")

            for exam in student.exams:
                exam_el = doc.createElement("exam")

                subject_el = doc.createElement("subject")
                subject_el.appendChild(doc.createTextNode(exam.subject))

                score_el = doc.createElement("score")
                score_el.appendChild(doc.createTextNode(str(exam.score)))

                exam_el.appendChild(subject_el)
                exam_el.appendChild(score_el)

                exams_el.appendChild(exam_el)

            # собираем student
            student_el.appendChild(name_el)
            student_el.appendChild(group_el)
            student_el.appendChild(exams_el)

            root.appendChild(student_el)

        # запись в файл
        with open(filename, "w", encoding="utf-8") as f:
            f.write(doc.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8"))