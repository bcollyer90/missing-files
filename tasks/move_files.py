import os

import pymysql
import glob
import re
import shutil
from settings import *
from celery import shared_task


def crc32(s: str):
    return re.search('[A-Za-z0-9]{8}', s).group(0)


def crc32_in_brackets(s: str):
    return re.search(r'\[[a-zA-Z0-9]{8}]', s).group(0)


@shared_task(name='tasks.move_files')
def move_files():
    restored = []
    connection = pymysql.connect(host=mysql_host,
                                 user=mysql_user,
                                 password=mysql_password,
                                 database=mysql_database,
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)

    os.chdir(upload_folder)

    with connection:
        with connection.cursor() as cursor:
            for file in glob.glob("*.*"):
                clean_crc32 = crc32(os.popen(f'crc32 "{file}"').read()).lower()
                cursor.execute(f"select * from files where name like '%{clean_crc32}%'")
                db_file = cursor.fetchone()

                if not db_file:
                    clean_crc32 = clean_crc32.upper()
                    cursor.execute(f"select * from files where name like '%{clean_crc32}%'")
                    db_file = cursor.fetchone()

                if not db_file:
                    shutil.move(file, f"new/{file}")
                    continue
                local_crc32 = crc32(os.popen(f'crc32 "{file}"').read())
                try:
                    db_crc32 = crc32_in_brackets(db_file.get('name')[2:])
                except:
                    continue
                if local_crc32.lower() in db_crc32.lower():
                    path = "/home/user/files"
                    shutil.move(file, f"{path}/{db_file.get('name')}")
                    cursor.execute(f"update files set server_id = 8 where id = {db_file.get('id')}")
                    restored.append(db_file.get("name"))
    return {"restored": restored}
