import sqlite3
import sys
import requests
import random
from bs4 import BeautifulSoup

from flask import Flask, redirect, request, url_for, render_template, session

# create a flask app
app = Flask(__name__)  # our Flask app
DB_FILE = 'mydb.db'  # file for our Database
app.secret_key = "super secret key"


# set-up index page / as well as bs for 'recipe of the day'
@app.route('/')
def root():
    # establish connection with the recipe website
    url = requests.get("https://www.allrecipes.com/recipes/")
    txt = url.text
    soup = BeautifulSoup(txt, 'html.parser')

    # scrape recipe of the day
    rotd= soup.find('article',class_='fixed-recipe-card' )
    f_name = rotd.find('span',class_='fixed-recipe-card__title-link').text
    f_desc = rotd.find('div',class_='fixed-recipe-card__description').text
    f_link = rotd.a['href']
    f_img = rotd.a.img['data-original-src']

    # save into db
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    params = {'name': f_name, 'desc': f_desc, 'link': f_link, 'img': f_img}
    try:
        cursor.execute("insert into recipeOfTheDay VALUES (:name, :desc, :link, :img)", params)
    except:
        print("Already in DB; Not updating.")
    connection.commit()
    cursor.close()

    # display index page with recipe of the day
    return render_template('index.html', f_name=f_name, f_desc=f_desc, f_link=f_link, f_img=f_img)
    


# guestbook - display entries / as well as bs for 'weather'
@app.route('/guestbook', methods=['POST', 'GET'])
def gb():
    # establish connection with the weather website
    page=requests.get("https://weather.com/en-IN/weather/tenday/l/af60f113ba123ce93774fed531be2e1e51a1666be5d6012f129cfa27bae1ee6c")
    content=page.content
    soup=BeautifulSoup(content,"html.parser")
    l=[]
    weather=""
    all=soup.find("div",{"class":"locations-title ten-day-page-title"}).find("h1").text
    
    # scrape the weather table
    table=soup.find_all("table",{"class":"twc-table"})
    for items in table:
        for i in range(len(items.find_all("tr"))-1):
            d = {}
            try:
                d["date"]=items.find_all("span",{"class":"day-detail"})[i].text			
                d["desc"]=items.find_all("td",{"class":"description"})[i].text
                d["temp"]=items.find_all("td",{"class":"temp"})[i].text
                d["wind"]=items.find_all("td",{"class":"wind"})[i].text
                d["humidity"]=items.find_all("td",{"class":"humidity"})[i].text

                # save into db
                connection = sqlite3.connect(DB_FILE)
                cursor = connection.cursor()
                params = {'date': d["date"], 'desc': d["desc"], 'temp': d["temp"], 'wind': d["wind"], 'humidity': d["humidity"]}
                try:
                    cursor.execute("insert into weather VALUES (:date, :desc, :temp, :wind, :humidity)", params)
                except:
                    print("Already in DB; Not updating.")
                connection.commit()
                cursor.close()

            except:
                d["date"]="None"
                d["desc"]="None"
                d["temp"]="None"
                d["wind"]="None"
                d["humidity"]="None"
            l.append(d)

    # connect and scrape random qoute to show as quote of the day from brainyquote
    q_url = "https://www.brainyquote.com/topics/inspirational-quotes"
    response = requests.get(q_url)
    soup = BeautifulSoup(response.content,'html.parser')
    quotes = soup.find_all('a', attrs={"title": "view quote"})
    quotesList = []
    for quote in quotes:
        quotesList.append(quote.text)

    # random quote
    num = random.randint(0,len(quotesList))
    qotd = quotesList[num]

    # save into db
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    params = {'qotd': qotd}
    try:
        cursor.execute("insert into quoteOfTheDay VALUES (:qotd)", params)
    except:
        print("Already in DB; Not updating.")
    connection.commit()
    cursor.close()

    # connect and scrape corona related data / what is corona?
    c_url = "https://www.who.int/news-room/q-a-detail/q-a-coronaviruses"
    response = requests.get(c_url)
    soup = BeautifulSoup(response.content,'html.parser')
    whatC = soup.find("div",{"class":"sf-accordion__content"}).find("p").text

    # connect and scrape corona related data / corona symptoms
    c_url = "https://www.who.int/health-topics/coronavirus"
    response = requests.get(c_url)
    soup = BeautifulSoup(response.content,'html.parser')
    symptomsC = soup.find_all('span', attrs={"style": "background-color:transparent;text-align:inherit;text-transform:inherit;white-space:inherit;word-spacing:normal;caret-color:auto;"})[0].text

    # connect and scrape corona related data / who to contact?
    c_url = "https://www.dha.gov.ae/Covid19/Pages/home.aspx"
    response = requests.get(c_url)
    soup = BeautifulSoup(response.content,'html.parser')
    contactC = soup.find_all('ul', attrs={"style": "list-style-type:disc;margin-left:22.15px;"})[1].text


    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM guestbook")
        rv = cursor.fetchall()
        cursor.close()
        return render_template('guestbook.html', entries=rv, weather=l, qotd=qotd, whatC=whatC, symptomsC=symptomsC, contactC=contactC)
    except:
        return render_template('error.html', msg=sys.exc_info()[1])


