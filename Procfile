web: gunicorn --bind :8000 --workers 2 web:app
beat: celery -A app.myapp beat -l INFO
wrk: celery -A app.myapp worker -l INFO -Q default_static
