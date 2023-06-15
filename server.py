import socket, threading
from cprotocol import Cprotocol
from cmessage import Cmessage
import mysql.connector
from mysql.connector import Error

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def create_tables(connection):
    create_userData_table = """
    CREATE TABLE UserInfo  (
        id VARCHAR(16) NOT NULL,
        username VARCHAR(64) NOT NULL,
        password VARCHAR(64) NOT NULL,
        PRIMARY KEY(id, username)
    );
    """
    create_wallet_table = """
    CREATE TABLE Wallets (
        id VARCHAR(16) NOT NULL,
        amount DECIMAL(16,2) NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(id) REFERENCES UserInfo(id)
    );
    """
    create_transactions_table = """
    CREATE TABLE Transactions (
	    id VARCHAR(16) NOT NULL,
	    state VARCHAR(16),
	    amount DECIMAL(16,2),
	    user_from VARCHAR(16),
	    user_to VARCHAR(16),
	    detail VARCHAR(2048),
	    category VARCHAR(16),
	    PRIMARY KEY(id),
	    FOREIGN KEY(user_from) REFERENCES UserInfo(id),
        FOREIGN KEY(user_to) REFERENCES UserInfo(id)
    );
    """
    execute_query(connection, create_userData_table)
    execute_query(connection, create_wallet_table)
    execute_query(connection, create_transactions_table)

def countUser():
    query = """
    SELECT COUNT(*)
    FROM UserInfo
    """
    read = read_query(connection, query)
    for x in read:
        for y in x:
            y = y + 1
    return y

def createAccount(u,p):
    id = countUser()
    query = "INSERT INTO UserInfo VALUES ('{}','{}','{}')"
    query = query.format(id, u, p)
    execute_query(connection, query)
    query = "INSERT INTO Wallets VALUES ('{}', 0.00)"
    query = query.format(id)
    execute_query(connection, query)

def checkAccount(u,p):
    query = """
    SELECT id, username, password
    FROM UserInfo
    """
    read = read_query(connection, query)
    for x in read:
        if x[1] == u:
            if x[2] == p:
                string = "user " + u + " exists\n"
                code = 1
                id = x[0]
                return code, string, id
            else:
                string = "password " + p + " is wrong\n"
                code = 2
                return code, string
    string = "username " + u + " was not found\n"
    code = 3
    return code, string

def countTransactions():
    query = """
    SELECT COUNT(*)
    FROM Transactions
    """
    read = read_query(connection, query)
    for x in read:
        for y in x:
            y = y + 1
    return y

def addMoney(amt,id,src):
    query = """
    UPDATE Wallets
    SET amount = amount + {}
    WHERE id = '{}'
    """
    query = query.format(amt, id)
    execute_query(connection, query)
    query = """
    INSERT INTO Transactions
    VALUES ('{}', "completed", '{}', "", '{}', '{}', "deposit")
    """
    number = countTransactions()
    query = query.format(number, amt, id, src)
    execute_query(connection, query)

def find(u):
    query = """
    SELECT id, username
    FROM UserInfo
    WHERE username = '{}'
    """
    query = query.format(u)
    read = read_query(connection, query)
    for x in read:
        if x[1]==u:
            return True, x[0]
    return False, read

def checkBalance(id,amt):
    query = """
    SELECT amount
    FROM Wallets
    WHERE id = '{}'
    """
    query = query.format(id)
    read = read_query(connection, query)
    for x in read:
        for y in x:
            if float(amt)<=y:
                return True
    return False

def showBalance(id):
    query = """
    SELECT amount
    FROM Wallets
    WHERE id = '{}'
    """
    query = query.format(id)
    read = read_query(connection, query)
    for x in read:
        for y in x:
            return y
    return 'ERRO'

