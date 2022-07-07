# -*- coding: utf-8 -*-
import os, json, multiline
from app import app

MODULE_FOLDER = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

data_folder = os.path.join(app.config['APP_DATA_PATH'], MODULE_FOLDER)
if not os.path.exists(data_folder):
    os.mkdir(data_folder)


# SCHEDULE = "scedule"
# CRON = "cron"


class Jobs:

	def __init__(self, daemon):
		# инструмент с помощью которого выполняются команды
		self.daemon = daemon

		self.data_folder = os.path.join(data_folder, self.daemon)
		if not os.path.exists(self.data_folder):
			os.mkdir(self.data_folder)

		self.daemon_json = self.daemon + ".json"
		self._file = os.path.join(self.data_folder, self.daemon_json)


	def get_job_data(self):
		if not os.path.exists(self._file):
			with open(self._file, 'w', encoding="utf-8") as _fp:
				_fp.write('{}')
		with open(self._file, "r", encoding="utf-8") as f:
			return multiline.load(f, multiline=True)


	def edit_job_data(self, data):
		with open(self._file, "w", encoding="utf-8") as f:
			json_text = json.dumps(data, indent='\t', ensure_ascii=False)
			json_text = json_text.replace('\\n', '\n').replace('\\r', '')
			f.write(json_text)



	def get_job_object(self, _id):
		data = self.get_job_data()
		return data[_id] if _id in data else {}


	def delete_job_object(self, _id):
		data = self.get_job_data()
		if _id in data:
			data.pop(_id)
			self.edit_job_data(data)



	def edit_job_object(self, _id, values={}):
		data = self.get_job_data()
		if _id not in data:
			data[_id] = {}

		for key in values:
			data[_id][key] = values[key]

		self.edit_job_data(data)

