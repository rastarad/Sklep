from flask import Flask, request, redirect, url_for, render_template, session, flash, g
from functools import wraps
import sqlite3, jwt

app = Flask(__name__)
app.secret_key = "secret_key"
app.database = "sklep.db"

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session:
            flash("Jesteś zalogowany.")
            return f(*args, **kwargs)
        else:
            flash('Aby korzystać z naszego sklepu musisz się zalogować!')
            return redirect(url_for('login'))
    return wrap

def login_required_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            flash("Jesteś zalogowany.")
            return f(*args, **kwargs)
        else:
            flash('Aby korzystać z naszego sklepu musisz się zalogować!')
            return redirect(url_for('login'))
    return wrap
def login_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'log_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        g.db = connect_db()
        cur = g.db.execute('select * from users')
        id = []
        users = []
        for row in cur.fetchall():
            id.append(row[0])
            users.append(row[1])
        if request.form['username'] in users[:]:
            g.db.close()
            flash("Użytkownik o podanym loginie już istnieje.")
            return render_template('register.html')
        if request.form['password'] == "":
            g.db.close()
            flash("Nie podałeś hasła.")
            return render_template('register.html')
        if request.form['username'] == "":
            g.db.close()
            flash("Nie podałeś nazwy.")
            return render_template('register.html')
        else:
            index = max(id)
            index = index + 1
            data = {"password": request.form['password']}
            encoded_jwt = jwt.encode(data, "secret_key", algorithm="HS256")
            sql = 'INSERT INTO users (user_id, login, password) VALUES(?, ?, ?)'
            val = (index, request.form['username'], encoded_jwt)
            g.db.execute(sql, val)
            g.db.commit()
            g.db.close()
            flash("Witaj! Właśnie się zarejestrowałeś.")
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required_admin
def admin():
    g.db = connect_db()
    cur = g.db.execute('select * from shop')
    products = []
    for row in cur.fetchall():
        products.append(dict(id=row[0], name=row[1], price=row[3]))
    cur = g.db.execute('select * from users')
    users = []
    for row in cur.fetchall():
        users.append(dict(user_id=row[0], login=row[1]))
    g.db.close()
    return render_template('admin.html', products=products, users=users, username=session['log_in'])

@app.route('/erase', methods=['GET', 'POST'])
@login_required_admin
def erase():
    g.db = connect_db()
    cur = g.db.execute('select * from users')
    users = []
    for row in cur.fetchall():
        users.append(dict(user_id=row[0], login=row[1]))
    g.db.close()
    if request.method == 'POST':
        if request.form['id'] == "":
            flash("Nie podałeś identyfikatora uzytkownika.")
            return render_template('erase.html', users=users)
        if not request.form['id'].isnumeric():
            flash("Nie podałeś liczby.")
            return render_template('erase.html', users=users)
        g.db = connect_db()
        g.db.execute('delete from users where user_id=?', request.form['id'])
        g.db.commit()
        cur = g.db.execute('select * from users')
        users = []
        for row in cur.fetchall():
            users.append(dict(user_id=row[0], login=row[1]))
        g.db.close()
        flash("Użytkownika o tym identyfikatorze nie ma już w bazie.")
        return redirect(url_for('erase'))
    return render_template('erase.html', users=users)

@app.route('/shop', methods = ['GET','POST'])
def shop():
    g.db = connect_db()
    cur = g.db.execute('select * from shop')
    products = []
    prod = []
    for row in cur.fetchall():
        products.append(dict(name=row[1], amount=row[2], price=row[3]))
        prod.append(row[1])
    if request.method == 'POST':
        if request.form['name'] == "":
            flash("Nie podałeś nazwy produktu.")
            return render_template('shop.html', products=products, username=session['log_in'])
        if not request.form['name'] in prod[:]:
            flash("Nie mamy takiego produktu :(")
            return render_template('shop.html', products=products, username=session['log_in'])
        cur = g.db.execute('select price from shop where product=?', [request.form['name']])
        price = []
        for row in cur.fetchall():
            price.append(row[0])
        sql = 'INSERT INTO CART (login, product, amount, price) VALUES(?, ?, ?, ?)'
        val = session['log_in'], request.form['name'], request.form['number'], price[0]
        g.db.execute(sql, val)
        g.db.commit()
        g.db.close()
        flash("Produkt dodany do koszyka")
        g.db.close()
        return redirect(url_for('shop'))
    return render_template('shop.html', products=products, username=session['log_in'])

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    g.db = connect_db()
    cur = g.db.execute('select * from cart where login=?', [session['log_in']])
    cart = []
    for row in cur.fetchall():
        cart.append(dict(name=row[1], amount=row[2], price=row[3]))
    g.db.close()
    if request.method == 'POST':
        g.db = connect_db()
        sql = 'delete from cart where login=? and product=?'
        val = (session['log_in'], request.form['product'])
        g.db.execute(sql, val)
        g.db.commit()
        g.db.close()
        flash("Usunałeś produkty z koszyka")
        return redirect(url_for('user'))
    return render_template('user.html', cart=cart, username=session['log_in'])

