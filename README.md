[![Python CI](https://github.com/ramilevi1/qeu/actions/workflows/main.yml/badge.svg)](https://github.com/ramilevi1/qeu/actions/workflows/main.yml)


# QT-ride
Carpooliong. features included:
1. sign up and log-in/log-out (authentication)
2. HTTPS support (currently with self sign certificate)
3. responsive front-end and backend
7. blog to share our progress and learnings
8. parsing blog for dynamic content and search functionality
9. newletter signin for anyone who wants to be notified of new posts
10. script to send weekly/monthly newsletter to registered users
11. unsubscrite functionality
12. contact us - Email sender (currently send to rami's personal email)


# Technology used : 
1. HTML 5
2. CSS 3
3. Javascript (vanilla)
4. Jquery
5. Bootstrap
6. MixItUp plugin
7. Flask - Python
8. Ajax for serving JS files
9. SQlite3
10. Playwright basic e2e tests
11. unig tests 

Next to do:
1. containerize
2. admin backoffice for managing users and blog posts
2. deploy to production using uWSGI ?!
3. github action setup for CI/CD
4. using web server NginX or Apache
5. SSL support (HTTP, HSTS) for security 
6. RabbitMQ for serving email async and later on live rides
7. MongoDB for serving images
8. sqlite3 database replication with the app and failover seperate service
9. create the offerRide and SearchRide as microservices


To start the web application:
python -m venv venv  OR 
python -m venv C:\xyz\venv\Scripts\python.exe
.\venv\Scripts\activate
$env:PATH = ".\venv\Scripts;" + $env:PATH 
flask db init     
flask db upgrade
flask db migrate
pip install Flask
set FLASK_APP=app.py flask run
pip install Flask-Mail
pip install Flask-SQLAlchemy      
pip install beautifulsoup4
pip install flask-migrate
pip install flask-login
pip install spacy
python -m spacy download en_core_web_sm
pip install WTForms
pip install Flask-WTF

# install selfsign certificate:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=127.0.0.1'
# remove passcode: 
openssl rsa -in key.pem -out key_decrypted.pem        

$env:PATH = ".\venv\Scripts;" + $env:PATH   
export PYTHONPATH=/path/to/parent_directory:$PYTHONPATH
>> python scripts/parse_blogs.py
python -m venv C:\xyz\venv\Scripts\python.exe
.\venv\Scripts\activate   
python .\app.py -debug 
flask run
 
 
Architecture:
N-tier microservices arcitecture 
                        --------
                        |Client |
                        --------
                            |
                            |
                            |  
------------------------    -------------------    -------------------
|authentication service|    |offerRide service|   |searchRide service|
------------------------    -------------------   --------------------
            |                        |                    |
            |                        |                    |
      ------------            --------------         ----------
      |   DB     |            |     DB     |         |    DB   |
      ------------            -------------          ----------
