define ANNOUNCE_BODY
Required section:
 build - build project into build directory, with configuration file and environment
 clean - clean all addition file, build directory and output archive file
 test - run all tests
 pack - make output archivne
Addition section:
endef

PROJECT_NAME=otp_benchmarks
VERSION=0.0.1

#GENERATE_VERSION = $(shell jq .version ./${PROJECT_NAME}/package.json )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')

#SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

#.SILENT:

COMPONENTS :

export ANNOUNCE_BODY
all:
	echo "$$ANNOUNCE_BODY"

pack: create_sfx
	$(SET_BRANCH)
	#$(SET_VERSION)
	echo Create archive \"$(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz\"
	@#cd build; tar czf ../$(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz $(PROJECT_NAME)*.run
	tar czf $(PROJECT_NAME)-$(VERSION)-$(BRANCH).tar.gz $(PROJECT_NAME)*.run ReadMe.txt

build: $(COMPONENTS) venv
	# required section
	@echo Build!
	mkdir build
	mkdir build/$(PROJECT_NAME)
	cp -r ./venv ./build/$(PROJECT_NAME)
	cp -r ./$(PROJECT_NAME)/* ./build/$(PROJECT_NAME)
	mv ./build/$(PROJECT_NAME)/benchmark.cfg ./build/$(PROJECT_NAME)/benchmark.cfg.example
	git lfs fetch
	cp dataset/benchmark_index_single_bucket_single_parquet_file.tar.gz dataset/benchmark_index_many_bucket_many_parquet_file_small.tar.gz dataset/benchmark_index_many_bucket_many_parquet_file_normal.tar.gz ./build
	cp README.md build/$(PROJECT_NAME)/
	cp CHANGELOG.md build/$(PROJECT_NAME)/
	cp LICENSE.md build/$(PROJECT_NAME)/

venv:
	echo Create venv
	mkdir -p /opt/otp/otp_benchmarks
	python3 -m venv --copies /opt/otp/otp_benchmarks/venv
	/opt/otp/otp_benchmarks/venv/bin/pip3 install -r requirements.txt
	cp -r /opt/otp/otp_benchmarks/venv venv

clean:
	# required section"
	find . -type d -name '*pycache*' -not -path '*venv*' | xargs rm -rf
	rm -rf build $(PROJECT_NAME)-*.tar.gz $(PROJECT_NAME)-*.run venv /opt/otp/otp_benchmarks/venv

test:
	# required section
	@echo "Testing..."
	@#echo $(PROJECT_NAME)

create_sfx: build
	@echo $@
	$(SET_BRANCH)
	#$(SET_VERSION)
	cp sfx_scripts/install.sh ./build
	chmod +x ./build/install.sh
	@#cd build; makeself ./$(PROJECT_NAME) $(PROJECT_NAME)-$(VERSION)-$(BRANCH).run "OTP Benchmark" ./install.sh
	makeself build $(PROJECT_NAME)-$(VERSION)-$(BRANCH).run "OTP Benchmark" ./install.sh
