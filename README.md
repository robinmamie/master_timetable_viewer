# Master Timetable Viewer

The Master Timetable Viewer allows EPFL Master students to build their timetable interactively.
It displays all necessary informations (timetable, credits, etc.)

Currently only available for the computer science EPFL master.

## Launch


To launch the program, verify that the following python packages are installed:

* PyQt5, used for the graphical interface;
* urllib, used to retrieve the study plan from the Internet;
* bs4, used to parse the retrieved study plan;
* PyPDF2, used to parse the pdf timetables.

Then, please type the following in a terminal:

    python master_timetable_viewer.py

## Known issues

The course "Information Security and Privacy" is displayed both as a fall and spring semester course, and can be selected in 2 semesters (if they are not during the same part of the year), which should not happen.
Starting from the second half of 2019, the course is given during the fall semester and not during the spring one as previously.
Since the program bases itself on previous semesters' timetables, it cannot take it into account.
Please ignore the course during the spring semesters (even numbered semesters in this case).

## Roadmap

Todo:

* Add more constraints (no PDM when more than 8 credits, etc)
* Save feature
* Offer offline HTML page of study plans
* Implement an automatic conflict resolver
* Take minors into account(?) -> would build the path for other masters
* Choose which master to look at, alternatively specify the link of the study plans
