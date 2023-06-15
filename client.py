import socket
from cprotocol import Cprotocol
from cmessage import Cmessage

if __name__ == '__main__':
    current = 'TOP MENU'
    force_exit = False

    while True:
        conn = socket.socket()                  # defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
        conn.connect(("localhost", 5000))       # connect to localhost:5000

        # run the application protocol
        cproto = Cprotocol(conn)

        m1 = Cmessage()

        if current=='TOP MENU':
            if force_exit==True:
                response = '99'
            else:
                print("Type the number of the action you want to perform:")
                print("1. Create User\n2. Login\n99. Exit")
                response = input()
            if response=='1':
                m1.setType('CRE8')
                username = input("Enter username: ")
                password = input("Enter password: ")
                m1.addParam('username', username)
                m1.addParam('password', password)
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print(m2.getParam('message'))
            elif response=='2':
                m1.setType('LGIN')
                username = input("Enter username: ")
                password = input("Enter password: ")
                m1.addParam('username', username)
                m1.addParam('password', password)
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print(m2.getParam('message'))
                if m2.getType() == 'GOOD':
                    current = 'INTRO'
                    cproto.close()
                    continue
            elif response=='99':
                m1.setType('EXIT')
                m1.addParam('message', "done")
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print(m2.getParam('message'))
                cproto.close()
                break
            else:
                m1.setType('ERRO')
                m1.addParam('error', "inextistent option")
                print("Option " + response + " does not exist\n\n")
                cproto.putMessage(m1)
                cproto.close()
                continue
        
        if current=='INTRO':
            m1.setType('INTR')
            m1.addParam('message', "requesting check")
            cproto.putMessage(m1)
            m2 = cproto.getMessage()
            empty = m2.getParam('empty')
            size = m2.getParam('size')
            if empty=="True":
                string = "You have 0 pending transactions to check...\n"
                print(string)
                current = 'MAIN MENU'
                cproto.close()
                continue
            else:
                string = "You have " + size + " pending transactions to check:\n"
                print(string)
                current='PROCESSING'
                cproto.close()
                continue

        if current=='PROCESSING':
            m1.setType('PROC')
            m1.addParam('message', "requesting next pending transaction")
            cproto.putMessage(m1)
            m2 = cproto.getMessage()
            next = m2.getParam('next')
            empty = m2.getParam('empty')
            if empty=="True":
                current = 'MAIN MENU'
                cproto.close()
                continue
            else:
                next = m2.getParam('next')
                category = m2.getParam('category')
                print(next)
                if category=='payment':
                    response = input("Press any key to continue: ")
                    response = 'accept'
                elif category=='request':
                    response = input("Press y to accept or n to decline: ")
                    if response=='y':
                        response = 'accept'
                    elif response=='n':
                        response = 'decline'
                    else:
                        response = 'unknown'
                elif category=='refund':
                    response = input("Press y to accept or n to decline: ")
                    if response=='y':
                        response = 'accept'
                    elif response=='n':
                        response = 'decline'
                    else:
                        response = 'unknown'
                m1.addParam('response', response)
                cproto.putMessage(m1)
                m2 = cproto.getMessage()
                print(m2.getParam('message'))
                cproto.close()
                continue

        if current=='MAIN MENU':
                print("Type the number of the action you want to perform:")
                print("1. Pay\n2. Request\n3. Cancel\n4. Add Money\n5. Check History\n6. Show Balance\n7. Refund\n98. Logout\n99. Exit")
                response = input()
                if response=='1':
                    m1.setType('PAY2')
                    target = input("Enter the username of who you want to pay: ")
                    m1.addParam('target', target)
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    if m2.getType()=='GOOD':
                        print(m2.getParam('message'))
                        try:
                            amount = float(input("Enter amount: "))
                        except:
                            print("What you entered was not a valid number...\n")
                            cproto.close()
                            continue
                        else:
                            m1.addParam('amount', amount)
                            cproto.putMessage(m1)
                            m2 = cproto.getMessage()
                            print(m2.getParam('message'))
                            if m2.getType()=='GOOD':
                                reason = input("State the reason of the payment: ")
                                m1.addParam('reason', reason)
                                cproto.putMessage(m1)
                                m2 = cproto.getMessage()
                                print(m2.getParam('message'))
                    elif m2.getType()=='ERRO':
                        print(m2.getParam('message'))
                    else:
                        print("something went wrong...\n")
                elif response=='2':
                    m1.setType('REQT')
                    target = input("Enter the username of who you want to request from: ")
                    m1.addParam('target', target)
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    if m2.getType()=='GOOD':
                        print(m2.getParam('message'))
                        try:
                            amount = float(input("Enter amount: "))
                        except:
                            print("What you entered was not a valid number...\n")
                            cproto.close()
                            continue
                        else:
                            m1.addParam('amount', amount)
                            reason = input("State the reason of the request: ")
                            m1.addParam('reason', reason)
                            cproto.putMessage(m1)
                            m2 = cproto.getMessage()
                            print(m2.getParam('message'))
                    elif m2.getType()=='ERRO':
                        print(m2.getParam('message'))
                    else:
                        print("something went wrong...\n")
                elif response=='3':
                    m1.setType('CANC')
                    m1.addParam('message', "requesting list")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    if m2.getParam('empty')=="True":
                        print("Your pending history is empty...\n")
                    else:
                        print("Your pending history:")
                        list = m2.getParam('list')
                        size = m2.getParam('size')
                        print(list)
                        ans = input("Type the number of the transaction you want to cancel: ")
                        select = int(ans)
                        if isinstance(select, int):
                            if (select < 1) or (select > int(size)):
                                print("You need to enter a number within the indexes of the list...\n")
                                m1.addParam('error', "True")
                                m1.addParam('select', select)
                                cproto.putMessage(m1)
                                m2 = cproto.getMessage()
                                cproto.close()
                                continue
                            m1.addParam('error', "False")
                            m1.addParam('select', select)
                            cproto.putMessage(m1)
                            m2 = cproto.getMessage()
                            print(m2.getParam('message'))
                        else:
                            print("What you entered was not a valid number...\n")
                            m1.addParam('error', "True")
                            cproto.putMessage(m1)
                            cproto.close()
                            continue
                elif response=='4':
                    m1.setType('ADDM')
                    try:
                        amount = float(input("Enter amount: "))
                    except:
                        print("What you entered was not a valid number...\n")
                        cproto.close()
                        continue
                    else:
                        source = input("State the source of the money: ")
                        m1.addParam('amount', amount)
                        m1.addParam('source', source)
                        cproto.putMessage(m1)
                        m2 = cproto.getMessage()
                        print(m2.getParam('message'))
                elif response=='5':
                    m1.setType('CKHI')
                    m1.addParam('message', "requesting history")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    print(m2.getParam('message'))
                elif response=='6':
                    m1.setType('SHBL')
                    m1.addParam('message', "requesting balance")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    print(m2.getParam('message'))
                elif response=='7':
                    m1.setType('REFU')
                    m1.addParam('message', "requesting refund")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    if m2.getParam('empty')=="True":
                        print("No history in your transaction was found...\n")
                    else:
                        print("Your payments history:\n")
                        list = m2.getParam('list')
                        size = m2.getParam('size')
                        print(list)
                        try:
                            select = int(input("Type the number of the payment you want to request a refund for: "))
                            if (select < 1) or (select > int(size)):
                                print("You need to enter a number within the indexes of the list...\n")
                                m1.addParam('error', "True")
                                m1.addParam('select', select)
                                cproto.putMessage(m1)
                                m2 = cproto.getMessage()
                                cproto.close()
                                continue
                        except:
                            print("What you entered was not a valid number...\n")
                            m1.addParam('error', "True")
                            m1.addParam('select', select)
                            cproto.putMessage(m1)
                            m2 = cproto.getMessage()
                            cproto.close()
                            continue
                        else:
                            m1.addParam('error', "False")
                            m1.addParam('select', select)
                            cproto.putMessage(m1)
                            m2 = cproto.getMessage()
                            print(m2.getParam('message'))
                elif response=='98':
                    m1.setType('LOUT')
                    m1.addParam('message', "done")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    print(m2.getParam('message'))
                    if m2.getType() == 'GOOD':
                        current = 'TOP MENU'
                        cproto.close()
                        continue
                elif response=='99':
                    m1.setType('LOUT')
                    m1.addParam('message', "done")
                    cproto.putMessage(m1)
                    m2 = cproto.getMessage()
                    print(m2.getParam('message'))
                    if m2.getType() == 'GOOD':
                        current = 'TOP MENU'
                        force_exit = True
                        cproto.close()
                        continue
                else:
                    m1.setType('ERRO')
                    m1.addParam('error', "inextistent option")
                    print("Option " + response + " does not exist\n\n")
                    cproto.putMessage(m1)
                    cproto.close()
                    continue

        cproto.close()                          # close the conn socket

    conn.close()                            # close the client socket