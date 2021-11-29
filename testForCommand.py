import os

# path = '/home/shir25/Pictures'
# for root, dirs, files in os.walk(path):
#     for dir in dirs:
#         print(root + os.sep + dir)
#     for file in files:
#         print(root + os.sep + file)

        #print(p)
d = "/home/shir25/Pictures/.asaf.txt.swp"
path = "/home/shir25/Pictures"
relpath = os.path.relpath(d, path)
d = os.path.join(os.path.dirname((os.path.splitext(d)[0])), (os.path.splitext(d)[0].split(os.sep)[-1])[1:])
print(d)
