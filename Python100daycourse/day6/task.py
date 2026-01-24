# def turn_right():
#     turn_left()
#     turn_left()
#     turn_left()

# def jump():
#     move()
#     turn_left()
#     move()
#     turn_right()
#     move()
#     turn_right()
#     move()
#     turn_left()

# def jump_n_times(n):
#     for i in range(n):
#         jump()

# jump_n_times(6)


# def turn_right():
# 	turn_left()
# 	turn_left()
# 	turn_left()


# def jump():
# 	turn_left()
# 	while wall_on_right():
# 		move()
# 	turn_right()
# 	move()
# 	turn_right()
# 	while front_is_clear():
# 		move()
# 	turn_left()


# while not at_goal():
# 	if wall_in_front():
# 		jump()
# 	else:
# 		move()

# ----


# def turn_right():
# 	turn_left()
# 	turn_left()
# 	turn_left()


# while not at_goal():
# 	while front_is_clear() and not at_goal():
# 		if not wall_in_front():
# 			move()
# 		if right_is_clear():
# 			turn_right()
# 	if wall_in_front():
# 		if right_is_clear():
# 			turn_right()
# 		elif wall_on_right():
# 			turn_left()
# 	elif not at_goal():
# 		move()

# -------------------------------


# def turn_right():
# 	turn_left()
# 	turn_left()
# 	turn_left()


# while not at_goal():
# 	if right_is_clear():
# 		turn_right()
# 		move()
# 	elif front_is_clear():
# 		move()
# 	else:
# 		turn_left()