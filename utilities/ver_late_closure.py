"""Demonstrates Python closures and the concept of late binding.

A closure captures variables by reference (late binding), not by value. This means that a lambda function created inside a loop retains access to the variable itself, rather than its value at creation time.

The commented-out section (lines 2-8) shows an early attempt at this demonstration. The live code block (lines 10-14) demonstrates how reassignment of 'i' *after* the lambdas are created makes the late binding effect visible, resulting in all closures referencing the final value of 'i'.
"""

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