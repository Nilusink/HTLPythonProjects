import random as r

FILENAME = "lorem.txt"
SECRET = "Wuffi"
SPOTS = 5

data: str = ""
with open(FILENAME, "r") as f:
    data = f.read()

size = len(data)

for i in range(SPOTS):
    pos = r.randint(0, size)
    print(f"Inserting at: {pos}")
    data = data[:pos] + SECRET + data[pos:]
    print(f"Done inserting")

with open(FILENAME, "w") as f:
    f.write(data)
