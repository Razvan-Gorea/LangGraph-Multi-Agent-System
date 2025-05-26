### Setup

### Python version 3.10.11

Setup your venv with:
```
python -m venv ./venv
```

Activate the venv (Windows):
```
venv\Scripts\activate
```
Or in Linux:
```
source venv/bin/activate
```

You can just use ```activate``` or ```deactivate``` from then on.

Install your pip dependencies from the requirements.txt:
```
pip install -r requirements.txt
```

Populate a .env file with the required variables. See .env_example for an idea of the ones you need.

### Unit testing
Run using  ```python -m pytest``` at the src level of the repo.

### Type Checking  
basedpyright is used here, with baseline enabled.  
To get all fails, just use ```basedpyright```

### Running
You can run both the backend and the frontend together with:

```
python main.py
```

### Frontend
To run just the node frontend:
```
npm run dev
```
