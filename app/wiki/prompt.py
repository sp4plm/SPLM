import markdown2
import multiline

def _help():
	result = ""
	result += markdown2.markdown("## Справка для wiki - основные команды")

	_help = """
	# H1
	## H2
	### H3
	#### H4
	##### H5
	###### H6

	Кроме того, H1 и H2 можно обозначить подчеркиванием:

	Alt-H1
	======

	Alt-H2
	------
	"""

	_help1 = """
# H1
## H2
### H3
#### H4
##### H5
###### H6

Кроме того, H1 и H2 можно обозначить подчеркиванием:

Alt-H1
======

Alt-H2
------
"""
	result += markdown2.markdown("----")
	result += markdown2.markdown("## Заголовки") + markdown2.markdown(_help) + markdown2.markdown(_help1) 

	_help = """
	Курсив обозначается *звездочками* или _подчеркиванием_.

	Полужирный шрифт - двойными **звездочками** или __подчеркиванием__.

	Комбинированное выделение **звездочками и _подчеркиванием_**.
	"""

	_help1 = """
Курсив обозначается *звездочками* или _подчеркиванием_.

Полужирный шрифт - двойными **звездочками** или __подчеркиванием__.

Комбинированное выделение **звездочками и _подчеркиванием_**.
"""
	result += markdown2.markdown("----")
	result += markdown2.markdown("### Выделение") + markdown2.markdown(_help) + markdown2.markdown(_help1) 

	_help = """
	(В данном примере предшествующие и завершающие пробелы обозначены точками: ⋅)

	1. Первый пункт нумерованного списка
	2. Второй пункт
	⋅⋅*Ненумерованный вложенный список.
	1. Сами числа не имеют значения, лишь бы это были цифры
	⋅⋅1. Нумерованный вложенный список
	4. И еще один пункт.

	⋅⋅⋅Внутри пунктов списка можно вставить абзацы с таким же отступом. Обратите внимание на пустую строку выше и на пробелы в начале (нужен по меньшей мере один, но здесь мы добавили три, чтобы также выровнять необработанный Markdown).

	⋅⋅⋅Чтобы вставить разрыв строки, но не начинать новый параграф, нужно добавить два пробела перед новой строкой.⋅⋅
	⋅⋅⋅Этот текст начинается с новой строки, но находится в том же абзаце.⋅⋅
	⋅⋅⋅(В некоторых обработчиках, например на Github, пробелы в начале новой строки не нужны.)

	* Ненумерованный список можно размечать звездочками
	- Или минусами
	+ Или плюсами
	"""

	_help1 = """
(В данном примере предшествующие и завершающие пробелы обозначены точками: ⋅)

1. Первый пункт нумерованного списка
2. Второй пункт
  * Ненумерованный вложенный список.
1. Сами числа не имеют значения, лишь бы это были цифры
  1. Нумерованный вложенный список
4. И еще один пункт.

   Внутри пунктов списка можно вставить абзацы с таким же отступом. Обратите внимание на пустую строку выше и на пробелы в начале (нужен по меньшей мере один, но здесь мы добавили три, чтобы также выровнять необработанный Markdown).

   Чтобы вставить разрыв строки, но не начинать новый параграф, нужно добавить два пробела перед новой строкой.  
   Этот текст начинается с новой строки, но находится в том же абзаце.  
   (В некоторых обработчиках, например на Github, пробелы в начале новой строки не нужны.)

 * Ненумерованный список можно размечать звездочками
 - Или минусами
 + Или плюсами
"""
	
	result += markdown2.markdown("----")
	result += markdown2.markdown("### Списки") + markdown2.markdown(_help) + markdown2.markdown(_help1) 

	_help = """
	Ссылки можно оформить разными способами.

	[Обычная ссылка в строке](https://www.google.com)

	[Обычная ссылка с title](https://www.google.com "Сайт Google")

	[Ссылка со сноской][Произвольный регистронезависимый текст]

	[Относительная ссылка на документ](../blob/master/LICENSE)

	[Для ссылок со сноской можно использовать цифры][1]

	Или можно просто вставить ссылку в квадратные скобки [текст ссылки]

	Произвольный текст, после которого можно привести ссылки.

	[произвольный регистронезависимый текст]: https://www.mozilla.org
	[1]: http://slashdot.org
	[текст ссылки]: http://www.reddit.com
	"""

	_help1 = """
Ссылки можно оформить разными способами.

[Обычная ссылка в строке](https://www.google.com)

[Обычная ссылка с title](https://www.google.com "Сайт Google")

[Ссылка со сноской][Произвольный регистронезависимый текст]

[Относительная ссылка на документ](../blob/master/LICENSE)

[Для ссылок со сноской можно использовать цифры][1]

Или можно просто вставить ссылку в квадратные скобки [текст ссылки]

Произвольный текст, после которого можно привести ссылки.

[произвольный регистронезависимый текст]: https://www.mozilla.org
[1]: http://slashdot.org
[текст ссылки]: http://www.reddit.com
"""

	result += markdown2.markdown("----")
	result += markdown2.markdown("### Ссылки") + markdown2.markdown(_help) + markdown2.markdown(_help1) 

	_help = """
	Вот наш логотип (наведите указатель, чтобы увидеть текст заголовка):

	Внутри строки:  
	![alt-текст](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Текст заголовка логотипа 1")

	В сноске:  
	![alt-текст][logo]

	[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Текст заголовка логотипа 2"
	"""

	_help1 = """
Вот наш логотип (наведите указатель, чтобы увидеть текст заголовка):

Внутри строки:  
![alt-текст](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Текст заголовка логотипа 1")

В сноске:  
![alt-текст][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Текст заголовка логотипа 2"
"""

	result += markdown2.markdown("----")
	result += markdown2.markdown("### Изображения") + markdown2.markdown(_help) + markdown2.markdown(_help1) 


	return result