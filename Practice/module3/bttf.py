import os
os.system('cls' if os.name == 'nt' else 'clear')

back_to_the_future = {
    "title": "Back to the Future",
    "release_year": 1985,
    "director": "Robert Zemeckis",
    "producer": "Bob Gale",
    "lead_actors": ["Michael J. Fox", "Christopher Lloyd", "Lea Thompson", "Crispin Glover"],
    "genre": "Sci-Fi, Adventure, Comedy",
    "runtime_minutes": 116,
    "plot_summary": ("Marty McFly, a teenager, is accidentally sent 30 years into the past"
                     " in a time-traveling Delorean invented by his close friend, eccentric"
                     " scientist Doc Brown. Marty encounters young versions of his parents"
                     " and must ensure they fall in love or risk altering the course of history.")
}
# We can write a multi-line comment like this, by using round parentheses
# This is useful for providing detailed explanations or documentation

keys = back_to_the_future.keys()
values = back_to_the_future.values()
items = back_to_the_future.items()

back_to_the_future.pop("plot_summary")
back_to_the_future.clear()
# for k in keys:
#     print(k, back_to_the_future[k], sep="=")
# The code above defines a dictionary for the movie "Back to the Future"
# print(values)
print(items)
