favorite_languages = {
    'jen': ['python', 'rust'],
    'sarah': ['c'],
    'edward': ['rust', 'go'],
    'phil': ['python', 'haskell'],
    }

# for name, languages in favorite_languages.items():
#     if len(languages) > 1:
#         print(f"\n{name.title()}'s favorite languages are:")
#         for language in languages:
#            print(f"\t{language.title()}")
#     else:
#         print(f"\n{name.title()}'s favorite language is:")
#         print(f"\t{languages[0].title()}")

users = {
    'aeinstein': {
        'first': 'albert', 
        'last': 'einstein',
        'location': 'princeton',
        },
    'mcurie': {
        'first': 'marie',
        'last': 'curie',
        'location': 'paris',
        },
    }

for username, user_info in users.items(): 
    print(f"\nUsername: {username}") 
    full_name = f"{user_info['first']} {user_info['last']}"
    location = user_info['location']
    print(f"\tFull name: {full_name.title()}")
    print(f"\tLocation: {location.title()}")