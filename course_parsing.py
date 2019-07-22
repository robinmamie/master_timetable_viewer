from urllib.request import urlopen
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
import re

link_cs = 'https://edu.epfl.ch/studyplan/en/master/computer-science'

# TODO add specializations

def get_courses():
    page_source  = urlopen(link_cs).read()
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

    return courses



weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
re_hour = '[0-9]{2}:[0-9]{2}'
re_enseignant = 'Enseignant-e-(s):'

course_dict = get_courses()

class Course:

    def __init__(self, name, day, start, end, isLecture, isObligatory, teacher):
        course            = course_dict.get(name.lower(), (name, 0, None))
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

        return f'''{self.code} / {self.name}, {self.teacher} ({self.credits} credits): {weekdays[self.day]} {time(self.start)}-{time(self.end)}, is an {obl} {lec}'''


def extract_timetable(name):

    pdf_reader = PdfFileReader(open(name, 'rb'))
    pdf_text   = [pdf_reader.getPage(i).extractText() for i in range(pdf_reader.getNumPages())]

    raw_text   = ''.join(pdf_text).replace('\n','')
    days       = re.split('LUNDI|MARDI|MERCREDI|JEUDI|VENDREDI', raw_text)[1:]

    return [re.split(f'(?={re_hour}-)', day)[1:] for day in days]


def parse_timetable(name):
    week = extract_timetable(name)
    slots = []

    # TODO SHS breaks everything...
    for day, d in zip(week, range(len(week))):
        for slot in day:
            hours = re.search(f'{re_hour}-{re_hour}', slot)[0].replace(':', '').split('-')

            temp = slot.split(re_enseignant)
            teacher = re.sub(r'(\w)([A-Z])', r'\1 \2', temp[1]) if len(temp) > 1 else None

            temp = re.split('OPT|OBL', temp[0])
            c_name = temp[1] if len(temp) > 1 else 'HSS:introductiontoproject'
            # Edge case (m1_2019.pdf)
            if c_name == 'MachinelearningThefirstweek,courseswilltakeplaceintheForumofRolexLearningCenter':
                c_name = 'Machinelearning'
            if c_name == 'Moderndigitalcommunications:ahands-on':
                c_name = 'moderndigitalcommunications:ahands-onapproach'

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

    return courses
