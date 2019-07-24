from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QAbstractScrollArea, QTextEdit, QTabWidget
import re
from sys import exit
from urllib.request import urlopen


## CONSTANTS ##

PROGRAM_NAME = 'Master Timetable Viewer'
"""Name of the program."""

M1_FILE = 'm1_2019.pdf'
"""Link to the fall semester timetable."""

M2_FILE = 'm2_2019.pdf'
"""Link to the spring semester timetable."""

LINK_CS = 'https://edu.epfl.ch/studyplan/en/master/computer-science'
"""Link to the study plan."""

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
"""List of the weekdays' English names."""

RE_HOUR = '[0-9]{2}:[0-9]{2}'
"""Regular expression used to retrieved the hour from the pdf timetable."""

PFX_TEACHER = 'Enseignant-e-(s):'
"""Prefix to all teachers' names in the pdf timetable."""


## BACKEND ##

def fetch_online_study_plan():
    """
    Fetches the online information about the study plans.

    Returns a quadruple withname, credits, course code and specializations.
    """
    page_source  = urlopen(LINK_CS).read()
    soup         = BeautifulSoup(page_source, 'html.parser')
    main_content = soup.find('body').find('div', {'id': 'main-content'})
    content      = main_content.find('div', {'id': 'content'})

    courses = {}

    for c in content.findAll('div', {'class', 'line-down'}):
        course_name = c.find('div', {'class', 'cours-name'})
        name        = course_name.string
        if not name:
            name = course_name.find('a').string

        credits = c.find('div', {'class', 'credit-time'}).string

        code    = c.find('div', {'class', 'cours-code'}).string.strip()

        if not code:
            code = 'SHS'
        specializations = c.find('div', {'class', 'specialisation'})
        specs = []
        for s in specializations.findAll('img'):
            specs.append(s['src'].split('.gif')[0][-1])

        lower_name = name.replace(' ', '').lower()
        courses[lower_name] = (name, credits, code, specs)

    # Edge cases
    courses['dynamicalsystemtheoryforengineersexercices:travailindividuelouengroupenonplanifiéàl\'horaire'] = ('Dynamical system theory for engineers', 4, 'COM-502', [])
    courses['machinelearningthefirstcourse(september18)willtakeplaceintheforumofrolexlearningcenter'] = ('Machine learning', 7, 'CS-433', ['b', 'f', 'i', 'j'])
    # Manual entries, but they are already present. Used to change the name.
    # They are not present in the PDF, since it acts as a timetable.
    courses['pdm'] = ('Master Project', 30, 'CS-599', [])
    courses['spro'] = ('Semester Project', 12, 'CS-498', [])
    courses['opro'] = ('Optional Project', 8, 'CS-596', [])

    return courses

course_dict = fetch_online_study_plan()

class Course:

    def __init__(self, name, day, start, end, isLecture, isObligatory, teacher):
        course            = course_dict.get(name, (name, 0, None))
        self.name         = course[0].strip()
        self.day          = int(day)
        self.start        = int(start)
        self.end          = int(end)
        self.isLecture    = bool(isLecture)
        self.isObligatory = bool(isObligatory)
        self.teacher      = teacher
        self.credits      = int(course[1])
        self.code         = course[2]
        self.specs        = course[3]

    def get_hour(self):
        start = self.start // 100 - 8
        end   = self.end // 100 - 8
        return range(start, end)

    def __str__(self):

        def time(time):
            return f'{time//100:02}:{time%100:02}'

        lec = 'lecture session' if self.isLecture else 'exercise/project session'
        obl = 'obligatory' if self.isObligatory else 'optional'

        return f'''{self.code} / {self.name}, {self.teacher} ({self.credits} credits): {WEEKDAYS[self.day]} {time(self.start)}-{time(self.end)}, is an {obl} {lec}'''


def extract_timetable(name):

    pdf_reader = PdfFileReader(open(name, 'rb'))
    pdf_text   = [pdf_reader.getPage(i).extractText() for i in range(pdf_reader.getNumPages())]

    raw_text   = ''.join(pdf_text).replace('\n','')
    days       = re.split('LUNDI|MARDI|MERCREDI|JEUDI|VENDREDI', raw_text)[1:]

    return [re.split(f'(?={RE_HOUR}-)', day)[1:] for day in days]


def parse_timetable(name):
    week = extract_timetable(name)
    slots = []

    # TODO SHS breaks everything...
    for day, d in zip(week, range(len(week))):
        for slot in day:
            hours = re.search(f'{RE_HOUR}-{RE_HOUR}', slot)[0].replace(':', '').split('-')

            temp = slot.split(PFX_TEACHER)
            teacher = re.sub(r'(\w)([A-Z])', r'\1 \2', temp[1]) if len(temp) > 1 else None

            temp = re.split('OPT|OBL', temp[0])
            c_name = temp[1] if len(temp) > 1 else 'HSS:introductiontoproject'
            # Edge case (m1_2019.pdf)
            if c_name == 'MachinelearningThefirstweek,courseswilltakeplaceintheForumofRolexLearningCenter':
                c_name = 'machinelearning'
            if c_name == 'Moderndigitalcommunications:ahands-on':
                c_name = 'moderndigitalcommunications:ahands-onapproach'

            c_name = c_name.lower()
            if course_dict.get(c_name):
                isLecture = temp[0][-1] == 'C'

                isObligatory = True
                obl = re.search('OPT|OBL', slot)
                if obl:
                    isObligatory = obl[0] == 'OBL'

                c = Course(c_name, d, hours[0], hours[1], isLecture, isObligatory, teacher)
                slots.append(c)

    courses = []
    for s in slots:
        added = False
        for c in courses:
            if s.name == c[0].name:
                c.append(s)
                added = True
                break
        if not added:
            courses.append([s])

    # Add manual entries of projects
    courses.append([Course('pdm', -1, -1, -1, False, False, 'None')])
    courses.append([Course('spro', -1, -1, -1, False, False, 'None')])
    courses.append([Course('opro', -1, -1, -1, False, False, 'None')])
    return courses


## FRONTEND ##

class CourseInfoBox(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)


class TableView(QTableWidget):

    def __init__(self, data, *args):
        super().__init__(*args)
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
            for d in WEEKDAYS:
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
        super().__init__(name)
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
                day = WEEKDAYS[c.day]
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

        courses = [parse_timetable(M1_FILE), parse_timetable(M2_FILE)]

        for i in range(8):
            # Course list Layout
            w_cl = QWidget()
            tabs.addTab(w_cl, f'M{i+1}')
            l_course_list = QVBoxLayout(w_cl)
            w_cl.setLayout(l_course_list)
            l_course_list.addStretch()

            # Course parsing & buttons
            courses_current = courses[i%2]
            buttons = []
            for c in courses_current:
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


def main():
    app = QApplication([PROGRAM_NAME])
    window = TimetableViewer()
    window.show()
    exit(app.exec_())

if __name__ == '__main__':
    main()
