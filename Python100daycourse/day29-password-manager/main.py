from tkinter import *     # pyright:ignore
from tkinter import messagebox
import random
import json
import pyperclip
# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate_password():
    password_entry.delete(0, END)
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)

    password_letters = [random.choice(letters) for _ in range(nr_letters)]
    password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
    password_numbers = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = password_letters + password_symbols + password_numbers

    random.shuffle(password_list)

    password = "".join(password_list)

    #print(f"Your password is: {password}")
    password_entry.insert(0, password)
    pyperclip.copy(password)

# ---------------------------- SAVE PASSWORD ------------------------------- #
# write all the into the data.txt file in the format:
# website | email/username | password
def save():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    new_data = {website: {
        "email": email, "password": password
                           }
                }
    # Validation: check if any field is empty
    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="The website and password fields cannot be left empty.")
    else:
        try:
            with open("data.json", "r") as data_file:
                # Read the existing data
                data = json.load(data_file)
                # Update the existing data with the new data
                data.update(new_data)
        except FileNotFoundError:
            with open("data.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            # Saving back to the file in case the file exists
            with open("data.json", "w") as data_file:
                # Saving the updated data
                json.dump(data, data_file, indent=4)
                #print(type(data))
        finally:
            # Clear the fields to prepare a new record to be inserted
            #messagebox.showinfo(title="Success", message=f"Added {website} to the data store.")
            website_entry.delete(0, END)
            email_entry.delete(0, END)
            password_entry.delete(0, END)
            # restore the email default value and the initial focus
            email_entry.insert(0, "antonio@gmail.com")
            website_entry.focus()

# ---------------------------- FIND PASSWORD ------------------------------- #
def find_password():
    try:
        with open("data.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    else:
        # We set the search criterion
        website = website_entry.get()
        # If the website is present we show the popup w
        if website in data:
            email = data[website]["email"]
            password = data[website]["password"]
            messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
        else:
            messagebox.showinfo(title="Error", message=f"Website {website} not found")

# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

canvas = Canvas(window, width=200, height=200 ,highlightthickness=0)
logo_img = PhotoImage(file="./day29-password-manager/logo.png")
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

lbl_website = Label(text="Website:")
lbl_website.grid(row=1, column=0)

lbl_email_username = Label(text="Email/Username:")
lbl_email_username.grid(row=2, column=0)

lbl_password = Label(text="Password:")
lbl_password.grid(row=3, column=0)

website_entry = Entry(window, width=24)
website_entry.grid(row=1, column=1, pady=3, padx=0)
# Set focus to website entry field
website_entry.focus()

email_entry = Entry(window, width=42)
email_entry.insert(0, "antonio@gmail.com")
email_entry.grid(row=2, column=1, columnspan=2, pady=3, padx=0)

password_entry = Entry(window, width=24)
password_entry.grid(row=3, column=1, pady=3, padx=0)

btn_gen_password = Button(window, text="Generate Password", command=generate_password, height=0, width=17)
btn_gen_password.grid(row=3, column=2)

btn_add_entry = Button(window, text="Add", command=save, height=0, width=42)
btn_add_entry.grid(row=4, column=1, columnspan=2)

brn_search = Button(window, text="Search", width=17, command=find_password)
brn_search.grid(row=1, column=2)


window.mainloop()