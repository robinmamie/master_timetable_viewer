from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QAbstractScrollArea, QTextEdit
from course_parsing import parse_timetable
from sys import exit

pdf_source = 'm1_2019.pdf'

app = QApplication(['Master Timetable Viewer'])

window = QMainWindow()
mainWidget = QWidget()
window.setCentralWidget(mainWidget)
window.resize(1900,900)
l_main = QGridLayout(mainWidget)

# Info Box
info_box = QTextEdit()
info_box.setReadOnly(True)

# Credit tally
c_tally = {
        'tot': ['0', '90 (78/70)'],
        'obl': ['0', '30'],
        'opt': ['0', '-'],
        'shs': ['0', '6'],
        'a': ['0', '30'],
        'b': ['0', '30'],
        'c': ['0', '30'],
        'd': ['0', '30'],
        'e': ['0', '30'],
        'f': ['0', '30'],
        'g': ['0', '30'],
        'h': ['0', '30'],
        'i': ['0', '30'],
        'j': ['0', '30']
    }

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
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def setData(self):
        horHeaders = []
        for n, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

w_table = TableView(data, 11, 6)
w_credits = TableView(c_tally, 2, 14)


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
        self.toggled.connect(self.handle_course)

    def handle_course(self):

        # Display Course
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

        # Display Information
        c = self.course[0]
        info = f'-- {c.code} / {c.name} -- {c.credits} credits\n'
        info += f'Teacher : {c.teacher}\n'
        info += 'Is a core course' if c.isObligatory else 'Is an optional course'
        if c.specs:
            info += ', counting for specialization(s): '
            for s in c.specs:
                info += s.upper() + ' '
        info_box.setText(info)

        # Count Credits
        cred = c.credits if self.isChecked() else -c.credits
        def add_credits(name):
            c_tally[name][0] = str(int(c_tally[name][0]) + cred)

        add_credits('tot')
        if 'HSS' in c.name:
            add_credits('shs')
        else:
            if c.isObligatory:
                add_credits('obl')
            else:
                add_credits('opt')
            for s in c.specs:
                add_credits(s)
        w_credits.setData()




# COURSE LIST
# TODO implement line breaks in buttons?
# Course list Widget
w_course_list = QWidget()
# Course list Scroll
s_course_list = QScrollArea()
s_course_list.setWidget(w_course_list)
s_course_list.setWidgetResizable(True)
s_course_list.setFixedHeight(750)
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
l_main.addWidget(w_credits, 2, 1)

window.show()
exit(app.exec_())
