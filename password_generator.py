import itertools
import string
import os
import threading
import queue
import signal
from tqdm import tqdm

def generate_passwords(min_length, max_length, file_path, characters):
    def worker(password_queue, file_lock, progress_bar, file):
        while True:
            password = password_queue.get()
            if password is None:
                break
            with file_lock:
                file.write(password + '\n')
            progress_bar.update(1)
            password_queue.task_done()

    try:
        with open(file_path, 'w') as file:
            file_lock = threading.Lock()
            total_combinations = sum(len(characters) ** length for length in range(min_length, max_length + 1))
            password_queue = queue.Queue(maxsize=100000)
            thread_count = min(os.cpu_count() or 4, 10)  # Use available cores, max 10
            threads = []

            with tqdm(total=total_combinations, desc="Generating passwords", unit="pass") as progress_bar:
                for _ in range(thread_count):
                    t = threading.Thread(target=worker, args=(password_queue, file_lock, progress_bar, file))
                    t.daemon = True
                    t.start()
                    threads.append(t)

                try:
                    for length in range(min_length, max_length + 1):
                        for combination in itertools.product(characters, repeat=length):
                            password = ''.join(combination)
                            password_queue.put(password)
                except KeyboardInterrupt:
                    print("\nInterrupted by user. Stopping...")
                finally:
                    for _ in threads:
                        password_queue.put(None)

                    password_queue.join()

                    for t in threads:
                        t.join()

            print("\nPasswords have been generated and saved to:", file_path)
    
    except IOError:
        print("Error: Cannot write to file at the specified path.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def get_integer_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Input must be between {min_val} and {max_val}. Try again.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_characters():
    default_characters = string.ascii_letters + string.digits + '@#%&*$'
    use_default = input("Use default character set? (Y/N): ").strip().lower() == 'y'
    if use_default:
        return default_characters
    else:
        custom_set = input("Enter custom character set: ").strip()
        if not custom_set:
            print("Error: Custom character set cannot be empty.")
            return get_characters()
        return custom_set

def signal_handler(signal_received, frame):
    print("\nTermination signal received. Exiting gracefully...")
    os._exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    min_length = get_integer_input("Enter minimum password length: ", 1, 1000)
    max_length = get_integer_input("Enter maximum password length: ", min_length, 1000)
    
    file_path = input("Enter the file path to save passwords (e.g., /home/bhanu/Desktop/password.txt): ").strip()
    if not file_path:
        print("Error: File path cannot be empty.")
    else:
        characters = get_characters()
        print(f"\nGenerating passwords ({min_length}-{max_length} characters)...")
        
        generate_passwords(min_length, max_length, file_path, characters)
