import pandas as pd
import os
os.system('cls')

nato_df = pd.read_csv('./NATO-alphabet/nato_phonetic_alphabet.csv')
#TODO 1. Create a dictionary in this format:
#{"A": "Alfa", "B": "Bravo"}
phonetic_dict = {row.letter:row.code for (index, row) in nato_df.iterrows()}
#print(phonetic_dict)
#TODO 2. Create a list of the phonetic code words from a word that the user inputs.
user_input = input("Enter a word:").upper()
# Translate the list of letters from user into a Nato letter list
word_translated_list = [phonetic_dict[letter] for letter in user_input if letter in phonetic_dict]
print(word_translated_list)
