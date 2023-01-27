import srt
import re
from genanki import Model, Note, Deck
from deep_translator import GoogleTranslator
import glob

TARGET_LANG = "it"
NATIVE_LANG = "fr"
SRT_FILE = "Il_Principe_dei_draghi_S01E04.srt"
ANKI_FILE_DST = "Il_Principe_dei_draghi_S01E04.apkg"
CSV_FILE = "Il_Principe_dei_draghi_S01E04.csv"
WORD_ALREADY_LEARNED = "word_already_learned.txt"


BASIC_WITH_SAMPLE_MODEL = Model(
  1559383000,
  'Basic with sample',
  fields=[
    {
      'name': 'Front',
      'font': 'Arial',
    },
    {
      'name': 'Back',
      'font': 'Arial',
    },
    {
      'name': 'Sample',
      'font': 'Arial',
    },
    {
      'name': 'Translated sample',
      'font': 'Arial',
    },
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Front}}',
      'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}\n\n<hr id=answer>\n\n{{Sample}}\n<br/><i>{{Translated sample}}</i>',
    },
  ],
  css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n.sample {\n font-family: arial;\n font-size: 14px;\n text-align: center;\n color: black;\n background-color: white;\n}',
)



class Sentence:

    def __init__(self,sentence):
        self.sentence=sentence
        self.translation=None

class Word:
    def __init__(self,word:str,sentence:str):
        self.word = word
        self.translation = None
        self.occur=1
        self.sentence = Sentence(sentence)

    def get_sentence(self):
        if self.sentence is not None :
            return self.sentence.sentence
        else :
            return "No sentence"    

class Movie:
    def __init__(self,srt_file:str):
        self.srt_file=srt_file
        self.words={}
        self.word_already_known = 0
        self.count_words = 0


    def add_word(self,word:Word):
        if word.word in self.words :
            self.words[word.word].occur+=1
        else :
            self.words[word.word]=word # on l'ajoute au dictionnaire des mots du film avec comme clef son libellé


    def read_and_parse(self):
        with open(self.srt_file) as f:
            self.text = f.read()
        self.parsed = srt.parse(self.text)
        self.parsed = list(self.parsed)
        self.length_in_seconds = self.parsed[-1].end.total_seconds()
        self.parsed = [self.cleanhtml(x.content) for x in self.parsed]
        for row in self.parsed:
            row_cleaned = self.cleanword(row)
            words = row_cleaned.split()
            for word in words:
                self.count_words+=1
                self.add_word(Word(word.lower(),row))   

    def sort_word(self):
        self.words = dict(sorted(self.words.items(), key=lambda item: item[1].occur,reverse=True))

    def cleanhtml(self,raw_html):
        cleanr = re.compile('<.*?>')
        cleaned = raw_html.replace('&nbsp;', '')
        cleantext = re.sub(cleanr, '', cleaned)
        cleantext = cleantext.replace('{\an8}','')
        cleantext = cleantext.replace('\n',' ')
        return cleantext  

    def cleanword(self, word):
        word = word.replace(',','')
        word = word.replace('-','')
        word = word.replace('\n',' ')
        word = word.replace('?','')
        word = word.replace('!','')
        word = word.replace('.','')
        word = word.replace(':','')
        word = word.replace('+','')
        word = word.replace('\'',' ')
        word = word.replace('…','')
        
        return word   

    def check_word(word):
        if word.word.isdigit():
            return False
        if word.occur==1 :
            return False
        if word.word in words_already_learned :
            return False
        return True            
        

    def translate(self):
        translator =  GoogleTranslator(source="it",target="fr")
        for word_str,word in self.words.items():
            if not Movie.check_word(word):
                continue
            word.translation = translator.translate(word.word)
            print("word : ",word.word,word.translation)
            
            word.sentence.translation = translator.translate(word.sentence.sentence)
            print("it:",word.sentence.sentence)
            print("fr:",word.sentence.translation)

    def generate_anki_id(string):
        return abs(hash(string)) % (10 ** 10)

    def generate_deck(self,deck_name):
        deck_name = deck_name.replace(" ","")
        deck = Deck(
            Movie.generate_anki_id(deck_name),
            deck_name)

        for word_str,word in self.words.items():
            if not Movie.check_word(word):
                continue
            deck.add_note(Note(
                model=BASIC_WITH_SAMPLE_MODEL,
                fields=[word.word, word.translation,word.sentence.sentence,word.sentence.translation],
                tags = [deck_name]
                )
            )

        file_path = deck_name
        deck.write_to_file(file_path)

    def generate_csv(self,csv_file_path):
        with open(csv_file_path,"w") as f:
            for word_str,word in self.words.items():
                if not Movie.check_word(word):
                    continue
                f.write(f'"{word.word}","{word.translation}",{word.occur},"{word.sentence.sentence}","{word.sentence.translation}"\n')

          

    def display_words(self):
        count_words = 0
        for word_str,word in self.words.items():
            count_words+=word.occur
            if not Movie.check_word(word):
                continue
            percent = 100 * count_words/movie.count_words 
            print(f"{count_words}/{movie.count_words} ({percent:.2f}%): {word_str} ({word.get_sentence()})")

    def display_stat(self):
        count_words = len(self.words)
        print(f"{count_words} differents words / {movie.srt_file} / {movie.length_in_seconds} seconds")
        word_per_hour = 3600 * count_words / self.length_in_seconds
        print(f"{word_per_hour:.2f} words per hour")
        print("-----------------------------")
        

words_already_learned = []

with open(WORD_ALREADY_LEARNED) as f:
    for word in f.readlines():
        words_already_learned.append(word.strip())


movie = Movie(SRT_FILE)
movie.read_and_parse()
movie.sort_word()
movie.display_words()
movie.display_stat()
movie.translate()
movie.generate_deck(ANKI_FILE_DST)   
movie.generate_csv(CSV_FILE) 

# for srt_file in glob.glob("*.srt"):
#     movie = Movie(srt_file)
#     movie.read_and_parse()
#     movie.display_stat()
