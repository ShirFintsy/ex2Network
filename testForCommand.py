import os

# path = "/home/bob/Pictures"
# src_path = "/home/bob/Pictures/bluh/Screenshot from 2021-11-18 05-12-27.png"
# src_path = os.path.relpath(src_path, path)
# print(src_path)

file_path = "/home/bob/Pictures/.asaf.txt.swp"

dir_name = os.path.dirname(file_path)
swp_name = os.path.basename(file_path)
file_name = swp_name[1:-4]
print(file_name)
