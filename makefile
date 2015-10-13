.PHONY: db fetch compile all css clean

all: compile
db:
	cat db.sql | psql -d prednavse -U io -W
fetch:
	./fetch.py
compile: css clean
	./compile.py > index.html
css: clean
	mkdir -p css
	sassc s.scss css/style.css
clean:
	rm -r css
	rm index.html
