cd $1

if [ ! -d "$1" ]
then
    echo directory \"$1\" does not exist!
    exit 1
fi

if [ ! -e "$2" ]
then
    echo config \"$2\" does not exist!
    exit 1
fi

./fetch.py -c $2
./compile.py -c $2
