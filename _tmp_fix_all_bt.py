path = r'C:\Users\93724\Desktop\Alpha monitor\INDEX.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old1 = '| strategy/lof_iopv/calc.py |'
new1 = '| strategy/lof_iopv/calc.py |'
old2 = '| strategy/lof_iopv/service.py |'
new2 = '| strategy/lof_iopv/service.py |'

while old1 in content:
    content = content.replace(old1, new1, 1)
while old2 in content:
    content = content.replace(old2, new2, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')