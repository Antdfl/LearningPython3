school_class = {}

while True:
    name = input("Enter the student's name: ")
    if name == '':
        print("Exit: no new names")
        break
    
    score = int(input("Enter the student's score (0-10): "))
    if score not in range(0, 11):
        print("score ", score,"not in range or not a number")
        break
	
    if name in school_class:
        school_class[name] += (score,)
    else:
        school_class[name] = (score,)
        
for name in sorted(school_class.keys()):
    adding = 0
    counter = 0
    for score in school_class[name]:
        adding += score
        counter += 1
    print(name, ":", adding / counter)
