from enum import Enum, unique
from django.db.models import Q
import tempfile
from datetime import datetime
# from import_export.tmp_storages import TempFolderStorage


# class Utf8TempFolderStorage(TempFolderStorage):
#     def open(self, mode='r'):
#         if self.name:
#             return open(self.get_full_path(), mode, encoding='utf-8')
#         else:
#             tmp_file = tempfile.NamedTemporaryFile(delete=False)
#             self.name = tmp_file.name
#             return tmp_file


def make_json_convertible(data):
    out_data = data
    if isinstance(data, datetime):
        out_data = data.isoformat()
    elif isinstance(data, set):
        out_data = list(data)
    elif isinstance(data, dict):
        out_data = {}
        for k, v in data.items():
            out_data[k] = make_json_convertible(v)
    elif isinstance(data, list):
        out_data = [make_json_convertible(it)
                    for it in data]
    return out_data
