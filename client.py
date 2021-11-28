import socket
import os
import sys
import time
from watchdog.observers import polling
from watchdog.events import PatternMatchingEventHandler

CHUNKSIZE = 1_000_000

server_ip = sys.argv[1]
server_port = int(sys.argv[2])
path = sys.argv[3]
time_step = int(sys.argv[4])
client_id = ''
client_comp = "-1"

# If the client has no id - then he will send 'False' to the server - which means he is a new client.
if len(sys.argv) < 6:
    client_id = 'False'
else:
    client_id = sys.argv[5]


def notify_created(is_dir, new_path, sock):
    mode = "created"
    curr_update = mode + ',' + str(is_dir) + ',' + new_path
    print(curr_update)
    with sock:
        sock.sendall(curr_update.encode() + b'\n')

        if not is_dir:
            new_path = os.path.join(path, new_path)
            send_file(sock, new_path)


def notify_deleted(old_path, sock):
    print("deleted")
    mode = "deleted"
    curr_update = mode + ',' + old_path
    # server_socket.sendall(client_id.encode('utf-8'))
    # server_socket.sendall(curr_update.encode() + b'\n')
    # send "deleted"
    # send old_path
    pass


def notify_moved(src_path, dest_path, sock):
    print("moved")
    # send "moved"
    # send src_path
    # send old_path
    pass


def notify_modified(is_dir, modified_path, sock):
    # print("modified")
    # send "modified"
    # send if is dir
    # if so - send name (path)
    # if not - send open and send file
    pass


def notify_server(event, event_type, src_path, sock):

    if event_type == "created":
        notify_created(event.is_directory, src_path, sock)

    if event_type == "deleted":
        notify_deleted(src_path, sock)

    if event_type == "moved":
        dest_path = event.dest_path.split(main_dir, 1)[1]
        notify_moved(src_path, dest_path, sock)

    if event_type == "modified":
        notify_modified(event.is_directory, src_path, sock)


def on_any_event(event):
    if (event.event_type == "modified"):
        return
    update_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    update_socket.connect((server_ip, server_port))
    update_socket.sendall(client_id.encode() + b'\n')  # send client id
    update_socket.sendall(client_comp.encode() + b'\n')  # send client id
    src_path = event.src_path.split(main_dir, 1)[1]  # the only relative path in the server
    notify_server(event, event.event_type, src_path, update_socket)
    server_socket.close()


def send_file(on_sock, src_path):
    with on_sock:
        filename = src_path
        relpath = os.path.basename(filename)  # get file name from my_dir (file path)
        filesize = os.path.getsize(filename)

        print(f'Sending {relpath}')

        with open(filename, 'rb') as f:
            on_sock.sendall(relpath.encode() + b'\n')  # send file name + subdirectory and '\n'.
            on_sock.sendall(str(filesize).encode() + b'\n')  # send file size.

            # Send the file in chunks so large files can be handled.
            while True:
                data = f.read(CHUNKSIZE)
                if not data:
                    break
                on_sock.sendall(data)

print('Done.')


def send_files(on_sock, src_path):  # type - socket
    with on_sock:
        for root, dirs, files in os.walk(src_path):
            for file in files:
                filename = os.path.join(root, file)
                relpath = os.path.relpath(filename, src_path)  # get file name from my_dir (file path)
                filesize = os.path.getsize(filename)

                print(f'Sending {relpath}')

                with open(filename, 'rb') as f:
                    on_sock.sendall(relpath.encode() + b'\n')  # send file name + subdirectory and '\n'.
                    on_sock.sendall(str(filesize).encode() + b'\n')  # send file size.

                    # Send the file in chunks so large files can be handled.
                    while True:
                        data = f.read(CHUNKSIZE)
                        if not data:
                            break
                        on_sock.sendall(data)
        print('Done.')


def get_my_files(client_file):  # type - makefile('rb')
    while True:
        line = client_file.readline()
        if line.strip().decode() == "finito":
            break  # no more files, client closed connection.

        filename = line.strip().decode()
        length = int(client_file.readline())
        print(f'Downloading {filename}...\n  Expecting {length:,} bytes...', end='', flush=True)

        file_path = os.path.join(path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Read the data in chunks so it can handle large files.
        with open(file_path, 'wb') as f:
            while length:
                chunk = min(length, CHUNKSIZE)
                data = client_file.read(chunk)
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
    client_file.close()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server_ip, server_port))
    get_data_sock = server_socket.makefile(mode='rb')

    server_socket.sendall(client_id.encode() + b'\n')  # send client id
    server_socket.sendall(client_comp.encode() + b'\n')  # send client id

    if client_id == 'False':
        client_id = get_data_sock.readline().strip().decode('utf-8')  # get new ID
        print(f"My new ID is... topim topim..{client_id}")
        client_comp = get_data_sock.readline().strip().decode('utf-8')  # get new comp ("1")
        print(f"My computer number {client_comp}")
        get_data_sock.close()
        send_files(server_socket, path)  # will send files and close socket.

    else:
        client_comp = get_data_sock.readline().strip().decode('utf-8')  # get new comp
        print(f"My computer number {client_comp}")
        get_my_files(get_data_sock)  # pull the directory from server, will close makefile object.
        server_socket.close()

    # from now on the client app is running, but the client will connects to the server only to transfer data.

    patterns = ["*"]  # contains the file patterns we want to handle (in my scenario, I will handle all the files)
    ignore_patterns = None  # contains the patterns that we don’t want to handle.
    ignore_directories = False  # a boolean that we set to True if we want to be notified just for regu
    # lar files.
    case_sensitive = False  # boolean that if set to “True”, made the patterns we introduced “case sensitive”.

    # Create event handler:
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    # specify to the handler that we want this function to be called when an event is raised:
    my_event_handler.on_any_event = on_any_event

    # create an Observer:
    # "path" is monitored, on server every file from this name an on is modified.
    main_dir = os.path.split(path)[-1] + os.sep
    go_recursively = True  # a boolean that allow me to catch all the event that occurs even in sub directories.
    my_observer = polling.PollingObserver()  # better Observer
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    # start the Observer:
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()