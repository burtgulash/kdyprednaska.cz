.PHONY: db fetch compile all css clean 

all: css compile-events compile-pages
db:
	cat db.sql | psql -d kdyprednaska -U io -W
fetch:
	./fetch.py
compile-events:
	./compile.py > dist/index.html
compile-pages:
	./compile_pages.py > dist/kluby.html
css:
	mkdir -p dist/css
	sassc s.scss dist/css/style.css
clean:
	if [ -d dist ]; then rm -r dist; fi
	mkdir -p dist
