import itertools
import string
import os
import multiprocessing
import queue
import signal
from tqdm import tqdm
from colorama import Fore, Style, init
from typing import List, Optional

# Initialize colorama
init(autoreset=True)

# Constants
DEFAULT_CHARACTERS = string.ascii_letters + string.digits + '@#%&*$'
MAX_PASSWORD_LENGTH = 1000
MIN_PASSWORD_LENGTH = 1
MAX_THREADS = 10

def generate_passwords(min_length: int, max_length: int, file_path: str, characters: str) -> None:
    """
    Generate all possible password combinations within the specified length range and save them to a file.

    Args:
        min_length (int): Minimum password length.
        max_length (int): Maximum password length.
        file_path (str): Path to the output file.
        characters (str): Character set to use for password generation.
    """
    def worker(password_queue: queue.Queue, file_lock: multiprocessing.Lock, progress_bar: tqdm, file) -> None:
        """Worker function to write passwords to the file."""
        while True:
            password = password_queue.get()
            if password is None:  # Sentinel value to stop the worker
                break
            with file_lock:
                file.write(password + '\n')
            progress_bar.update(1)
            password_queue.task_done()

    try:
        # Validate file path
        if not os.path.exists(os.path.dirname(file_path)):
            raise FileNotFoundError(f"Directory does not exist: {os.path.dirname(file_path)}")

        with open(file_path, 'w') as file:
            file_lock = multiprocessing.Lock()
            total_combinations = sum(len(characters) ** length for length in range(min_length, max_length + 1))
            password_queue = multiprocessing.Queue(maxsize=100000)
            thread_count = min(os.cpu_count() or 4, MAX_THREADS)  # Use available cores, max 10
            processes = []

            with tqdm(total=total_combinations, desc=f"{Fore.GREEN}Generating passwords", unit="pass") as progress_bar:
                for _ in range(thread_count):
                    p = multiprocessing.Process(target=worker, args=(password_queue, file_lock, progress_bar, file))
                    p.daemon = True
                    p.start()
                    processes.append(p)

                try:
                    for length in range(min_length, max_length + 1):
                        for combination in itertools.product(characters, repeat=length):
                            password = ''.join(combination)
                            password_queue.put(password)
                except KeyboardInterrupt:
                    print(f"\n{Fore.RED}Interrupted by user. Stopping...")
                finally:
                    # Signal workers to stop
                    for _ in processes:
                        password_queue.put(None)

                    # Wait for all workers to finish
                    password_queue.join()

                    for p in processes:
                        p.join()

            print(f"\n{Fore.BLUE}Passwords have been generated and saved to: {file_path}")
            print(f"{Fore.BLUE}Total passwords generated: {total_combinations:,}")
    
    except FileNotFoundError as e:
        print(f"{Fore.RED}Error: {e}")
    except IOError:
        print(f"{Fore.RED}Error: Cannot write to file at the specified path.")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}")

def get_integer_input(prompt: str, min_val: int, max_val: int) -> int:
    """
    Get an integer input from the user within a specified range.

    Args:
        prompt (str): Prompt to display to the user.
        min_val (int): Minimum allowed value.
        max_val (int): Maximum allowed value.

    Returns:
        int: Validated integer input.
    """
    while True:
        try:
            value = int(input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}"))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"{Fore.YELLOW}Input must be between {min_val} and {max_val}. Try again.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter an integer.")

def get_characters() -> str:
    """
    Get the character set to use for password generation.

    Returns:
        str: Character set.
    """
    use_default = input(f"{Fore.CYAN}Use default character set? (Y/N): {Style.RESET_ALL}").strip().lower() == 'y'
    if use_default:
        return DEFAULT_CHARACTERS
    else:
        custom_set = input(f"{Fore.CYAN}Enter custom character set: {Style.RESET_ALL}").strip()
        if not custom_set:
            print(f"{Fore.RED}Error: Custom character set cannot be empty.")
            return get_characters()
        return custom_set

def signal_handler(signal_received: int, frame: Optional[object]) -> None:
    """
    Handle termination signals (e.g., Ctrl+C).

    Args:
        signal_received (int): Signal number.
        frame (Optional[object]): Current stack frame.
    """
    print(f"\n{Fore.RED}Termination signal received. Exiting gracefully...")
    os._exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print(f"{Fore.MAGENTA}Welcome to the Password Generator!{Style.RESET_ALL}")
    min_length = get_integer_input("Enter minimum password length: ", MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)
    max_length = get_integer_input("Enter maximum password length: ", min_length, MAX_PASSWORD_LENGTH)
    
    file_path = input(f"{Fore.CYAN}Enter the file path to save passwords (e.g., /home/user/passwords.txt): {Style.RESET_ALL}").strip()
    if not file_path:
        print(f"{Fore.RED}Error: File path cannot be empty.")
    else:
        characters = get_characters()
        print(f"\n{Fore.GREEN}Generating passwords ({min_length}-{max_length} characters)...{Style.RESET_ALL}")
        generate_passwords(min_length, max_length, file_path, characters)
