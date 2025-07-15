# non_ai_service

## Environment setup
```
powershell
python -m venv _env

 .\_env\Scripts\activate

 pip install -r requirements.txt
 
 pip install -r .\app\wrk_data\requirements.txt

 .\_env\Scripts\deactivate
```

## To test it locally
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8003

uvicorn app.endpoints.api_endpoints.main:app  --reload --port 8000 --host 0.0.0.0
```
 
 ```browser
http://localhost:8003/docs#/
```