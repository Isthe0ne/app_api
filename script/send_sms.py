from twilio.rest import Client

def send(exp, num, msg):
    # Twilio credentials
    account_sid = os.environ.get('SID')
    auth_token = os.environ.get('TOKEN')
    client = Client(account_sid, auth_token)


    exp = exp
    num = num
    msg = msg

    try:
        client.messages.create(from_=exp,to=num,body=msg)
    except:
        print("Oops!!")

    print("Done!")