# guestbook - insert entries / html to sql
def _insert(name, email, comment):
    params = {'name': name, 'email': email, 'comment': comment}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into guestbook VALUES (:name, :email, :comment)", params)
    connection.commit()
    cursor.close()


# guestbook - insert entries / button action
@app.route('/sign', methods=['POST'])
def sign():
    _insert(request.form['name'], request.form['email'], request.form['comment'])
    return redirect(url_for('gb'))


# set-up register page
@app.route('/reg')
def reg():
    return render_template('reg.html')


# register - insert entries / html to sql
def _newaccount(username, email, password):
    params = {'username': username, 'email': email, 'password': password}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into accounts VALUES (:username, :email, :password)", params)
    connection.commit()
    cursor.close()


# register - insert entries / button action
@app.route('/register', methods=['POST'])
def register():
    _newaccount(request.form['username'], request.form['email'], request.form['password'])
    return redirect(url_for('login'))


# set-up login page
@app.route('/login')
def login():
    return render_template('login.html')


# login - read entries / authentication
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        query = "select * from accounts where username = '" + request.form['username']
        query = query + "' and password = '" + request.form['password'] + "';"
        connection = sqlite3.connect(DB_FILE)
        cur = connection.execute(query)
        rv = cur.fetchall()
        cur.close()
        if len(rv) == 1:
            session['username'] = request.form['username']
            session['logged in'] = True
            return redirect("/")
        else:
            return render_template('login.html', msg="Check your login details and try again.")
    else:
        return render_template('login.html')


# logout - button action
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("logged in", None)
    session.pop("username", None)
    return render_template('index.html')


# post/1 - set-up page / display entries
@app.route('/posts/1', methods=['POST', 'GET'])
def posts1():
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM post1")
        rv = cursor.fetchall()
        cursor.close()
        return render_template('/posts/1.html', entries=rv)
    except:
        return render_template('error.html', msg=sys.exc_info()[1])


# post/1 - insert entries / html to sql
def _newcomment1(username, comment):
    params = {'username': username, 'comment': comment}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into post1 VALUES (:username, :comment)", params)
    connection.commit()
    cursor.close()


# post/1 - insert entries / button action
@app.route('/comment1', methods=['POST'])
def comment1():
    _newcomment1(session['username'], request.form['comment'])
    return redirect(url_for('posts1'))


# post/2 - set-up page / display entries
@app.route('/posts/2', methods=['POST', 'GET'])
def posts2():
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM post2")
        rv = cursor.fetchall()
        cursor.close()
        return render_template('/posts/2.html', entries=rv)
    except:
        return render_template('error.html', msg=sys.exc_info()[1])


# post/2 - insert entries / html to sql
def _newcomment2(username, comment):
    params = {'username': username, 'comment': comment}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into post2 VALUES (:username, :comment)", params)
    connection.commit()
    cursor.close()


# post/2 - insert entries / button action
@app.route('/comment2', methods=['POST'])
def comment2():
    _newcomment2(session['username'], request.form['comment'])
    return redirect(url_for('posts2'))


# post/3 - set-up page / display entries
@app.route('/posts/3', methods=['POST', 'GET'])
def posts3():
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM post3")
        rv = cursor.fetchall()
        cursor.close()
        return render_template('/posts/3.html', entries=rv)
    except:
        return render_template('error.html', msg=sys.exc_info()[1])


# post/3 - insert entries / html to sql
def _newcomment3(username, comment):
    params = {'username': username, 'comment': comment}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into post3 VALUES (:username, :comment)", params)
    connection.commit()
    cursor.close()


# post/3 - insert entries / button action
@app.route('/comment3', methods=['POST'])
def comment3():
    _newcomment3(session['username'], request.form['comment'])
    return redirect(url_for('posts3'))


# run flask in debug mode
if __name__ == '__main__':
    app.run(debug=True)
