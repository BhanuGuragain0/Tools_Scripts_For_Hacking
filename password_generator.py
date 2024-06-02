import itertools
import string
import os
import threading
import queue

def generate_passwords(min_length, max_length, file_path, characters):
    def worker(password_queue, file_lock, file):
        while True:
            password = password_queue.get()
            if password is None:
                break
            with file_lock:
                file.write(password + '\n')
            password_queue.task_done()

    try:
        with open(file_path, 'w') as file:
            file_lock = threading.Lock()
            total_combinations = sum(len(characters) ** length for length in range(min_length, max_length + 1))
            chunk_size = min(total_combinations // 100, 1000000)
            password_queue = queue.Queue(maxsize=chunk_size)
            thread_count = 4  # Number of threads to use
            threads = []

            for _ in range(thread_count):
                t = threading.Thread(target=worker, args=(password_queue, file_lock, file))
                t.start()
                threads.append(t)

            try:
                for length in range(min_length, max_length + 1):
                    all_combinations = itertools.product(characters, repeat=length)
                    for i, combination in enumerate(all_combinations, 1):
                        password = ''.join(combination)
                        password_queue.put(password)
                        if i % chunk_size == 0 or (i == total_combinations and total_combinations <= chunk_size):
                            print(f"Progress: {i}/{total_combinations} ({(i / total_combinations) * 100:.2f}%)", end='\r')
            except KeyboardInterrupt:
                print("\nInterrupted by user. Stopping...")

            password_queue.join()

            for _ in range(thread_count):
                password_queue.put(None)

            for t in threads:
                t.join()

            print("\nPasswords have been generated and saved to:", file_path)
    
    except IOError:
        print("Error: Cannot write to file at the specified path.")

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
    return default_characters if use_default else input("Enter custom character set: ").strip()

if __name__ == "__main__":
    min_length = get_integer_input("Enter minimum password length: ", 1, 1000)
    max_length = get_integer_input("Enter maximum password length: ", min_length, 1000)
    
    file_path = input("Enter the file path to save passwords (e.g., /home/bhanu/Desktop/password.txt): ").strip()
    if not file_path:
        print("Error: File path cannot be empty.")
    else:
        characters = get_characters()
        print(f"\nGenerating passwords ({min_length}-{max_length} characters)...")
        
        generate_passwords(min_length, max_length, file_path, characters)
