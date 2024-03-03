# -*- coding: utf-8 -*-
import os
import json
import multiline
import string
import random
from app import app, app_api
from app.utilites.extend_processes import ExtendProcesses

MODULE_FOLDER = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

data_folder = os.path.join(app.config['APP_DATA_PATH'], MODULE_FOLDER)
if not os.path.exists(data_folder):
	try: os.mkdir(data_folder)
	finally: pass


class Jobs:
	""" Класс позволяет работать с периодическими заданиями на базе Flask """

	def __init__(self, daemon):
		# инструмент с помощью которого выполняются команды
		self.daemon = daemon

		self.data_folder = os.path.join(data_folder, self.daemon)
		if not os.path.exists(self.data_folder):
			try: os.mkdir(self.data_folder)
			finally: pass

		self.daemon_json = self.daemon + ".json"
		self._file = os.path.join(self.data_folder, self.daemon_json)

	@staticmethod
	def get_executable_files():
		""" Получаем список доступных исполняемых файлов """
		query = """SELECT ?cron_lbl ?cron_file WHERE {
				?mod osplm:hasPathToCronExecutableFile ?mod_uri .
				?mod_uri rdfs:label ?cron_lbl .
				?mod_uri osplm:value ?cron_file .
				}"""

		# {"text" : <label>, "value" : <file>}
		executable_files = [
			{
				"text": str(item['cron_lbl']) + " - " + str(item['cron_file']),
				"value": str(item['cron_file'])
			}
			for item in app_api.get_mod_manager().query(query)
		]
		return executable_files

	@staticmethod
	def job_by_script(action):
		"""
		SCHEDULE
		Метод запускает питоновский скрипт отдельным процессом

		:param str action: путь до исполняемого скрипта
		"""
		log = os.path.join(app.config['APP_DATA_PATH'], "logs", "job_by_script.log")
		with open(log, "w", encoding="utf-8") as f:
			f.write("")

		script = os.path.join(app.config['APP_ROOT'], "app", action)
		ExtendProcesses.run(script, [], errors=log)

	@staticmethod
	def get_job_kwargs(id, job_item):
		"""
		SCHEDULE
		Получение параметров для запуска schedule

		:param str id: идентификатор
		:param dict job_item: настройки для задания
		"""
		# вычисляем период
		minute, hour, day, month, day_of_week = job_item['period'].split(' ')
		job_kwargs = {
			"id": id,
			"name": job_item['name'],
			"func": Jobs.job_by_script,
			"trigger": "cron",
			"day_of_week": day_of_week,
			"month": month,
			"day": day,
			"hour": hour,
			"minute": minute,
			"second": "0",
			"args": [job_item['action']]
		}
		return job_kwargs

	@staticmethod
	def create_job_id():
		""" Получаем случайную последовательность символов для id """
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

	@staticmethod
	def update_job(id, job_item, scheduler=None):
		""""""
		if 'active' in job_item and job_item['active'] == "1":
			if 'period' in job_item and 'action' in job_item and 'name' in job_item:
				try:
					if scheduler.get_job(id) is not None:
						# чтобы изменить задание - сначала удаляем его, потом создаем заново
						scheduler.remove_job(id)

					# запускаем активное задание
					scheduler.add_job(**Jobs.get_job_kwargs(id, job_item))
				except Exception as e:
					pass
		else:
			if scheduler.get_job(id) is not None:
				# чтобы изменить задание - сначала удаляем его, потом создаем заново
				scheduler.remove_job(id)

	def get_job_data(self):
		"""
		Метод возвращает все доступные задания

		:return: объект с заданиями
		:rtype: dict
		"""
		if not os.path.exists(self._file):
			with open(self._file, 'w', encoding="utf-8") as _fp:
				_fp.write('{}')
		with open(self._file, "r", encoding="utf-8") as f:
			return multiline.load(f, multiline=True)

	def edit_job_data(self, data):
		"""
		Метод изменяет журнал заданий

		:param dict data: объект с заданиями
		"""
		with open(self._file, "w", encoding="utf-8") as f:
			json_text = json.dumps(data, indent='\t', ensure_ascii=False)
			json_text = json_text.replace('\\n', '\n').replace('\\r', '')
			f.write(json_text)

	def get_job_object(self, _id):
		"""
		Метод возвращает задание c идентификатором _id

		:param str _id: идентификатор задания
		:return: объект задания
		"""
		data = self.get_job_data()
		return data[_id] if _id in data else {}

	def delete_job_object(self, _id):
		"""
		Метод удаляет задание c идентификатором _id

		:param str _id: идентификатор задания
		"""
		data = self.get_job_data()
		if _id in data:
			data.pop(_id)
			self.edit_job_data(data)

	def edit_job_object(self, _id, values={}):
		"""
		Метод изменяет задание c идентификатором _id

		:param str _id: идентификатор задания
		:param dict values: новое задание
		"""
		data = self.get_job_data()
		if _id not in data:
			data[_id] = {}

		for key in values:
			data[_id][key] = values[key]

		self.edit_job_data(data)
