all: lib run

run:
	dev_appserver.py .

lib:
	pip install -r requirements.txt -t lib/

test:
	python test.py ~/google-cloud-sdk/platform/google_appengine/ tests/

clean:
	$(RM) -rf *~ *.pyc lib
	$(RM) -rf $(shell find . -name *~)
	$(RM) -rf $(shell find . -name *pyc)
