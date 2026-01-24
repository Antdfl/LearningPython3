from pizza import make_pizza as mp

pizza_ai_peperoni = mp(16, 'pepperoni')
pizza_ai_funghi = mp(12, 'mushrooms', 'green peppers',
                                     'extra cheese')
print(pizza_ai_peperoni)
print(pizza_ai_funghi)