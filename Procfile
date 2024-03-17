web: flask db upgrade; flask translate compile; gunicorn flaskproject:app
worker: rq worker -u $REDIS_URL microblog-tasks