def showTransactions(id):
    query = """
    SELECT state, amount, user_from, user_to, detail, category 
    FROM Transactions
    WHERE id = '{}'
    """
    query = query.format(id)
    read = read_query(connection, query)
    array = []
    for x in read:
        if x[5]=='payment':
            string = "A payment was made from {} to {} for the amount of {}. Reason: '{}'."
            string = string.format(x[2], x[3], x[1], x[4])
        if x[5]=='request':
            if x[0]=='completed':
                string = "A request of {} was made from {} to {} and the payment was completed succesfully. Reason: '{}'."
                string = string.format(x[1], x[2], x[3], x[4])
        if x[5]=='refund':
            if x[0]=='completed':
                string = "A refund request for '{}', of the amount {}, was made and completed succesfully from {} to {}."
                string = string.format(x[4], x[1], x[2], x[3])
        if x[5]=='deposit':
            string = "A deposit of the amount of {} was made to {}. Reason: ''."
            string = string.format(x[1], x[3], x[4])
        array.append(string)
    return array

def showRefundMenu(id):
    query = """
    SELECT state, amount, user_from, user_to, detail, category
    FROM Transactions
    WHERE (user_from = '{}' AND state='completed' AND category='payment') OR (user_to = '{}' AND state='completed' AND category='request')
    """
    query = query.format(id)
    read = read_query(connection, query)
    array = []
    i = 1
    for x in read:
        if x[5]=='payment':
            string = "{}. A payment was made from {} to {} for the amount of {}. Reason: '{}'."
            string = string.format(i, x[2], x[3], x[1], x[4])
            array.append(string)
            i+=1
        if x[5]=='request':
            string = "{}. A request of {} was made from {} to {} and the payment was completed succesfully. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
            i+=1
    return array

def requestRefund(sel, arr):
    number = countTransactions()
    query = """
    INSERT INTO TRANSACTIONS
    VALUES ('{}', "pending", {}, '{}', '{}', "refund for: {}", "refund")
    """
    if arr[sel][5]=='payment':
        query = query.format(number, arr[sel][1], arr[sel][2], arr[sel][3], arr[sel][4])
    if arr[sel][5]=='request':
        query = query.format(number, arr[sel][1], arr[sel][3], arr[sel][2], arr[sel][4])
    execute_query(connection, query)

def pay(amt,idB,idA,rsn):
    number = countTransactions()
    query = """
    INSERT INTO Transactions
    VALUES ('{}', "pending", {}, '{}', '{}', '{}', "payment")
    """
    query = query.format(number, amt, idA, idB, rsn)
    execute_query(connection, query)

def request(rsn,amt,idB,idA):
    number = countTransactions()
    query = """
    INSERT INTO Transactions
    VALUES ('{}', "pending", {}, '{}', '{}', '{}', "request")
    """
    query = query.format(number, amt, idB, idA, rsn)
    execute_query(connection, query)

def showCancelMenu(id):
    query = """
    SELECT state, amount, user_from, user_to, detail, category
    FROM Transactions
    WHERE (user_from = '{}' AND state='pending' AND category='payment') OR (user_to = '{}' AND state='pending' AND (category='request' OR category='refund'))
    """
    query = query.format(id)
    read = read_query(connection, query)
    array = []
    i = 1
    for x in read:
        if x[5]=='payment':
            string = "{}. Pending payment from {} to {} for the amount of {}. Reason: '{}'."
            string = string.format(i, x[2], x[3], x[1], x[4])
            array.append(string)
            i+=1
        if x[5]=='request':
            string = "{}. Pending request of {} from {} to {}. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
            i+=1
        if x[5]=='refund':
            string = "{}. Pending refund request of {} from {} to {}. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
            i+=1
    return array

def cancel(sel,menu):
    number = countTransactions()
    query = """
    UPDATE Transactions
    SET state='canceled'
    """
    execute_query(connection, query)

def intro(id):
    query = """
    SELECT state, amount, user_from, user_to, detail, category
    FROM Transactions
    WHERE user_to = '{}' AND state='pending'
    """
    query = query.format(id)
    read = read_query(connection, query)
    array = []
    i = 0
    for x in read:
        if x[5]=='payment':
            i+=1
            string = "Pending payment of {} from {}. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
        if x[5]=='request':
            i+=1
            string = "Pending request of {} from {}. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
        if x[5]=='refund':
            i+=1
            string = "Pending refund of {} from {}. Reason: '{}'."
            string = string.format(i, x[1], x[2], x[3], x[4])
            array.append(string)
    return array, i

