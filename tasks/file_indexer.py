import pymysql.cursors
from os.path import exists
import meilisearch
from settings import *
from celery import shared_task

servers = [
    {"id": 8, "path": "/home/user/files"},
    {"id": 7, "path": "/files-2"}
]


def get_path(i: int) -> str:
    for s in servers:
        if s.get('id') == i:
            return s.get('path')


def get_files_for_show(c, show_id: int, server_id: int) -> dict:
    c.execute(f"select * from files where server_id = {server_id} and show_id = {show_id}")
    return c.fetchall()


def is_missing(file: dict) -> bool:
    p = get_path(file.get('server_id'))
    if not exists(f"{p}/{file.get('name')}"):
        return True
    return False


@shared_task(name='tasks.index_missing_files')
def index_missing_files():
    client = meilisearch.Client(meilisearch_url, meilisearch_key)

    connection = pymysql.connect(host=mysql_host,
                                 user=mysql_user,
                                 password=mysql_password,
                                 database=mysql_database,
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)

    shows = []

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from x")
            results = cursor.fetchall()
            for s in results:
                d = {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "image": {s.get('image')},
                    "files": []
                }
                x = get_files_for_show(cursor, s.get("id"), 7)
                for f in x:
                    if is_missing(f):
                        d["files"].append({"name": f.get("name"), "server_id": f.get("server_id")})
                y = get_files_for_show(cursor, s.get("id"), 8)
                for f in y:
                    if is_missing(f):
                        d["files"].append({"name": f.get("name"), "server_id": f.get("server_id")})
                if len(d["files"]) > 0:
                    shows.append(d)

    client.delete_index('missing-files-by-x')
    index = client.index('missing-files-by-x')
    index.add_documents(shows)
