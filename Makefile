define ANNOUNCE_BODY
Required section:
 build - build project into build directory, with configuration file and environment
 clean - clean all addition file, build directory and output archive file
 test - run all tests
 pack - make output archivne
Addition section:
endef

PROJECT_NAME=clisearch

BASE_DIST_URL := http://192.168.4.178:8089/releases

ot_simple_connector_URL := $(BASE_DIST_URL)/ot_simple_connector/master/ot_simple_connector-0.1.1-master-specialfix.tar.gz

tmp_path := tmp

GENERATE_VERSION = $(shell cat clisearch/clisearch.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')

SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

#.SILENT:

COMPONENTS := ot_simple_connector

define GetPack
	@echo "Getting archive for $(1) and unpack"
	mkdir -p $(tmp_path)/$(1) && curl $($(1)_URL) | tar zxv --directory=$(tmp_path)/$(1)
endef

export ANNOUNCE_BODY
all:
	echo "$$ANNOUNCE_BODY"

pack: make_build
	$(SET_BRANCH)
	#$(SET_VERSION)
	echo Create archive \"$(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz\"
	@#cd build; tar czf ../$(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz $(PROJECT_NAME)*.run
	cd make_build; tar czf ../$(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz clisearch

build: make_build

make_build: $(COMPONENTS:%=$(tmp_path)/%) dist venv
	# required section
	@echo make_build!
	mkdir make_build
	mkdir make_build/$(PROJECT_NAME)
	cp dist/clisearch make_build/$(PROJECT_NAME)
	cp clisearch/clisearch.cfg make_build/$(PROJECT_NAME)/clisearch.cfg.example
#	cp -r ./$(PROJECT_NAME)/* ./build/$(PROJECT_NAME)
#	mv ./build/$(PROJECT_NAME)/benchmark.cfg ./build/$(PROJECT_NAME)/benchmark.cfg.example
#	cp README.md build/$(PROJECT_NAME)/
#	cp CHANGELOG.md build/$(PROJECT_NAME)/
	cp LICENSE.md make_build/$(PROJECT_NAME)/

$(tmp_path)/ot_simple_connector:
	$(call GetPack,$(@:$(tmp_path)/%=%))

clisearch/ot_simple_connector: $(tmp_path)/ot_simple_connector
	cp -r $(tmp_path)/ot_simple_connector/ot_simple_connector clisearch/ot_simple_connector


dist: venv
	#./venv/bin/pyinstaller --runtime-tmpdir ./tmp --hidden-import=_cffi_backend -F clisearch/clisearch.py
	./venv/bin/pyinstaller --hidden-import=_cffi_backend -F clisearch/__main__.py

venv:
	echo Create venv
	#mkdir -p /opt/otp/otp_benchmarks
	#python3 -m venv --copies /opt/otp/otp_benchmarks/venv
	python3 -m venv ./venv
	. ./venv/bin/activate
	./venv/bin/python3 -m pip install --upgrade pip setuptools wheel
	./venv/bin/python3 -m pip install -r requirements.txt
	#cp -r /opt/otp/otp_benchmarks/venv venv

publish: venv
	#mv ./clisearch/clisearch.py ./clisearch/__main__.py
	./venv/bin/python3 ./setup.py sdist bdist_wheel
	#mv ./clisearch/__main__.py ./clisearch/clisearch.py

clean: $(COMPONENTS:%=.clean.%)
	# required section"
	find . -type d -name '*pycache*' -not -path '*venv*' | xargs rm -rf
	rm -rf build $(PROJECT_NAME)-*.tar.gz  venv make_build tmp clisearch/ot_simple_connector dist *.spec

.clean.ot_simple_connector:
	rm -rf $(tmp_path)/$(@:.clean.%=%)

test: venv
	echo "Testing..."
	export PYTHONPATH=./clisearch/:./tests/; ./venv/bin/python -m unittest

clean_test: clean_venv
	echo "Cleaning after test..."


create_sfx: build
	@echo $@
	$(SET_BRANCH)
	#$(SET_VERSION)
	cp sfx_scripts/install.sh ./build
	chmod +x ./build/install.sh
	@#cd build; makeself ./$(PROJECT_NAME) $(PROJECT_NAME)-$(VERSION)-$(BRANCH).run "OTP Benchmark" ./install.sh
	makeself build $(PROJECT_NAME)-$(VERSION)-$(BRANCH).run "OTP Benchmark" ./install.sh
