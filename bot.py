#Ładowanie skryptów
from fbchat import Client
from fbchat.models import *
from bs4 import BeautifulSoup
from requests import get
import random, time, datetime, json, requests, os, sys
import numpy as np

#Logowanie, podaj tutaj dane logowania do konta. Nie zalecam używania swojego głównego, lepiej utworzyć osobne pod bota.####
email = ""                                                                                       #
password = ""                                                                                                    #
#                                                                                                                          #
#Tu podaj ID swojego głównego konta (jest to swego rodzaju uprzywilejowany użytkownik)######################################
admin = "ADMIN_ID_GOES_HERE"                                                                                               #
############################################################################################################################
kolorki = [ThreadColor.BILOBA_FLOWER, ThreadColor.BRILLIANT_ROSE, ThreadColor.CAMEO, ThreadColor.DEEP_SKY_BLUE, ThreadColor.FERN, ThreadColor.FREE_SPEECH_GREEN, ThreadColor.GOLDEN_POPPY, ThreadColor.LIGHT_CORAL, ThreadColor.MEDIUM_SLATE_BLUE, ThreadColor.MESSENGER_BLUE]




#!miejski, słownik oparty o biblioteke BS4.
def urban_dictionary(word):
    word = word.replace(" ", "+")
    response = requests.get("https://www.miejski.pl/slowo-" + word)
    if response.status_code == 404:
        response = None
        return "Brak takiego słowa."
    else:
        parsed = BeautifulSoup(response.text, "html.parser")
        title = parsed.body.find("h1").get_text()
        definition = parsed.find("div", "definition summary").get_text()
        example = parsed.find("div", "example").get_text()
        message = title + "\nDefinicja:" + definition + "\n\nPrzyklad/y:" + example
        parsed = None
        response = None
        return message


class Bot(Client):
    banned = np.load("banned.npy").tolist()
    def mentions(self, thread_id):
        thread = list(self.fetchThreadInfo(thread_id)[thread_id].participants)
        mention = []
        for i in range(len(thread)):
            mention.append(Mention(thread[i], 0, 9))
        return mention
#Automatyczna nazwa nicku. Zawrzyj go w pliku names.npy podczas jego generacji.
# import numpy as np
# np.save("names", "nazwa")
    def onNicknameChange(self, mid=None, author_id=None, changed_for=None, new_nickname=None, thread_id=None, thread_type=ThreadType.USER, ts=None, metadata=None, msg=None):
        if author_id != self.uid:
            if changed_for == self.uid:
                if new_nickname != np.load("nazwa.npy"):
                    abcdef = np.load("nazwa.npy")
                    self.changeNickname(str(abcdef), str(self.uid), str(thread_id), thread_type)
