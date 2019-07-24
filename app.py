from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QAbstractScrollArea, QTextEdit, QTabWidget
from course_parsing import parse_timetable
from sys import exit

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
        'tot': ['0', '120'],
        'pdm': ['0', '30'],
        'obl': ['0', '30'],
        'pro': ['0', '12'],
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
for i in range(1,9):
    c_tally[f'M{i}'] = ['0', '-']

# Create data table
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
data = []
for i in range(8):
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
    data_u = dict([(d[0], d[1:]) for d in data_l])
    data.append(data_u)



# TIMETABLE
# Table Widget
class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData(0)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def setData(self, index):
        horHeaders = []
        data = self.data[index]
        for n, key in enumerate(data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

w_table = TableView(data, 11, 6)
w_credits = TableView([c_tally], 2, 23)


# COURSES
# Course Button
class CourseButton(QPushButton):
    def __init__(self, course, table, index):
        name = course[0].name
        self.isProject = name == 'Master Project' or name == 'Semester Project' or name == 'Optional Project'
        if self.isProject:
            name = '# ' + name
        elif course[0].isObligatory:
            name = '* ' + name
        QPushButton.__init__(self, name)
        self.name = name
        self.course = course
        self.table = table
        self.index = index
        self.setCheckable(True)
        self.toggled.connect(self.handle_course)

    def handle_course(self):

        # Display Course
        if not self.isProject:
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
                        data[self.index][day][hour] += specific_title
                    else:
                        data[self.index][day][hour] = data[self.index][day][hour].replace(specific_title, "")
            self.table.setData(self.index)

        # Display Information
        c = self.course[0]
        info = f'-- {c.code} / {c.name} -- {c.credits} credits\n'
        info += f'Teacher : {c.teacher}\n'
        info += 'Is a project' if self.isProject else 'Is a core course' if c.isObligatory else 'Is an optional course'
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
        add_credits(f'M{self.index+1}')
        if 'HSS' in c.name:
            add_credits('shs')
        else:
            if c.isObligatory:
                add_credits('obl')
            elif 'master project' in c.name.lower():
                add_credits('pdm')
            elif 'project' in c.name.lower():
                add_credits('pro')
            for s in c.specs:
                add_credits(s)
        w_credits.setData(0)




# COURSE LIST
# TODO implement line breaks in buttons?
# Course list Widget
w_course_list = QTabWidget()
# Course list Scroll
s_course_list = QScrollArea()
s_course_list.setWidget(w_course_list)
s_course_list.setWidgetResizable(True)
s_course_list.setFixedHeight(750)
s_course_list.setFixedWidth(600)
# Course tabs
def tab_change(i):
    w_table.setData(i)
w_course_list.currentChanged.connect(tab_change)


for i in range(8):
    # Course list Layout
    w_cl = QWidget()
    w_course_list.addTab(w_cl, f'M{i+1}')
    l_course_list = QVBoxLayout(w_cl)
    w_cl.setLayout(l_course_list)
    l_course_list.addStretch()

    # Course parsing & buttons
    pdf_source = f'm{(i%2)+1}_2019.pdf'
    courses = parse_timetable(pdf_source)
    buttons = []
    for c in courses:
        buttons.append(CourseButton(c, w_table, i))
    buttons.sort(key=lambda b: b.name)
    for b in buttons:
        l_course_list.addWidget(b)


l_main.addWidget(s_course_list, 1, 0)
l_main.addWidget(w_table, 1, 1)
l_main.addWidget(info_box, 2, 0)
l_main.addWidget(w_credits, 2, 1)

window.show()
exit(app.exec_())
