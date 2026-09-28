.PHONY: setup analysis dashboard clean

setup:
	pip install -r requirements.txt

analysis:
	python load_data.py
	python initial_analysis.py
	python statistical_analysis.py
	python subset_analysis.py

dashboard:
	streamlit run dashboard.py --server.headless true

clean:
	rm -f cell-data.db summary_table.csv boxplot.pdf
