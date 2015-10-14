.PHONY: db fetch compile all css clean 

all: compile-events compile-pages
db:
	cat db.sql | psql -d prednavse -U io -W
fetch:
	./fetch.py
compile-events: css clean
	./compile.py > index.html
compile-pages:  css clean
	./compile_pages.py > kluby.html
css: clean
	mkdir -p css
	sassc s.scss css/style.css
clean:
	rm -r css
	rm index.html
