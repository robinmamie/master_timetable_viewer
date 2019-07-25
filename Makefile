all: clean timetable shortcut

DEPS = master_timetable_viewer.py
EXEC = master_timetable_viewer

timetable: $(DEPS)
	pyinstaller --windowed $^;

shortcut:
	ln -s dist/$(EXEC)/$(EXEC) $(EXEC);

clean:
	rm -rf build dist $(EXEC).spec $(EXEC);

onefile: $(DEPS)
	pyinstaller --onefile --windowed $^;

shortcut_onefile:
	ln -s dist/$(EXEC) $(EXEC);

compact: clean onefile shortcut_onefile