def processPayment(id, str, type):
    query = """
    SELECT state, amount, user_from, user_to, detail, category
    FROM Transactions
    WHERE user_to = '{}' AND state='pending'
    LIMIT 1
    """
    query = query.format(id)
    read = read_query(connection, query)
    for x in read:
        if type=='payment':
            query = """
            UPDATE Transactions
            SET state='completed'
            WHERE detail='{}' AND amount='{}'
            """
            query = query.format(x[4], x[1])
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount+{}
            WHERE id='{}'
            """
            query = query.format(x[1], id)
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount-{}
            WHERE id='{}'
            """
            query = query.format(x[1], x[2])
            execute_query(connection, query)
        if type=='request':
            query = """
            UPDATE Transactions
            SET state='completed'
            WHERE detail='{}' AND amount='{}'
            """
            query = query.format(x[4], x[1])
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount-{}
            WHERE id='{}'
            """
            query = query.format(x[1], id)
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount+{}
            WHERE id='{}'
            """
            query = query.format(x[1], x[2])
            execute_query(connection, query)
        if type=='refund':
            query = """
            UPDATE Transactions
            SET state='completed'
            WHERE detail='{}' AND amount='{}'
            """
            query = query.format(x[4], x[1])
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount-{}
            WHERE id='{}'
            """
            query = query.format(x[1], id)
            execute_query(connection, query)
            query = """
            UPDATE Wallets
            SET amount=amount+{}
            WHERE id='{}'
            """
            query = query.format(x[1], x[2])
            execute_query(connection, query)

if __name__ == '__main__':
    # create the first database (the following section is commented because it only needs to be executed once)
    """ connection = create_server_connection("localhost", "root", "password") """
    """ create_database(connection, "CREATE DATABASE Databank")                  """

    # connect to the database
    connection = create_db_connection("localhost", "root", "password", "Databank")

    # create the tables (the following section is commented because it only needs to be executed once)
    """ create_tables(connection) """

    # create the server socket
    serversoc = socket.socket()              # defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    serversoc.bind(("localhost", 5000))      # bind to local host:5000
    serversoc.listen(5)                      # make passive with backlog=5
    
    # wait for incoming connections
    while True:
        print("Listening on ", 5000)
        
        conn, addr = serversoc.accept()      # accept the connection
        print("Getting connection from %s" % str(addr))
        
        # run the application protocol
        cproto = Cprotocol(conn)
        
        m1 = Cmessage()
        m1.setType('ERRO')
        m1.addParam('message', "nothing was processed...\n")

        m2 = cproto.getMessage()
        print("receiving message: ", m2)
        type = m2.getType()

        if type=='CRE8':
            username = m2.getParam('username')
            password = m2.getParam('password')
            check = checkAccount(username, password)
            if (check[0] == 3):
                createAccount(username,password)
                m1.setType('GOOD')
                m1.addParam('message', "Account created successfully...\n")
            else:
                m1.setType('ERRO')
                m1.addParam('message', "The user you entered already exists...\n")

        if type=='LGIN':
            username = m2.getParam('username')
            password = m2.getParam('password')
            check = checkAccount(username, password)
            if (check[0] == 1):
                id = check[2]
                m1.setType('GOOD')
                m1.addParam('message', "Logged in...\n")
            elif (check[0] == 2):
                m1.setType('ERRO')
                m1.addParam('message', check[1])
            elif (check[0] == 3):
                m1.setType('ERRO')
                m1.addParam('message', check[1])
            else:
                m1.setType('ERRO')
                m1.addParam('message', "Something went wrong...\n")

        if type=='LOUT':
            m1.setType('GOOD')
            m1.addParam('message', "Loggin out...\n")

        if type=='EXIT':
            m1.setType('GOOD')
            m1.addParam('message', "Client out...\n")

        if type=='ADDM':
            amount = m2.getParam('amount')
            source = m2.getParam('source')
            addMoney(amount,id,source)
            m1.setType('GOOD')
            m1.addParam('message', "Money was added...\n")
        
        if type=='PAY2':
            target = m2.getParam('target')
            check = find(target)
            if check[0]==True:
                m1.setType('GOOD')
                m1.addParam('message', "User found...\n")
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print("receiving message: ", m2)
                amount = m2.getParam('amount')
                enough = checkBalance(id,amount)
                if enough==True:
                    m1.setType('GOOD')
                    m1.addParam('message', "Enough money in the account...\n")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    print("receiving message: ", m2)
                    reason = m2.getParam('reason')
                    pay(amount, check[1], id, reason)
                    m1.setType('GOOD')
                    m1.addParam('message', "Payment successfull...\n")
                else:
                    m1.setType('ERRO')
                    m1.addParam('message', "Not enough money in the account...\n")
            else:
                string = "User " + target + " not found...\n"
                m1.setType('ERRO')
                m1.addParam('message', string)

        if type=='SHBL':
            balance = showBalance(id)
            m1.setType('GOOD')
            string = "Your balance is: " + str(balance) + "\n"
            m1.addParam('message', string)

        if type=='CKHI':
            history = showTransactions(id)
            m1.setType('GOOD')
            if history==[]:
                string = "No history in your transaction was found...\n"
            else:
                string = ""
                for x in history:
                    string = string + x + "\n"
                m1.addParam('message', string)

        if type=='REQT':
            target = m2.getParam('target')
            check = find(target)
            if check[0]==True:
                m1.setType('GOOD')
                m1.addParam('message', "User found...\n")
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print("receiving message: ", m2)
                amount = m2.getParam('amount')
                request(reason, amount, check[1], id)
                m1.setType('GOOD')
                m1.addParam('message', "Request successfull...\n")
            else:
                string = "User " + target + " not found...\n"
                m1.setType('ERRO')
                m1.addParam('message', string)

        if type=='REFU':
            m1.setType('GOOD')
            payments = showRefundMenu(id)
            if payments==[]:
                m1.addParam('empty', True)
            else:
                string = ""
                for x in payments:
                    string = string + x + "\n"
                m1.addParam('list', string)
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                select = m2.getParam('select')
                requestRefund(select, payments)
                m1.addParam('message', "Refund requested successfully...\n")

        if type=='CANC':
            m1.setType('GOOD')
            menu = showCancelMenu(id)
            if payments==[]:
                m1.addParam('empty', True)
            else:
                string = ""
                for x in payments:
                    string = string + x + "\n"
                m1.addParam('list', string)
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                select = m2.getParam('select')
                cancel(select, menu)
                m1.addParam('message', "Transaction canceled successfully...\n")

        if type=='INTR':
            m1.setType('GOOD')
            pending = intro(id)
            print(pending)
            list = pending[0]
            if list==[]:
                m1.addParam('empty', True)
                m1.addParam('size', pending[1])
            else:
                m1.addParam('empty', False)
                m1.addParam('size', pending[1])
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print("receiving message: ", m2)
                word = ["payment", "request", "refund"]
                for x in list:
                    if word[0] in x:
                        m1.addParam('type', word[0])
                        m1.addParam('transaction', x)
                        m1.addParam('next', True)
                        cproto.putMessage(m1)
                        m2 = cproto.getMessage()
                        print("receiving message: ", m2)
                        processPayment(id, x, word[0])
                    if word[1] in x:
                        m1.addParam('type', word[1])
                        m1.addParam('transaction', x)
                        m1.addParam('next', True)
                        cproto.putMessage(m1)
                        m2 = cproto.getMessage()
                        print("receiving message: ", m2)
                        response = m2.getParam('response')
                        processPayment(id, x, word[0])
                    if word[2] in x:
                        m1.addParam('type', word[2])
                        m1.addParam('transaction', x)
                        m1.addParam('next', True)
                        cproto.putMessage(m1)
                        m2 = cproto.getMessage()
                        print("receiving message: ", m2)
                        response = m2.getParam('response')
                        processPayment(id, x, word[0])
                m1.addParam('next', False)

        cproto.putMessage(m1)               # send socket to client
        cproto.close()                      # close the conn socket
    
    serversoc.close()                       # close the server