blocks = int(input("Enter the number of blocks: "))
height = 0
current_blocks = 0
index = 1
while current_blocks != blocks:
    current_blocks += index
    # print("current_blocks: ",current_blocks)
    if current_blocks > blocks:
        break
    height += 1
    index += 1
    # if index > 100:
    #     print("Something seems hirewiring --> infinite loop. Exit")
    #     break
print("The height of the pyramid:", height)
