all: lib run

run:
	dev_appserver.py .

lib:
	pip install -r requirements.txt -t lib/

clean:
	$(RM) -rf *~ *.pyc lib
	$(RM) -rf $(shell find . -name *~)
	$(RM) -rf $(shell find . -name *pyc)
