import os

USERS = [
    {
        "username": "Amirali",
        "password": "1234",
        "is_privilaged": True
    },
    {
        "username": "Asal",
        "password": "5678",
        "is_privilaged": False
    },
    {
        "username": "Arshia",
        "password": "1010",
        "is_privilaged": True
    }
]

PRIVATE_PATHS = [
    os.path.abspath("./data/confidential"),
    os.path.abspath("./data/private.txt")
]
