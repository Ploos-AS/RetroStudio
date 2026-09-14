.PHONY: check check-m0 check-m1 check-m2 check-m3 check-m4 check-m5 test run

check: check-m0 check-m1 check-m2 check-m3 check-m4 check-m5

check-m0:
	python3 scripts/check_m0.py

check-m1: test

check-m2: test

check-m3: test

check-m4: test
	python3 scripts/check_m4.py

check-m5: test
	python3 scripts/check_m5.py

test:
	python3 -m unittest discover -s tests -v

run:
	python3 -m retrostudio.desktop
