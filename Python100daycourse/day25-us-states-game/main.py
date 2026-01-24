import turtle
import pandas
# import os 
# cwd = os.getcwd() 
# print("Current Working Directory:", cwd)

screen = turtle.Screen()
screen.title("US State Game")
image = ".\\day25-us-states-game\\blank_states_img.gif"
screen.addshape(image)
turtle.shape(image)
#def get_mouse_click_coor(x,y):
#    print(x,y)
#turtle.onscreenclick(get_mouse_click_coor)
data = pandas.read_csv(".\\day25-us-states-game\\50_states.csv")
guessed_states= []
num_guesses = 0
all_states = data.state.to_list()

while len(guessed_states) < 50:
    raw_answer = screen.textinput(title=f"{num_guesses} out of 50 states", prompt="What's another state's name?")
    if raw_answer is None:
        break
    answer_state = raw_answer.title()
    #print(answer_state)
    if answer_state == "Exit":
        # states_to_learn = []
        # for state in all_states:
        #     if state not in guessed_states:
        #         states_to_learn.append(state)
        states_to_learn = [state for state in all_states if state not in guessed_states]
        new_data = pandas.DataFrame(states_to_learn, columns=["State"])  # type: ignore
        new_data.to_csv(".\\day25-us-states-game\\States_to_learn.csv")
        break
    if answer_state in all_states:
        state_data = data[data.state == answer_state]
        x_position = state_data.x.item()
        y_position = state_data.y.item()
        #print(f"state: {state}, x: {x_position}, y: {y_position}")
        # Draw the name of the state at a certain positiion
        t = turtle.Turtle()
        t.hideturtle()
        t.penup()
        t.goto(x_position, y_position)
        t.pendown()
        t.write(answer_state, font=("Arial", 10, "bold"))
        # Increase the number of guesses and append our state to a list
        num_guesses += 1
        guessed_states.append(answer_state)



#turtle.mainloop()
