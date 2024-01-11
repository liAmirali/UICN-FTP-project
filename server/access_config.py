import os

USERS = [
    {
        "username": "admin",
        "password": "admin",
        "is_privileged": True
    },
    {
        "username": "Amirali",
        "password": "1234",
        "is_privileged": True
    },
    {
        "username": "Asal",
        "password": "5678",
        "is_privileged": False
    },
    {
        "username": "Arshia",
        "password": "1010",
        "is_privileged": True
    }
]

PRIVATE_PATHS = [
    os.path.abspath("./data/confidential"),
    os.path.abspath("./data/private.txt")
]
