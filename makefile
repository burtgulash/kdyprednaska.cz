.PHONY: db fetch compile all css clean 

all: compile-events compile-pages
db:
	cat db.sql | psql -d prednavse -U io -W
fetch:
	./fetch.py
compile-events: css clean
	./compile.py > dist/index.html
compile-pages:  css clean
	./compile_pages.py > dist/kluby.html
css: clean
	mkdir -p dist/css
	sassc s.scss dist/css/style.css
clean:
	if [ -d dist ]; then rm -r dist; fi
	mkdir -p dist
