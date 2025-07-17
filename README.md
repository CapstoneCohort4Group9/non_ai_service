# non_ai_service

## Environment setup

```
powershell
py -3.11 -m venv _env

 .\_env\Scripts\activate

# for api running
 pip install -r requirements.txt

# for database setting
 pip install -r .\app\wrk_data\requirements.txt

 .\_env\Scripts\deactivate
```

## To test it locally

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8003

```

```browser
http://localhost:8003/docs#/
```
