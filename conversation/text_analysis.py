import os
import re
import csv
from collections import defaultdict, Counter
import nltk 
import spacy
from nltk import word_tokenize, pos_tag
from django.contrib.staticfiles.finders import find

# needs to be done when running the first time
# a gui will pop up, select "all" and click "download"
# nltk.download()

# class to analyze the saved text files 
class TextAnalyzer():
    def __init__(self):
        # Set up the correct path to the saved_chats folder (in parent dir)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.chat_folder_path = os.path.join(os.path.dirname(current_dir), "saved_chats")

        if not os.path.exists(self.chat_folder_path):
            raise FileNotFoundError(f"Directory not found: {self.chat_folder_path}")

        self.all_texts = self.load_texts()
        print("TextAnalyzer constructed and all texts from 'saved_chats' loaded!")

    def load_texts(self):
        all_texts = []

        try:
            text_folder = os.listdir(self.chat_folder_path)
        except FileNotFoundError:
            print(f"Could not find directory: {self.chat_folder_path}")
            return all_texts

        for filename in text_folder:
            file_path = os.path.join(self.chat_folder_path, filename)
            try:
                #create a text_data dict with information on the file
                text_data = {}
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    
                    text_data["filename"] = filename
                    match = re.search(r'MODEL USED:\s*(.*?)\s*===', lines[1])
                    if match:
                        text_data["used_model"] = match.group(1)
                    else:
                        text_data["used_model"] = "unknown"
                    text_data["lines"] = str(len(lines))
                    # TODO: maybe also strip the chat date and time
                    text_data["text"] = lines[4:] #strip the decoration and information already in the dict
                    
                    all_texts.append(text_data)
            except Exception as e:
                print(f"Could not load {filename}: {e}")
        
        return all_texts
    
    # sum up function to gather all information
    def get_stats(self):
        stats = {}
        choices = self.get_choice_freq()
        models = self.get_model_freq()
        proper_nouns = self.get_nnp(5)

        stats["most_popular_choice"] = choices[0]
        stats["most_popular_choice_percent"] = choices[1]
        stats["least_popular_choice"] = choices[2]
        stats["least_popular_choice_percent"] = choices[3]
        # choices[4] would be the the whole distribution
        stats["most_popular_model"] = models[0]
        stats["most_popular_model_percent"] = models[1]
        stats["least_popular_model"] = models[2]
        stats["least_popular_model_percent"] = models[3]
        stats["most_common_proper_nouns"] = proper_nouns

        # put other calls to calculations here and save in dict 'stats'

        return stats
    
    #counts the choices
    def get_choice_freq(self):

        choice_absolute_frequencies = {"1": 0,
                                       "2": 0,
                                       "3": 0,
                                       "4": 0}

        for i in range(len(self.all_texts)):
            for j in self.all_texts[i]['text']:
                if "USER" in j:
                    choice_absolute_frequencies[j[-2]] += 1

        frequencies_overall = choice_absolute_frequencies.values()

        try:
            highest_freq = max(choice_absolute_frequencies, key=choice_absolute_frequencies.get)
            highest_freq_percent = (choice_absolute_frequencies[highest_freq] / sum(frequencies_overall))*100
            lowest_freq = min(choice_absolute_frequencies, key=choice_absolute_frequencies.get)
            lowest_freq_percent = (choice_absolute_frequencies[lowest_freq] / sum(frequencies_overall))*100
        except Exception: # in case there are no prompt files
            highest_freq = 0
            lowest_freq = 0
            highest_freq_percent = 0
            lowest_freq_percent = 0


        return highest_freq, round(highest_freq_percent,2), lowest_freq, round(lowest_freq_percent,2), choice_absolute_frequencies
    
    #counts the models
    def get_model_freq(self):

        model_absolute_frequencies = {"openai/gpt-4o": 0,
                                      "openai/gpt-4o-mini": 0,
                                      "mistral/mistral-large-latest": 0,
                                      "deepseek/deepseek-chat": 0,
                                      "groq/llama3.1-8b (hosted locally)": 0}
        
        for i in self.all_texts:
            if i["used_model"] in model_absolute_frequencies.keys():
                model_absolute_frequencies[i['used_model']] +=1

        frequencies_overall = model_absolute_frequencies.values()

        try:
            highest_freq = max(model_absolute_frequencies, key=model_absolute_frequencies.get)
            highest_freq_percent = (model_absolute_frequencies[highest_freq] / sum(frequencies_overall))*100
            lowest_freq = min(model_absolute_frequencies, key=model_absolute_frequencies.get)
            lowest_freq_percent = (model_absolute_frequencies[lowest_freq] / sum(frequencies_overall))*100
        except Exception:
            # in case there are no prompt files
            highest_freq = 0
            lowest_freq = 0
            highest_freq_percent = 0
            lowest_freq_percent = 0

        return highest_freq, round(highest_freq_percent,2), lowest_freq, round(lowest_freq_percent), model_absolute_frequencies
    
    # counts all the named entities in all texts
    def get_named_entities(self):
        # Use defaultdict with Counter to track frequency of each named entity per label
        all_named_entities = defaultdict(Counter)

        try:
            for entry in self.all_texts:
                for text in entry['text']:
                    nlp = spacy.load('en_core_web_sm')
                    doc = nlp(text)
                    for ent in doc.ents:
                        entity = ent.text
                        label = ent.label_
                        all_named_entities[label][entity] += 1
            # Write to CSV
            with open("output.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Entity Type", "Entity", "Frequency"])

                for label, entities in all_named_entities.items():
                    for entity, freq in entities.items():
                        writer.writerow([label, entity, freq])

        except Exception as e:
            print(f"An error occurred! {e}")
        
        return all_named_entities
    
    # get all proper nouns 
    def get_nnp(self, top=5):
        all_proper_nouns = Counter()
        nlp = spacy.load('en_core_web_sm')
        try:
            for entry in self.all_texts:
                for text in entry['text']:
                    
                    doc = nlp(text)
                    for token in doc:
                        if token.tag_ == "NNP" and token.lemma_ != "ROBOPSY" and token.lemma_ != "*" and "2025" not in token.text:
                            proper_noun = token.text
                            all_proper_nouns[proper_noun] += 1
        except Exception as e:
            print(f"An error occurred! {e}")

        most_freq = all_proper_nouns.most_common(top)
        
        try:
            max_count = most_freq[0][1]
            normalized_data = [(word, count, "{:.2f}".format((count / max_count) * 100)) for word, count in most_freq]
        except Exception:
            normalized_data = []


        return normalized_data