@app.route('/offer', methods=['GET', 'POST'])
@login_required
def offer():
    g.db = connect_db()
    cur = g.db.execute('select * from offer where login=?', [session['log_in']])
    offers = []
    for row in cur.fetchall():
        offers.append(dict(name=row[1], amount=row[2], price=row[3]))
    if request.method == 'POST':
        if request.form['ads'] == "" or request.form['amount'] == "" or request.form['price'] == "":
            flash("Nie podałeś elementu oferty.")
            return render_template('offer.html', offers=offers, username=session['log_in'])
        sql = 'INSERT INTO offer (login, product, amount, price) VALUES(?, ?, ?, ?)'
        val = (session['log_in'], request.form['ads'], request.form['amount'], request.form['price'])
        g.db.execute(sql, val)
        g.db.commit()
        cur = g.db.execute('select product_id from shop')
        id = []
        for row in cur.fetchall():
            id.append(row[0])
        index = max(id)
        index = index + 1
        sql = 'INSERT INTO shop (product_id, product, amount, price) VALUES(?, ?, ?, ?)'
        val = (index, request.form['ads'], request.form['amount'], request.form['price'])
        g.db.execute(sql, val)
        g.db.commit()
        g.db.close()
        flash("Dodałeś nową ofertę")
        return redirect(url_for('offer'))
    g.db.close()
    return render_template('offer.html', offers=offers, username=session['log_in'])

@app.route('/offerX', methods=['GET', 'POST'])
@login_required
def offerX():
    if request.method == 'POST':
        g.db = connect_db()
        sql = 'delete from offer where login=? and product=?'
        val = (session['log_in'], request.form['sub'])
        g.db.execute(sql, val)
        g.db.commit()
        g.db.close()
        flash("Usunąłeś produkt.")
        return redirect(url_for('offerX'))
    return render_template('offerX.html', username=session['log_in'])

@app.route('/offerXadmin', methods=['GET', 'POST'])
@login_required_admin
def offerXadmin():
    if request.method == 'POST':
        print("if")
        g.db = connect_db()
        sql = 'delete from shop where product=?'
        val = (request.form['sub'],)
        print(type(val))
        val2 = (request.form['sub'],)
        print(val2)
        g.db.execute(sql, val)
        g.db.commit()
        g.db.close()
        return redirect(url_for('offerXadmin'))
    return render_template('offerXadmin.html', username=session['log_in'])

@app.route('/change', methods=['GET', 'POST'])
@login_in
def change():
    error = None
    if request.method == 'POST':
        if not request.form['old']:
            error = 'Podaj swoje obecne hasło.'
            return render_template('change.html', error=error)
        if not request.form['new']:
            error = 'Podaj nowe hasło.'
            return render_template('change.html', error=error)
        login = session['log_in']
        g.db = connect_db()
        cur = g.db.execute('select * from users where login=?', [login])
        passwords = []
        for row in cur.fetchall():
            passwords.append(row[2])
        passwords = jwt.decode(passwords[0], "secret_key", algorithms=["HS256"])
        print(passwords)
        g.db.close()
        if request.form['old'] in passwords.values():
            if session['log_in'] == admin:
                g.db = connect_db()
                data = {"password": request.form['new']}
                encoded_jwt = jwt.encode(data, "secret_key", algorithm="HS256")
                sql = 'update users set password=? where login=?'
                val = (encoded_jwt, login)
                g.db.execute(sql, val)
                g.db.commit()
                g.db.close()
                flash("Hasło zostało zmienione.     ")
                return redirect(url_for('admin'))
            g.db = connect_db()
            data = {"password": request.form['new']}
            encoded_jwt = jwt.encode(data, "secret_key", algorithm="HS256")
            sql = 'update users set password=? where login=?'
            val = (encoded_jwt , login)
            g.db.execute(sql, val)
            g.db.commit()
            g.db.close()
            flash("Hasło zostało zmienione.     ")
            return redirect(url_for('user'))
        else:
            g.db.close()
            error = 'Niepoprawne dane. Spróbuj jeszcze raz.'
    return render_template('change.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        g.db = connect_db()
        cur = g.db.execute('select * from users where login=?', [request.form['username']])
        users = []
        passwords = []
        for row in cur.fetchall():
            users.append(row[1])
            passwords.append(row[2])
        if not passwords:
            error = 'Niepoprawne dane. Spróbuj jeszcze raz.'
            return render_template('login.html', error=error)
        passwords = jwt.decode(passwords[0], "secret_key", algorithms=["HS256"])
        passwords = list(passwords.values())
        if request.form['username'] in users[:] and request.form['password'] in passwords[:]:
            if request.form['username'] == 'admin' and request.form['password'] == 'admin':
                admin = request.form['username']
                session['admin'] = True
                session['log_in'] = admin
                g.db.close()
                return redirect(url_for('admin'))
            username = request.form['username']
            session['user'] = True
            session['log_in'] = username
            g.db.close()
            return redirect(url_for('user'))
        else:
            g.db.close()
            error = 'Niepoprawne dane. Spróbuj jeszcze raz.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    session.pop('log_in', None)
    flash("Właśnie się wylogowałeś. Miłego dnia!")
    return redirect(url_for('main'))

def connect_db():
    return sqlite3.connect(app.database)

if __name__ == '__main__':
    app.run(debug=True)

# run Win in terminal:
#: venv/Scripts/activate
#: python app.py

# konsola pyhtona
#: python

# baza
#: sqlite3 sklep.db
