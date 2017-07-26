## Local Debug Steps

**MAKE SURE YOU ARE ON THE PYTHON3(<3.6) ENVIRONMENT**

### On Dev Mode

1. `pip install flask`
2. `pip install flask_cors`
3. `pip install bson`
4. `pip install pymongo`
5. `pip install pyqrcode`
6. `set FLASK_APP=advocateSimpleServer.py`
7. `flask run`(Single process mode)
8. Open browser and test REST APIs (may use Chrome extension *Restlet Client*).

### Deploy(Multiprocess Mode)
1. Choose your own uWSGI Container, you can follow the [link](http://flask.pocoo.org/docs/0.12/deploying/);
2. Using `Gunicorn` as example:
    - `pip install gunicorn`
    - `gunicorn -w 4 -b :13888 --log-level=debug advocateSimpleServer:app`

## Useful Links

[MongoDB Reference](https://docs.mongodb.com/manual/reference/)

[PyMongo Documentation](https://api.mongodb.com/python/current/)

[Gunicorn Documentation](http://gunicorn.org/)

## Problem Solving

1. Run Gunicorn said `'No module named flask'` like [this](https://stackoverflow.com/questions/18776745/gunicorn-with-flask-using-wrong-python)
    > Maybe the gunicorn load the global pip environment which influence proj., better create the `virtualenv` to make sure you have pure pip environment;
