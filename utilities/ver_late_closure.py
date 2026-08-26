
# funcs = [lambda: i for i in range(3)]
# print(funcs)
# print([f() for f in funcs])   # stampa [2, 2, 2], non [0, 1, 2]

# funcs = [lambda: i for i in range(3)]
# i = 99                              # cambio i DOPO aver creato le lambda
# print([f() for f in funcs])        # cosa stampa adesso?

funcs = []
for i in range(3):
    funcs.append(lambda: i)
i = 99                          # ora i e' la STESSA variabile catturata dalle lambda
print([f() for f in funcs])     # adesso esce [99, 99, 99]