# utils/helpers.py

import os

def clean_query(query):
    return query.strip().lower()

def check_file_exists(filepath):
    return os.path.isfile(filepath)

def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")