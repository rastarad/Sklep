import sqlite3
with sqlite3.connect('sklep.db') as connection:

    c = connection.cursor()

    c.execute('CREATE TABLE users(user_id INT, login TEXT NOT NULL UNIQUE, password TEXT NOT NULL)')
    c.execute('CREATE TABLE shop(product_id INT UNIQUE, product TEXT NOT NULL, amount INT, price INT NOT NULL)')
    c.execute('CREATE TABLE cart(login TEXT NOT NULL, product TEXT, amount INT, price INT NOT NULL)')
    c.execute('CREATE TABLE offer(login TEXT NOT NULL, product TEXT, amount INT, price INT NOT NULL)')

    c.execute('INSERT INTO users VALUES(0, "admin","admin")')
    c.execute('INSERT INTO users VALUES(1, "user1","1231")')
    c.execute('INSERT INTO users VALUES(2, "user2","1232")')
    c.execute('INSERT INTO users VALUES(3, "user3","1233")')

    c.execute('INSERT INTO shop VALUES(1, "telefon", 30, 500)')
    c.execute('INSERT INTO shop VALUES(2, "karma", 10, 20)')
    c.execute('INSERT INTO shop VALUES(3, "przybory", 50, 10)')
    c.execute('INSERT INTO shop VALUES(4, "zeszyt", 100, 4)')

    c.execute('INSERT INTO cart VALUES("user1", "telefon", 2, 30)')
    c.execute('INSERT INTO cart VALUES("user1", "przybory", 10, 10)')
    c.execute('INSERT INTO cart VALUES("user2", "karma", 10, 100)')
    c.execute('INSERT INTO cart VALUES("user4", "przybory", 50, 10)')

    c.execute('INSERT INTO offer VALUES("user3", "buty", 2, 300)')
    c.execute('INSERT INTO offer VALUES("user4", "biurko", 1, 1000)')

# Niestokenizowane hasła dodane przez terminal należy stokenizować dodając wiersz:
# if len(passwords) > 100:
# przed funkcję detokenizującą w endopoincie "change" oraz zmienić hasło jeszcze raz przez stronę