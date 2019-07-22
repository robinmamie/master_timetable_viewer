from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QAbstractScrollArea, QTextEdit
from course_parsing import parse_timetable
from sys import exit

pdf_source = 'm1_2019.pdf'

app = QApplication(['Master Timetable Viewer'])

window = QMainWindow()
mainWidget = QWidget()
window.setCentralWidget(mainWidget)
window.resize(1900,800)
l_main = QGridLayout(mainWidget)

info_box = QTextEdit()
info_box.setReadOnly(True)

# Create data table
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
data_l = []
hours = ['Time']
for i in range(8,19):
    hours.append(f'{i:02}:15-\n{i+1:02}:00')
data_l.append(hours)
for d in days:
    l = [d]
    for i in range(11):
        l.append("")
    data_l.append(l)
data = dict([(d[0], d[1:]) for d in data_l])


# TIMETABLE
# Table Widget
class TableView(QTableWidget):
    def __init__(self, *args):
        QTableWidget.__init__(self, *args)
        self.setData()
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def setData(self):
        horHeaders = []
        for n, key in enumerate(data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

w_table = TableView(11, 6)



# COURSES
# Course Button
class CourseButton(QPushButton):
    def __init__(self, course, table):
        name = course[0].name
        if course[0].isObligatory:
            name = '* ' + name
        QPushButton.__init__(self, name)
        self.name = name
        self.course = course
        self.table = table
        self.setCheckable(True)
        self.toggled.connect(self.display_course)

    def display_course(self):
        for c in self.course:
            day = days[c.day]
            title = f'{self.name} '
            start = c.start // 100 - 8
            end = c.end // 100 - 8
            for hour in range(start, end):
                specific_title = title
                specific_title += '(lec)' if c.isLecture else '(ex)'
                specific_title += '\n'
                if self.isChecked():
                    data[day][hour] += specific_title
                else:
                    data[day][hour] = data[day][hour].replace(specific_title, "")
        self.table.setData()

        c = self.course[0]
        info = f'-- {c.code} / {c.name} -- {c.credits} credits\n'
        info += f'Teacher : {c.teacher}\n'
        info += 'Is a core course' if c.isObligatory else 'Is an optional course'
        info_box.setText(info)

# COURSE LIST
# TODO implement line breaks in buttons?
# Course list Widget
w_course_list = QWidget()
# Course list Scroll
s_course_list = QScrollArea()
s_course_list.setWidget(w_course_list)
s_course_list.setWidgetResizable(True)
s_course_list.setFixedHeight(800)
s_course_list.setFixedWidth(600)
# Course list Layout
l_course_list = QVBoxLayout(w_course_list)
l_course_list.addStretch()

# Course parsing & buttons
courses = parse_timetable(pdf_source)
buttons = []
for c in courses:
    buttons.append(CourseButton(c, w_table))
buttons.sort(key=lambda b: b.name)
for b in buttons:
    l_course_list.addWidget(b)


l_main.addWidget(s_course_list, 1, 0)
l_main.addWidget(w_table, 1, 1)
l_main.addWidget(info_box, 2, 0)

window.show()
exit(app.exec_())