#Re-login
    def onListenError(self, exception=None):
        print(exception)
        if self.isLoggedIn():
            pass
        else:
            self.login(email, password)

    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None,
                  thread_type=ThreadType.USER, ts=None, metadata=None, msg=None):
        # self.markAsDelivered(thread_id, message_object.uid)
        # self.markAsRead(thread_id)
        print(message_object)
        print(message_object.text)
        if author_id in self.banned and author_id != admin:
            pass
        elif author_id != self.uid:
            if author_id == admin:
                if message_object.text[0:7] == "!nazwa ":
                    a = message_object.text.replace("!nazwa ", "")
                    np.save("nazwa", a)
                    b = self.fetchThreadList()
                    for c in b:
                        self.changeNickname(a, self.uid, c.uid, c.type)
                elif message_object.text[0:4] == "!bc ":
                    a = message_object.text.replace("!bc ", "")
                    b = self.fetchThreadList()
                    for c in b:
                        self.send(Message(a), c.uid, c.type)
                elif message_object.text[0:3].lower() == "!r ":
                    react = message_object.text.lower().replace("!r ", "")
                    react = react.split(" ")
                    s = self.fetchThreadMessages(thread_id, int(react[0])+int(react[1]))
                    if react[2] == "angry":
                        react[2] = MessageReaction.ANGRY
                    elif react[2] == "smile":
                        react[2] = MessageReaction.SMILE
                    elif react[2] == "sad":
                        react[2] = MessageReaction.SAD
                    elif react[2] == "wow":
                        react[2] = MessageReaction.WOW
                    elif react[2] == "love":
                        react[2] = MessageReaction.LOVE
                    elif react[2] == "yes":
                        react[2] = MessageReaction.YES
                    elif react[2] == "no":
                        react[2] = MessageReaction.NO

                    for a in range(int(react[1])):
                        self.reactToMessage(s[int(react[0])+a].uid, react[2])
                elif message_object.text == "!ip":
                    if thread_type == ThreadType.USER:
                        ip = get("https://api.ipify.org").text
                        self.send(Message("Moje IP: "+ip), thread_id, thread_type)
                        ip = None
                    else:
                        self.send(Message("Moje IP to 127.0.0.1"), thread_id, thread_type)
                elif message_object.text[0:5].lower() == "!ban ":
                    a = message_object.mentions[0].thread_id
                    b = self.fetchUserInfo(a)[a]
                    self.banned.append(b.uid)
                    np.save("banned", self.banned)
                    self.send(Message("Zbanowano @"+b.name, [Mention(b.uid, 10, len(b.name)+1)]), thread_id, thread_type)
                elif message_object.text[0:7].lower() == "!unban ":
                    a = message_object.mentions[0].thread_id
                    b = self.fetchUserInfo(a)[a]
                    self.banned.remove(b.uid)
                    np.save("banned", self.banned)
                    self.send(Message("Odbanowano @"+b.name, [Mention(b.uid, 11, len(b.name)+1)]), thread_id, thread_type)
                elif message_object.text[0:6].lower() == "!bomb ":
                    a = message_object.text.split(" ")
                    parameters = {"inputUserMobile": a[1]}
                    self.send(Message("Zaczynam wysyłać"), thread_id, thread_type)
                    for i in range(int(a[2])):
                        adres = "http://gry.wapster.pl/ma/send.aspx?src=wap2&fid="+str(random.choice(self.gamelist))+"&r=LPH"
                        r = requests.post(adres, data=parameters)
                    self.send(Message("Wysłano "+a[2]+" wiadomosci na numer "+a[1]), thread_id, thread_type)
                
                pass

#komendy na pieski, na kotki, ptaszki, pandy i na przepiękne shiby
                if message_object.text.lower() == "!doggo":
                    response = requests.get("https://dog.ceo/api/breeds/image/random")
                    dog = json.loads(response.text)
                    self.sendRemoteImage(dog["message"], None, thread_id, thread_type)
                elif message_object.text.lower() == "!catto":
                    response = requests.get("https://api.thecatapi.com/v1/images/search", headers)
                    cat = json.loads(response.text)
                    self.sendRemoteImage(cat[0]["url"], None, thread_id, thread_type)
                elif message_object.text.lower() == "!birb":
                    response = requests.get("http://random.birb.pw/tweet.json")
                    bird = json.loads(response.text)
                    self.sendRemoteImage("https://random.birb.pw/img/" + bird["file"], None, thread_id, thread_type)
#tęcza, kolorki u góry; tu właśnie widać uprawnienia admina; tylko on może wykonać tą komendę, innym zwróci wiadomość poniżej
            if message_object.text[0:15].lower() == "tęcza":
                if author_id == admin:
                    for i in range(10):
                        self.changeThreadColor(random.choice(kolorki), thread_id)
                    self.changeThreadColor(ThreadColor.BRILLIANT_ROSE, thread_id)
                    self.changeThreadColor(ThreadColor.BRILLIANT_ROSE, thread_id)
                else:
                    self.send(Message("Sam sobie zrób tęczę."), thread_id, thread_type)
					
