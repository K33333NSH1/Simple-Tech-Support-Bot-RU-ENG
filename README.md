Simple Tech Support Bot. <br>
INSTALLATION<br>
1<br>
```<br>
pip install -r requirements.txt<br>
```<br>
2 Add values in config.py<br>
3 Run main.py<br>
How it works<br>
It creates a local database with a table where it records tickets and admin responses.
When creating a ticket, the body of the request is recorded in the database, forwarded to the administrators chat, and the bot waits for a response.
Upon receiving a response, the response is recorded in the database and forwarded to the chat of the user who left the request.





Простой бот технической поддержки.
УСТАНОВКА
1
```
pip install -r requirements.txt
```
2 Добавить значения в config.py
3 Запустить main.py


Принцид действия
Создает локальную бд с таблицей, куда записывает тикеты и ответы администраторов.

При создании тикета тело заявки записывается в базу данных, переслыется в adminschat и бот ожидает ответ.
При получении ответа ответ записывается в базу даннынх и пересылается в чат пользователю, оставившему заявку.#   S i m p l e - T e c h - S u p p o r t - B o t - R U - E N G 
 
 
