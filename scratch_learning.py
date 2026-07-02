def print_users(*names):
    for i, name in enumerate(names, start=1):
        print(f"{i}. {name}")