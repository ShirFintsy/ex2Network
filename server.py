from socket import *
import os
import sys
import random
import string

CHUNKSIZE = 1_000_000
port = int(sys.argv[1])

clients_id_path = {}  # create dictionary that maps id to path in the server.
data_base = {}

# open server
main_socket = socket()
main_socket.bind(('', port))
main_socket.listen(5)


# return random string with 128 characters compared of letters and numbers.
def get_random_id(id_set):
    new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    while new_id in id_set:
        new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    return new_id


def init_client_files(get_files_sock):
        while True:
            line = get_files_sock.readline()
            if not line:
                break  # no more files, client closed connection.

            filename = line.strip().decode()
            length = int(get_files_sock.readline())
            print(f'Downloading {filename}...\n  Expecting {length:,} bytes...', end='', flush=True)

            file_path = os.path.join('AllClients', str(client_id))
            file_path = os.path.join(file_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Read the data in chunks so it can handle large files.
            with open(file_path, 'wb') as f:
                while length:
                    chunk = min(length, CHUNKSIZE)
                    data = get_files_sock.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    length -= len(data)
                else:  # only runs if while doesn't break and length==0
                    print('Complete')
                    continue

            # socket was closed early.
            print('Incomplete')
            break


def send_files(on_socket, src_dir):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            filename = os.path.join(root, file)
            relative_path = os.path.relpath(filename, src_dir)
            file_size = os.path.getsize(filename)

            print(f'Sending {relative_path}')

            with open(filename, 'rb') as f:
                on_socket.sendall(relative_path.encode() + b'\n')  # send file name + subdirectory and '\n'.
                on_socket.sendall(str(file_size).encode() + b'\n')  # send file size.

                # Send the file in chunks so large files can be handled.
                while True:
                    data = f.read(CHUNKSIZE)
                    if not data:
                        break
                    on_socket.sendall(data)
    on_socket.sendall("finito".encode('utf-8') + b'\n')
    print('Done.')


def get_comp_num(c_id, c_comp):
    if data_base.keys().__contains__(c_id):  # check if the ID exists
        if c_comp == "-1":  # check if the computer not exists
            c_comp = str(len(data_base[c_id]) + 1)
            data_base[c_id][c_comp] = None  # new computer has joined the data base.
        else:
            return c_comp  # else we don't change the client_comp
    else:
        c_id = get_random_id(clients_id_path.keys())  # create client id
        c_comp = "1"
        data_base[c_id] = {}
        data_base[c_id][c_comp] = None
    return c_comp, c_id


if __name__ == "__main__":

    # make folder to store all clients data
    server_dir = os.getcwd()
    allClients = os.path.join(server_dir, 'AllClients')
    os.mkdir(allClients)

    while True:
        print('Waiting for a client...')
        client_socket, address = main_socket.accept()
        get_data_sock = client_socket.makefile(mode='rb')

        print(f'Client joined from {address}')
        # identification - get client's ID, comp number
        client_id = get_data_sock.readline().strip().decode()
        client_comp = get_data_sock.readline().strip().decode()
        client_comp, real_id = get_comp_num(client_id, client_comp)  # also update the database

        client_dir_path = ''
        if client_id == 'False':
            client_id = real_id
            client_socket.sendall(client_id.encode('utf-8') + b'\n')
            client_socket.sendall(client_comp.encode('utf-8') + b'\n')   # notify the client that he is the first computer of this ID.

            # create & enter his folder name to the dictionary
            os.mkdir(os.path.join(allClients, client_id))
            clients_id_path[client_id] = os.path.join(allClients, client_id)

            # get files to server.
            init_client_files(get_data_sock)

        # ID exists:
        else:
            client_dir_path = clients_id_path[client_id]  # search for path in AllClients folders

            # check if the computer is already on the system - we just added him hence the condition.
            if str(len(data_base[client_id])) != client_comp:
                # already signed computer- check if there are updates:
                if data_base[client_id][client_comp]:  # check if there are some updates
                    updates = data_base[client_id][client_comp]  # list of updates
                    cmd = get_data_sock.readline().strip().decode()
                    # TODO: share the updates to this computer
                # waiting for updates
            else:
                client_socket.sendall(client_comp.encode('utf-8') + b'\n')
                send_files(client_socket, client_dir_path)

            # if it is not a new client, and not a new computer than the client needs something. (push or pull)
