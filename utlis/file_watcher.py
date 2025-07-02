import os, time

def watch_folder(folder):
    seen = set(os.listdir(folder))  # Initialize with existing files
    while True:
        current = set(os.listdir(folder))
        new_files = current - seen
        for f in new_files:
            if f.endswith((".png", ".jpg", ".jpeg")):
                yield os.path.join(folder, f)
        seen = current
        time.sleep(2)

