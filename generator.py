from time import sleep
import requests
import re
import json

class mailer:
    def __init__(self, userAgent="Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"):
        self.session = requests.session()
        self.session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "upgrade-insecure-requests": "1",
            "user-agent": userAgent
        }

    def create(self, minLen=10, maxLen=10):
        self.session.get("https://temp-mail.io/en")
        #domains = json.loads(self.session.get("https://api.internal.temp-mail.io/api/v2/domains").text)['domains']
        #print("Current Domains are " + domains)
        data = {
            "min_name_length": str(minLen),
            "max_name_length": str(maxLen)
        }
        self.email = json.loads(self.session.post(
            "https://api.internal.temp-mail.io/api/v2/email/new", data=data).text)["email"]
        return self.email

    def readMessages(self):
        return requests.get("https://api.internal.temp-mail.io/api/v2/email/" + self.email + "/messages").content.decode("utf-8")

class shodanGenerator:
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            "origin": "https://account.shodan.io",
            "referer": "https://account.shodan.io/register",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        }

    def createAccount(self, user, passwd="123456789"):
        self.user = user
        self.passwd = passwd
        self.mail = mailer()
        self.mail.create()
        page = self.session.get("https://account.shodan.io/register")
        token = re.search(r'csrf_token.*="(\w*)"',
                          page.content.decode("utf-8")).group(1)
        data = {
            "username": user,
            "password": passwd,
            "password_confirm": passwd,
            "email": self.mail.email,
            "csrf_token": token
        }
        response = self.session.post(
            "https://account.shodan.io/register", data=data).text
        if response.find("Please check the form and fix any errors") is -1:
            self.session.get("https://account.shodan.io/")
            return self.mail.email
        return None

    def activateAccount(self):
        activation = re.search(
            r'(https://account.shodan.io/activate/\w*)', self.mail.readMessages()).group(1)
        self.session.get(activation)
        print("Success!")

    def outro(self):
        token = re.search(r'csrf_token.*="(\w*)"', self.session.get(
            "https://account.shodan.io/login").content.decode('utf-8')).group(1)
        data = {
            "username": self.user,
            "password": self.passwd,
            "grant_type": "password",
            "continue": "https://account.shodan.io/",
            "csrf_token": token,
            "login_submit": "Login",
        }
        self.session.post("https://account.shodan.io/login",
                          data=data).content.decode('utf-8')
        res = self.session.get(
            "https://account.shodan.io/").content.decode('utf-8')
        api = re.search(r'<td>(\w*)<br /><br />', res).group(1)
        print("Your account info: ")
        print("User: " + self.user)
        print("Pass: " + self.passwd)
        print("API Key: " + api)

username = input("Pick a username: ")
gen = shodanGenerator()
if gen.createAccount(username):
    sleep(3)
    gen.activateAccount()
    gen.outro()
else:
    print("Username|Email taken, try again!")
