
import os
os.system('cls' if os.name == 'nt' else 'clear')

back_to_the_future_trilogy = {
    "title": "Back to the Future Trilogy",
    "movies": [
        {
            "title": "Back to the Future",
            "release_year": 1985,
            "lead_actors": (
                {"name": "Michael J. Fox", "age": 24},
                {"name": "Christopher Lloyd", "age": 47}
            ),
            "runtime_minutes": 116
        },
        {
            "title": "Back to the Future Part II",
            "release_year": 1989,
            "lead_actors": (
                {"name": "Michael J. Fox", "age": 28},
                {"name": "Christopher Lloyd", "age": 51}
            ),
            "runtime_minutes": 108
        },
        {
            "title": "Back to the Future Part III",
            "release_year": 1990,
            "lead_actors": (
                {"name": "Michael J. Fox", "age": 29},
                {"name": "Christopher Lloyd", "age": 52}
            ),
            "runtime_minutes": 118
        }
    ],
    "director": "Robert Zemeckis",
    "producer": "Bob Gale"
}

# print(back_to_the_future_trilogy["movies"][2]["lead_actors"][0]["name"])

movie = back_to_the_future_trilogy["movies"][2] 
actor = movie["lead_actors"][0]
name = actor["name"]
age = actor["age"]
print(f"Actor: {name}, Age: {age}")