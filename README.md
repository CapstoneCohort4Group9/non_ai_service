# non_ai_service

## Environment setup

```
powershell
py -3.11 -m venv _env

 .\_env\Scripts\activate

# for api running
 pip install -r requirements.txt

 .\_env\Scripts\deactivate
```

## Environment for database

```
powershell
py -3.11 -m venv _dbenv

 .\_dbenv\Scripts\activate

# for database setting
 pip install -r .\app\wrk_data\requirements.txt

 .\_dbenv\Scripts\deactivate
```
pt
## To test it locally

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8003

```

```browser
http://localhost:8003/docs#/
```
