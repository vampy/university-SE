# SE-project
Software engineering project from UBB.

# Installation
Notice, you need Python 3.4+ for this steps to work.

1. Create and activate [virtual environment](https://docs.python.org/3.4/library/venv.html)

2. If you get a weird error on some systems regarding pip, [follow this setup](https://gist.github.com/denilsonsa/21e50a357f2d4920091e#pyvenv-34-ubuntu-1404-also-debian).

3. Install required dependencies
`pip install -r requirements.txt`

4. Init the database data (this will create all the database tables)
`python manage.py init`

# Running
If you are not in the virtual environment you must change to it.
 
`python manage.py run`

You can log in with the username `test` and password `test` (if you did init the database using the instructions from step 4, as described above).

# Contributing
This project uses [Flask](http://flask.pocoo.org/) as a framework ([general documentation](http://flask.pocoo.org/docs/0.10/)), with the following extensions:
- [Flask-Login](https://flask-login.readthedocs.org/en/latest/) - handles the common tasks of logging in, logging out, and remembering your users’ sessions over extended periods of time.
- [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/) - handles creation/validation and using of forms in the UI.
- [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/) - adds [SQLAlchemy](http://www.sqlalchemy.org/) support, which is an [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping).

On the UI side we use the following technologies/libraries:
- [jQuery](https://jquery.com/) as a helper library for Javascript
- [Twitter Bootstrap](http://getbootstrap.com/) for UI elements and components
- [Jinja2](http://jinja.pocoo.org/) as a template engine (used by default by [Flask](http://flask.pocoo.org/docs/0.10/templating/) framework).
