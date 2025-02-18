#!/usr/bin/env python3
import argparse
import itertools
import string
import os
import multiprocessing
import signal
import sys
import logging
from tqdm import tqdm
from colorama import Fore, Style, init
from typing import Optional

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DEFAULT_CHARACTERS = string.ascii_letters + string.digits + '@#%&*$'
MAX_PASSWORD_LENGTH = 1000
MIN_PASSWORD_LENGTH = 1
DEFAULT_CHUNK_SIZE = 10000
DEFAULT_WORKERS = multiprocessing.cpu_count() or 4
MAX_WORKERS = 10

def index_to_password(index: int, length: int, characters: str) -> str:
    """
    Convert an integer index into a password string by treating the index as a number in base=len(characters).
    """
    base = len(characters)
    pwd = []
    for _ in range(length):
        pwd.append(characters[index % base])
        index //= base
    return ''.join(reversed(pwd))

def generate_chunk(task, output_queue: multiprocessing.Queue) -> None:
    """
    Generate passwords for the given task and put them in the output queue.
    
    Args:
        task (tuple): A tuple (length, start, end, characters).
        output_queue (multiprocessing.Queue): Queue to send generated passwords.
    """
    length, start, end, characters = task
    try:
        for i in range(start, end):
            pwd = index_to_password(i, length, characters)
            output_queue.put(pwd)
    except Exception as e:
        logging.error(f"Error generating chunk for length {length} from {start} to {end}: {e}")

def writer_process(file_path: str, output_queue: multiprocessing.Queue, counter: multiprocessing.Value) -> None:
    """
    Write passwords from the output queue to the output file. Increment the shared counter after each write.
    
    Args:
        file_path (str): Path of the output file.
        output_queue (multiprocessing.Queue): Queue from which to read generated passwords.
        counter (multiprocessing.Value): Shared counter for progress tracking.
    """
    try:
        with open(file_path, 'w') as f:
            while True:
                pwd = output_queue.get()
                if pwd is None:
                    break
                f.write(pwd + '\n')
                with counter.get_lock():
                    counter.value += 1
    except Exception as e:
        logging.error(f"Error in writer process: {e}")
        sys.exit(1)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Advanced Password Generator")
    parser.add_argument("--min-length", type=int, default=None, help="Minimum password length")
    parser.add_argument("--max-length", type=int, default=None, help="Maximum password length")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--characters", type=str, default=DEFAULT_CHARACTERS, help="Character set to use")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Chunk size for generation")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of worker processes")
    return parser.parse_args()

def get_interactive_input() -> tuple:
    """
    Prompt the user interactively for required inputs.
    """
    try:
        min_length = int(input(f"{Fore.CYAN}Enter minimum password length: {Style.RESET_ALL}"))
        max_length = int(input(f"{Fore.CYAN}Enter maximum password length: {Style.RESET_ALL}"))
        if min_length < MIN_PASSWORD_LENGTH or max_length > MAX_PASSWORD_LENGTH or min_length > max_length:
            print(f"{Fore.RED}Invalid length range provided. Exiting.")
            sys.exit(1)
        output = input(f"{Fore.CYAN}Enter output file path: {Style.RESET_ALL}").strip()
        if not output:
            print(f"{Fore.RED}Output file path cannot be empty. Exiting.")
            sys.exit(1)
        use_default = input(f"{Fore.CYAN}Use default character set? (Y/N): {Style.RESET_ALL}").strip().lower() == 'y'
        if use_default:
            characters = DEFAULT_CHARACTERS
        else:
            characters = input(f"{Fore.CYAN}Enter custom character set: {Style.RESET_ALL}").strip()
            if not characters:
                print(f"{Fore.RED}Custom character set cannot be empty. Exiting.")
                sys.exit(1)
        return min_length, max_length, output, characters
    except Exception as e:
        logging.error(f"Error in interactive input: {e}")
        sys.exit(1)

def main() -> None:
    # Parse command-line arguments; if essential args are missing, fall back to interactive mode.
    args = parse_arguments()
    if args.min_length is None or args.max_length is None or args.output is None:
        min_length, max_length, output, characters = get_interactive_input()
    else:
        min_length = args.min_length
        max_length = args.max_length
        output = args.output
        characters = args.characters

    # Validate length range
    if min_length < MIN_PASSWORD_LENGTH or max_length > MAX_PASSWORD_LENGTH or min_length > max_length:
        logging.error("Invalid password length range.")
        sys.exit(1)

    # Validate output directory exists
    output_dir = os.path.dirname(os.path.abspath(output))
    if not os.path.isdir(output_dir):
        logging.error(f"Directory does not exist: {output_dir}")
        sys.exit(1)

    # Ensure number of workers is within bounds
    workers = min(args.workers, MAX_WORKERS)

    total_passwords = 0
    tasks = []
    # Partition the search space for each password length into tasks (chunks)
    for length in range(min_length, max_length + 1):
        combinations = len(characters) ** length
        total_passwords += combinations
        for start in range(0, combinations, args.chunk_size):
            end = min(start + args.chunk_size, combinations)
            tasks.append((length, start, end, characters))

    logging.info(f"Total passwords to generate: {total_passwords:,}")
    logging.info(f"Total tasks created: {len(tasks)}")
    logging.info(f"Using {workers} worker process(es) with chunk size {args.chunk_size}")

    # Setup multiprocessing structures
    output_queue = multiprocessing.Queue(maxsize=workers * 2)
    counter = multiprocessing.Value('i', 0)

    # Start the writer process that will write to the output file
    writer = multiprocessing.Process(target=writer_process, args=(output, output_queue, counter))
    writer.start()

    # Setup signal handling for graceful termination
    def signal_handler(signum, frame):
        logging.info("Termination signal received. Exiting gracefully...")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create a pool of worker processes to generate password chunks
    pool = multiprocessing.Pool(workers)
    for task in tasks:
        pool.apply_async(generate_chunk, args=(task, output_queue))
    pool.close()

    # Monitor progress using tqdm in the main process
    with tqdm(total=total_passwords, desc=f"{Fore.GREEN}Generating passwords", unit="pass") as pbar:
        last_count = 0
        while True:
            with counter.get_lock():
                current = counter.value
            pbar.update(current - last_count)
            last_count = current
            if current >= total_passwords:
                break

    pool.join()
    # Signal the writer process to finish
    output_queue.put(None)
    writer.join()

    logging.info(f"{Fore.BLUE}Passwords have been generated and saved to: {output}{Style.RESET_ALL}")
    logging.info(f"{Fore.BLUE}Total passwords generated: {total_passwords:,}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
