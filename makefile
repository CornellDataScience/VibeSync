db:
	uv run backend/database.py

app:
	uv run streamlit run backend/app.py

scrape:
	uv run backend/scrape.py