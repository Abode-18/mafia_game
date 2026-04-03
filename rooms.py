import random
import string
def generate_code(len=5):
    return ''.join(random.choices(string.ascii_uppercase, k=len))

def creat_room(host_name):
    pass
