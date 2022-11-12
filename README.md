This was for a small project I had. Gives a user an interface to upload files, then compare them to a sql entry, if good, move to where it used to live (it was removed), otherwise pop into a folder for future use.

There's also an indexer to find out what files are missing, simply get dumped into meilisearch for viewing.

Tech used: 
 - mariadb
 - flask
 - celery
 - meilisearch
 - redis

In "prod" this sits behind caddy, using supervisor to run the application using gunicorn.

Highly doubt this will be useful to someone, but feel free to steal what you like!