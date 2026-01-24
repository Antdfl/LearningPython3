class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.followers = 0
        self.following = 0
    def follow(self, user):
        user.followers += 1
        self.following += 1

user_1 = User("001","Antonio")
user_2 = User("002","Angela")

user_1.follow(user_2)
print(f" user1 followers {user_1.followers}, following {user_1.following}")
print(f" user2 followers {user_2.followers}, following {user_2.following}")

