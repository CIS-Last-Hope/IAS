# How to run
Создаёте .env файл в папке /backend(в итоге у вас получится /backend/.env)
В .env прописываете следующее
`
```
SERVER_HOST=127.0.0.1  
SERVER_PORT=8000  
DATABASE_URL='sqlite:///./database.sqlite3'  
JWT_SECRET=PtIN-JH1o00QwicDXrHWAXOtGtGsCbGYa3MzYIYpdRQ  
JWT_ALGORITHM='HS256'  
JWT_EXPIRATION=3600  
API_KEY_ANTIVIRUS='ваш апи ключ'  
ADMIN_CODE='1234'
```
Вместо ключа вы пишите апи ключ с VirusTotal или можете прото закоментить по пути /IAS/backend/services/course.py начиная с 93 строчки это:
```
loop = asyncio.get_event_loop()  
virus = await loop.run_in_executor(executor, antivirus, BytesIO(file.file.read()))  
if virus:  
raise exception
```
Далее запускаете
```
docker-compose up
```
