from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QAbstractScrollArea, QTextEdit, QTabWidget
from course_parsing import parse_timetable
from sys import exit

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

class CourseInfoBox(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)


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


class CreditTable(TableView):

    def __init__(self):
        credit_tally = {
            'tot': ['0', '120'],
            'pdm': ['0', '30'],
            'obl': ['0', '30'],
            'pro': ['0', '12'],
            'shs': ['0', '6']
        }
        for i in range(ord('a'), ord('k')):
            credit_tally[chr(i).upper()] = ['0', '30']
        for i in range(1,9):
            credit_tally[f'M{i}'] = ['0', '-']
        super().__init__([credit_tally], len(credit_tally['tot']), len(credit_tally))


class Timetable(TableView):

    def __init__(self):
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
        super().__init__(data, len(data[0]['Monday']), len(data[0]))


class CourseButton(QPushButton):
    def __init__(self, course, index, timetable, info_box, credit_table):
        name = course[0].name
        self.isProject = name == 'Master Project' or name == 'Semester Project' or name == 'Optional Project'
        if self.isProject:
            name = '# ' + name
        elif course[0].isObligatory:
            name = '* ' + name
        QPushButton.__init__(self, name)
        self.name = name
        self.course = course
        self.index = index
        self.setCheckable(True)
        self.timetable = timetable
        self.info_box = info_box
        self.credit_table = credit_table
        self.toggled.connect(self.handle_course)

    def handle_course(self):

        # Display Course
        if not self.isProject:
            for c in self.course:
                day = days[c.day]
                title = f'{self.name} '
                start = c.start // 100 - 8
                end = c.end // 100 - 8
                data = self.timetable.data
                for hour in range(start, end):
                    specific_title = title
                    specific_title += '(lec)' if c.isLecture else '(ex)'
                    specific_title += '\n'
                    if self.isChecked():
                        data[self.index][day][hour] += specific_title
                    else:
                        data[self.index][day][hour] = data[self.index][day][hour].replace(specific_title, "")
            self.timetable.setData(self.index)

        # Display Information
        c = self.course[0]
        info = f'-- {c.code} / {c.name} -- {c.credits} credits\n'
        info += f'Teacher : {c.teacher}\n'
        info += 'Is a project' if self.isProject else 'Is a core course' if c.isObligatory else 'Is an optional course'
        if c.specs:
            info += ', counting for specialization(s): '
            for s in c.specs:
                info += s.upper() + ' '
        self.info_box.setText(info)

        # Count Credits
        cred = c.credits if self.isChecked() else -c.credits
        tally = self.credit_table.data[0]

        def add_credits(name):
            tally[name][0] = str(int(tally[name][0]) + cred)

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
                add_credits(s.upper())
        self.credit_table.setData(0)




class CourseList(QScrollArea):

    def __init__(self, timetable, info_box, credit_table):
        super().__init__()
        course_list_widget = QTabWidget()
        self.setWidget(course_list_widget)
        self.setWidgetResizable(True)
        # TODO remove hardcoded numbers
        self.setFixedHeight(750)
        self.setFixedWidth(600)
        self.init_tabs(course_list_widget, timetable, info_box, credit_table)

    def init_tabs(self, tabs, timetable, info_box, credit_table):
        # Course tabs
        def tab_change(i):
            timetable.setData(i)
        tabs.currentChanged.connect(tab_change)


        for i in range(8):
            # Course list Layout
            w_cl = QWidget()
            tabs.addTab(w_cl, f'M{i+1}')
            l_course_list = QVBoxLayout(w_cl)
            w_cl.setLayout(l_course_list)
            l_course_list.addStretch()

            # Course parsing & buttons
            pdf_source = f'm{(i%2)+1}_2019.pdf'
            courses = parse_timetable(pdf_source)
            buttons = []
            for c in courses:
                button = CourseButton(c, i, timetable, info_box, credit_table)
                buttons.append(button)
            buttons.sort(key=lambda b: b.name)
            for b in buttons:
                l_course_list.addWidget(b)



class TimetableViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # TODO fill 90% of screen, at the center
        self.resize(1900,900)

        timetable = Timetable()
        info_box = CourseInfoBox()
        credit_table = CreditTable()
        course_list = CourseList(timetable, info_box, credit_table)

        main_layout = QGridLayout(main_widget)
        main_layout.addWidget(course_list, 1, 0)
        main_layout.addWidget(timetable, 1, 1)
        main_layout.addWidget(info_box, 2, 0)
        main_layout.addWidget(credit_table, 2, 1)





# COURSES
# Course Button




def main():
    app = QApplication(['Master Timetable Viewer'])
    window = TimetableViewer()
    window.show()
    exit(app.exec_())

if __name__ == '__main__':
    main()
