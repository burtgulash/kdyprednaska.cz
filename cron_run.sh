cd $1
./fetch.py
./compile.py > $1/dist/index.html
./compile_pages.py > $1/dist/kluby.html
