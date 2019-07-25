all: timetable shortcut

DEPS = master_timetable_viewer.py
EXEC = master_timetable_viewer

timetable: $(DEPS)
	pyinstaller --windowed $^;

shortcut:
	ln -s dist/$(EXEC)/$(EXEC) $(EXEC);

clean:
	rm -rf build dist $(EXEC).spec $(EXEC);
