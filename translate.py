import googletrans
import random
import time

trans = googletrans.Translator()

lang_codes = googletrans.LANGCODES

class Session:
    def __init__(self, lang):
        self.qls = []
        self.lang = lang_codes[lang.lower()]
        with open("questions.txt", "r") as questions:
            for i in questions:
                self.qls.append(i)

    def question(self): #translates the text based on the language chosen
        question = random.choice(self.qls)
        if __name__ == "__main__": print(question)
        self.qls.remove(question)
        return translate(question, self.lang)

def translate(text, lang):
    c = 0
    while c < 5:
        try:
            c += 1
            return trans.translate(text, lang).text
        except:
            time.sleep(1)
    return "googletranslate failed"
#
s = Session('Spanish')
print(s.question())

print(translate("Hi I am henry", "es"))