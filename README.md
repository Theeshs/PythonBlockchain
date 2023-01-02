**Activate the virtual environment**

```
    pipenv shell
```

**Install all packages**
``` 
    pipenv install 
```

**Run the tests**

Make sure to activate the virtial environments

```
   python -m pytest backend/tests
```

**Run the application and API**
Make sure to activate the virtual environment

```
   python -m backend.app
```

**Run a peer instace**
make sure to activate virtual env
```
    export PEER=True && python -m backend.app
```

**Seed backend with Data**
```
export SEED_DATA=True && python -m backend.app
```