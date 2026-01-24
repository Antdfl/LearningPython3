# generator function
def generate(number):
    i = 0
    while i < number:
        yield i
        i += 1

for n in generate(1_000_000):
    print(n)