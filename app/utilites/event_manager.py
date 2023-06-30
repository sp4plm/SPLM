# -*- coding: utf-8 -*-
import threading
import re


# Реализация через threading.Event()
class EventManager:
	"""
	Класс реализует событийную модель

	"""
	event_start = "event_start"
	event_complete = "event_complete"
	handler = "handler"
	event_name_regex = r'^[A-Za-z0-9_]+$'

	# Хранение Событий
	events = {}
	# СХЕМА
	# {
	# 	"event_name1" : [
	# 		{
	# 			"event_start" : event_start1,
	# 			"event_complete" : event_complete1,
	# 			"handler" : hander1
	# 		},
	# 		{
	# 			"event_start" : event_start2,
	# 			"event_complete" : event_complete2,
	# 			"handler" : hander2
	# 		}
	# 	]
	# 	"event_name2" : 
	# }
	# Параметры для обработчика хранятся в event_start.params

	def __new__(cls):
		"""
		Метод проверяет что существует только один экземпляр класса EventManager

		"""
		if not hasattr(cls, 'instance'):
			cls.instance = super(EventManager, cls).__new__(cls)
		return cls.instance

	def check_event_name(self, event_name):
		"""
		Метод проверяет что в event_name есть только символы A-Za-z0-9_

		:param str event_name: имя события
		:return: True/False
		:rtype: bool
		"""
		if not isinstance(event_name, str):
			try:
				event_name = str(event_name)
			except:
				return False

		if not re.findall(self.event_name_regex, event_name):
			return False

		return True

	def define_thread(self, event_start, event_complete, handler):
		"""
		Метод создает процесс с обработчиком и запускает его

		:param threading.Event event_start: событие начала работы обработчика handler
		:param threading.Event event_complete: событие окончания работы обработчика handler
		:param def handler: функция-обработчик события event
		"""
		# запускаем процесс с ожиданием события
		class event_thread(threading.Thread):
			def __init__(self):
				threading.Thread.__init__(self)
				self.daemon = True # Will be stopped abruptly on program exit
			def run(self):
				while True:
					event_start.wait() # print("Wait function " + handler.__name__)
					event_start.clear()
					
					# print("Call function " + handler.__name__)
					try:
						event_complete.params = handler(event_start, event_start.params) # print("Function " + handler.__name__ + " done")
					except Exception as e:
						pass
					
					event_complete.set()


		t = event_thread()
		t.start()

	def register_event(self, event_name, handler):
		"""
		Метод регистрирует событие с именем event_name и функцией-обработчиком handler
		
		:param str event_name: имя события
		:param def handler: функция-обработчик события event_start
		"""
		if not self.check_event_name(event_name):
			return False

		event_start = None
		if event_name not in list(self.events.keys()):
			self.events[event_name] = []
			event_start = threading.Event()
		else:
			event_start = self.events[event_name][-1][self.event_complete]

		event_complete = threading.Event()

		self.events[event_name].append({self.event_start : event_start, self.event_complete : event_complete, self.handler : handler})

		self.define_thread(event_start, event_complete, handler)


	def get_event(self, event_name):
		"""
		Метод возвращает экземпляр события event, зарегистрированного под именем event_name
	
		:param str event_name: имя события
		:return: event_start, event_complete - события начала и окончания работы обработчика
		:rtype: threading.Event
		"""
		event_start = self.events[event_name][0][self.event_start]
		event_complete = self.events[event_name][-1][self.event_complete]
		return event_start, event_complete


	def raise_event(self, event_name, params = {}):
		"""
		Метод вызывает событие, зарегистрированное под именем event_name
	
		:param str event_name: имя события
		:param dict params: параметры для функции-обработчика

		:return: params
		:rtype: dict
		"""
		if not self.check_event_name(event_name):
			return params

		if event_name not in list(self.events.keys()):
			return params

		# где event_start - самое первое событие
		# где event_complete - самое последнее событие

		event_start, event_complete = self.get_event(event_name)
		# Передаем параметры params в событие
		event_start.params = params

		# Отрабатываем событие вызова get_top_navi
		# print("Raise Event")

		# Вызываем Событие event
		event_start.set()

		# Ждем пока отработают все обработчики События event

		event_complete.wait()
		event_complete.clear()

		# print("All handlers done")
		return event_complete.params