#odliczanie do świąt, ferii, wakacji; wszystko dostosowane jest do TK25
            elif message_object.text.lower() == "czas":
                now = datetime.datetime.now()
                tera = now.strftime("%A %d %B %H:%M")
                tera = tera.replace("September", "Września")
                tera = tera.replace("August", "Sierpnia")
                tera = tera.replace("October", "Października")
                tera = tera.replace("November", "Listopada")
                tera = tera.replace("December", "Grudnia")
                tera = tera.replace("Saturday", "Sobota")
                tera = tera.replace("Sunday", "Niedziela")
                tera = tera.replace("Monday", "Poniedziałek")
                tera = tera.replace("Tuesday", "Wtorek")
                tera = tera.replace("Wednesday", "Środa")
                tera = tera.replace("Thursday", "Czwartek")
                tera = tera.replace("Friday", "Piątek")
                czas = round(time.time())-3600
                czasdoswiat = 1545350400 - czas
                czasdoferii = 1547078400 - czas
                czasdowakacji = 1561068000 - czas
                wiadomosc = "Jest: " + tera + "\nPoczątek przerwy świątecznej (21 grudnia) za: " + str(int((czasdoswiat - czasdoswiat % 86400) / 86400)) + "dni " + time.strftime("%Hh %Mmin %Ssek", time.gmtime(int(round(czasdoswiat))))\
							+ "\nPoczątek ferii (10 stycznia) za: " + str(int((czasdoferii - czasdoferii % 86400) / 86400)) + "dni " + time.strftime("%Hh %Mmin %Ssek", time.gmtime(int(round(czasdoferii))))\
                            + "\nKoniec roku szkolnego za: " + str(int((czasdowakacji - czasdowakacji % 86400) / 86400)) + "dni " + time.strftime("%Hh %Mmin %Ssek", time.gmtime(int(round(czasdowakacji))))
                self.send(Message(wiadomosc), thread_id, thread_type)
				#plan lekcji stworzony jest na podobnej konstrukcji; tutaj dla 1IA TK25
            elif message_object.text.lower() == "!plan":
                now = datetime.datetime.now()
                tera = now.strftime("%A")
                tera = tera.replace("Monday", "Poniedziałek")
                tera = tera.replace("Tuesday", "Wtorek")
                tera = tera.replace("Wednesday", "Środa: Początek lekcji 7:30\nNumer lekcji; Nazwa; Długość przerwy\n1. Matematyka 5 minut\n2. Angielski\WF 5 minut\n3. WF\Angielski 10 minut\n4. Historia 10 minut\n5. Fizyka 10 minut\n6. EDB 5 minut\n7. Polski")
                tera = tera.replace("Thursday", "Czwartek: Początek lekcji 9:10\nNumer lekcji; Nazwa; Długość przerwy\n3. Chemia 5 minut\n4. Polski 10 minut\n5. Przedsiębiorczość 10 minut\n6. Wychowawcza 5 minut\n7. Matematyka 20 minut\n8. UTK 5 minut\n9. Geografia 5 minut\n10. Historia")
                tera = tera.replace("Friday", "Piątek: Początek lekcji 8:20\7:30 \nNumer lekcji; Nazwa; Długość przerwy\n1. Brak\SysOp 5 minut\n2. SysOp\Informatyka 5 minut\n3. Religia 10 minut\n4. Religia 10 minut\n5. UTK 10 minut\n6. Biologia 5 minut\n7. Informatyka\SysOp 20 minut\n8. WDŻ")
                wiadomosc = "Dzisiejsze lekcje: " + tera
                self.send(Message(wiadomosc), thread_id, thread_type)
            elif message_object.text.lower() == "!planpiątek":
                self.send(Message("Piątek: Początek lekcji 8:20/7:30 \nNumer lekcji; Nazwa; Długość przerwy\n1. Brak\SysOp 5 minut\n2. SysOp\Informatyka 5 minut\n3. Religia 10 minut\n4. Religia 10 minut\n5. UTK 10 minut\n6. Biologia 5 minut\n7. Informatyka\SysOp 20 minut\n8. WDŻ"), thread_id, thread_type)
#przykład komend zwracających tekst:
            elif message_object.text.lower() == "komenda":
                self.send(Message("działa"), thread_id, thread_type)
#oznaczanie wszystkich: zarezerw. dla admina
            if author_id == admin or author_id == admin:
                if "@everyone" in message_object.text.lower():
                    self.send(Message("@everyone", self.mentions(thread_id)), thread_id, thread_type)

#reakcje do xd
            if "xd" in message_object.text.lower():
                if "Xd" in message_object.text:
                    self.reactToMessage(mid, MessageReaction.ANGRY)
                elif (thread_id != ryz) or self.ryz_commands is True:
                    self.reactToMessage(mid, MessageReaction.SMILE)
#oznaczanie bota, dosyc prymitywne haha
            if thread_id != admin:
                if "wons" in message_object.text.lower():
                    self.send(Message("siema"), thread_id, thread_type)
                    self.reactToMessage(mid, MessageReaction.SMILE)
                elif "michał" in message_object.text.lower():
                    self.send(Message("siema"), thread_id, thread_type)
                    self.reactToMessage(mid, MessageReaction.SMILE)

#miejski
                elif message_object.text.lower()[0:9] == "!miejski ":
                    word = message_object.text.replace("!miejski ", "")
                    self.send(Message(urban_dictionary(word)), thread_id, thread_type)
                    word = None

bot = Bot(email, password)
bot.listen()
