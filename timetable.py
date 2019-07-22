from course_parsing import parse_timetable

def create_table():
    table = []
     for i in range(11):
        row = []
        for i in range(5):
            row.append([])
        table.append(row)
    return table

def build_timetable(courses, name):
    m = parse_timetable(name)
    slots = [i for i in m if i.code and i.code in courses]

    timetable = create_table()

    for i in slots:
        for j in i.get_hour():
            timetable[j][i.day].append(i)
