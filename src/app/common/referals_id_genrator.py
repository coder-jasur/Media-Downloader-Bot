import random
import string
import time


def generate_ref_id(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(random.choice(characters) for _ in range(length)) + str(time.time_ns())[:5]