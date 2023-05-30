BINDIR := `echo ~/bin`

default :
	echo BINDIR=${BINDIR}

install :
	python3 script-to-bin.py script-to-bin.py ${BINDIR}
