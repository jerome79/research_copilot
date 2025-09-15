dev:
    python -m pip install -r requirements.txt

test:
    pytest -q

run:
    streamlit run app/ui_streamlit.py
