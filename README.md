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

    python timetable_viewer.py

## Roadmap

Todo:

* Add constraints (no double semester project, etc)
* Save feature
* Offer offline HTML page of study plans
* Implement an automatic conflict resolver
* Take minors into account(?) -> would build the path for other masters
* Choose which master to look at, alternatively specify the link of the study plans
