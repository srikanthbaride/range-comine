.PHONY: install test plots lattice all

install:
	python -m pip install -U pip pytest matplotlib

test:
	pytest -q

plots:
	python experiments.py --mode min_prev --mins 0.3,0.5 --d1 8 --d2 25 --features 3 --instances 4 --seed 5 --algos range,naive --export_svg
	python experiments.py --mode range --min_prev 0.5 --d1s 3 --d2s 6,8 --csv examples/toy.csv --algos range,naive --export_svg

lattice:
	python lattice_export.py --outfile lattice_demo --d1 8 --d2 30 --min_prev 0.5 --features 4 --instances 5 --seed 7 --cross_level --png

all: install test plots lattice


lock:
	pip install -r requirements.txt && pip freeze > requirements.lock

docker-build:
	docker build -t range-comine:latest .

docker-test:
	docker run --rm -v $(PWD)/plots:/app/plots range-comine:latest

docker-minprev:
	docker run --rm -v $(PWD)/plots:/app/plots range-comine:latest \
		python experiments.py --mode min_prev --mins 0.3,0.5 --d1 8 --d2 25 --features 3 --instances 4 --seed 5 --algos range,naive --export_svg

docker-range:
	docker run --rm -v $(PWD)/plots:/app/plots range-comine:latest \
		python experiments.py --mode range --min_prev 0.5 --d1s 3 --d2s 6,8 --csv examples/toy.csv --algos range,naive --export_svg

docker-lattice:
	docker run --rm -v $(PWD)/plots:/app/plots range-comine:latest \
		python lattice_export.py --outfile lattice_demo --d1 8 --d2 30 --min_prev 0.5 --features 4 --instances 5 --seed 7 --cross_level --png