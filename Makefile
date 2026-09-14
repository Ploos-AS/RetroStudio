.PHONY: check check-m0 check-m1 check-m2 test

check: check-m0 check-m1 check-m2

check-m0:
	python3 scripts/check_m0.py

check-m1: test

check-m2: test


test:
	python3 -m unittest discover -s tests -v
