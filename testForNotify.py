import socket
import os
import sys
import time
from watchdog.observers import polling
from watchdog.events import PatternMatchingEventHandler
path = "/home/bob/temp"


def notify_created(is_dir, new_path):
    mode = "created"
    curr_update = mode + ',' + str(is_dir) + ',' + new_path
    print(curr_update)


def notify_deleted(old_path):
    mode = "deleted"
    curr_update = mode + ',' + old_path
    print(curr_update)


def notify_moved(src_path, dest_path):
    mode = "moved"
    curr_update = mode + ',' + src_path + ',' + dest_path
    print(curr_update)


def notify_modified(is_dir, modified_path):
    mode = "modified"
    curr_update = mode + ',' + modified_path
    print(curr_update)
    print("modified")


def notify_server(event, event_type, src_path):

    if event_type == "created":
        notify_created(event.is_directory, src_path)

    if event_type == "deleted":
        notify_deleted(src_path)

    if event_type == "moved":
        dest_path = event.dest_path.split(main_dir, 1)[1]
        notify_moved(src_path, dest_path)

    if event_type == "modified":
        notify_modified(event.is_directory, src_path)


def on_any_event(event):
    # print(f"even src path : {event.src_path}")
    # src_path = event.src_path.split(main_dir, 1)[1]  # the only relative path in the server
    # print(f"src: {src_path}")
    notify_server(event, event.event_type, event.src_path)


if __name__ == "__main__":

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
    print("main dir: " + main_dir)
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



# # path_to_del = "/home/bob/temp (copy)"
# # for root, dirs, files in os.walk(path_to_del, topdown=False):
# #     for file in files:
# #         file_path = os.path.join(root, file)
# #         os.remove(file_path)
# #     for dir in dirs:
# #         dir_path = os.path.join(root, dir)
# #         os.rmdir(dir_path)
# # os.rmdir(path_to_del)