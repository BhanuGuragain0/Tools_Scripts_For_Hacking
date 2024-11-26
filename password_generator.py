# File: password_generator.py

import itertools
import string
import os
import threading
import queue
import signal
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

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

            with tqdm(total=total_combinations, desc=f"{Fore.GREEN}Generating passwords", unit="pass") as progress_bar:
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
                    print(f"\n{Fore.RED}Interrupted by user. Stopping...")
                finally:
                    for _ in threads:
                        password_queue.put(None)

                    password_queue.join()

                    for t in threads:
                        t.join()

            print(f"\n{Fore.BLUE}Passwords have been generated and saved to: {file_path}")
    
    except IOError:
        print(f"{Fore.RED}Error: Cannot write to file at the specified path.")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}")

def get_integer_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}"))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"{Fore.YELLOW}Input must be between {min_val} and {max_val}. Try again.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter an integer.")

def get_characters():
    default_characters = string.ascii_letters + string.digits + '@#%&*$'
    use_default = input(f"{Fore.CYAN}Use default character set? (Y/N): {Style.RESET_ALL}").strip().lower() == 'y'
    if use_default:
        return default_characters
    else:
        custom_set = input(f"{Fore.CYAN}Enter custom character set: {Style.RESET_ALL}").strip()
        if not custom_set:
            print(f"{Fore.RED}Error: Custom character set cannot be empty.")
            return get_characters()
        return custom_set

def signal_handler(signal_received, frame):
    print(f"\n{Fore.RED}Termination signal received. Exiting gracefully...")
    os._exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print(f"{Fore.MAGENTA}Welcome to the Password Generator!{Style.RESET_ALL}")
    min_length = get_integer_input("Enter minimum password length: ", 1, 1000)
    max_length = get_integer_input("Enter maximum password length: ", min_length, 1000)
    
    file_path = input(f"{Fore.CYAN}Enter the file path to save passwords (e.g., /home/user/passwords.txt): {Style.RESET_ALL}").strip()
    if not file_path:
        print(f"{Fore.RED}Error: File path cannot be empty.")
    else:
        characters = get_characters()
        print(f"\n{Fore.GREEN}Generating passwords ({min_length}-{max_length} characters)...{Style.RESET_ALL}")
        generate_passwords(min_length, max_length, file_path, characters)
