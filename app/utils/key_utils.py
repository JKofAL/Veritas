import random, string

def generate_uniq_keys(n_k: int):
    LENGTH_OF_KEY = 10
    keys = []
    for _ in range(n_k):
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=LENGTH_OF_KEY))
        keys.append(key)
    return keys