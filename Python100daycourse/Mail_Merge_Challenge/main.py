PLACEHOLDER = "[name]"
#DONE: Create a letter using starting_letter.txt 
# Here I found that the difficult part w to nail the exact paths
# to read and write files in different folders
# It all depends on the working directory of your script
# With VS code with .venv it should be the root folder of your project

# Read the starting letter
with open("./Python100daycourse/Mail_Merge_Challenge/Input/Letters/starting_letter.txt") as letter_file:
    letter_contents = letter_file.read()
# Read the invited names
with open("./Python100daycourse/Mail_Merge_Challenge/Input/Names/invited_names.txt") as names_file:
    names = names_file.readlines()
# For each name, create a letter and save it to ReadyToSend folder
    for name in names:
        strip_name = name.strip()
        new_letter = letter_contents.replace(PLACEHOLDER, strip_name)
        with open(f"./Python100daycourse/Mail_Merge_Challenge/Output/ReadyToSend/letter_for_{strip_name}.docx", mode="w") as completed_letters:
            completed_letters.write(new_letter)
#for each name in invited_names.txt
#Replace the [name] placeholder with the actual name.
#Save the letters in the folder "ReadyToSend".
    
#Hint1: This method will help you: https://www.w3schools.com/python/ref_file_readlines.asp
    #Hint2: This method will also help you: https://www.w3schools.com/python/ref_string_replace.asp
        #Hint3: THis method will help you: https://www.w3schools.com/python/ref_string_strip.asp