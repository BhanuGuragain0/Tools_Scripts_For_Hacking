
```markdown
# Advanced Password Generator For Rainbow Attack

Advanced Password Generator is a Python‑based tool that efficiently generates all possible password combinations within a specified length range. Utilizing multiprocessing with a chunk‑based task partitioning approach, real‑time progress tracking via tqdm, robust logging, and graceful signal handling, this tool is designed for high‑performance, real‑world usage.

## Features

- **Complete Password Generation:**  
  Generate every possible combination for a specified range of password lengths.

- **Customizable Character Set:**  
  Use the default character set (letters, digits, and special characters) or supply your own.

- **Multiprocessing & Task Partitioning:**  
  The search space is divided into manageable chunks and processed concurrently using multiple worker processes.

- **Real-Time Progress Tracking:**  
  A live tqdm progress bar displays the generation progress in real time.

- **Graceful Termination:**  
  Signal handling (e.g., Ctrl+C) allows for a safe and immediate shutdown.

- **Command-Line & Interactive Modes:**  
  Easily use the tool via command-line arguments or through an interactive prompt.

- **Detailed Logging:**  
  Logging provides insight into processing details, errors, and overall progress.

## Prerequisites

- **Python 3.x**

- **Required Python Packages:**
  - `tqdm`
  - `colorama`

Install these packages via pip:

```bash
pip install tqdm colorama
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/advanced-password-generator.git
   cd advanced-password-generator
   ```

2. **(Optional) Set Up a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *(If you do not have a requirements.txt, manually install `tqdm` and `colorama` as shown above.)*

## Usage

You can run Advanced Password Generator either by providing command-line arguments or interactively.

### Command-Line Mode

```bash
python advanced_password_generator.py --min-length 1 --max-length 3 --output ./passwords.txt --characters "abc123" --chunk-size 10000 --workers 4
```

- `--min-length`: Minimum password length.
- `--max-length`: Maximum password length.
- `--output`: File path to save the generated passwords.
- `--characters`: Character set to use (default: `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#%&*$`).
- `--chunk-size`: Number of passwords to generate per task chunk (default: 10000).
- `--workers`: Number of worker processes (default: number of CPU cores, maximum 10).

### Interactive Mode

If essential arguments are omitted, the script will prompt you for input interactively:

```bash
python advanced_password_generator.py
```

Follow the prompts to specify the minimum and maximum password lengths, output file path, and whether to use the default or a custom character set.

## Example Output

```
2025-02-18 12:00:00,123 - INFO - Total passwords to generate: 238,328
2025-02-18 12:00:00,124 - INFO - Total tasks created: 24
2025-02-18 12:00:00,125 - INFO - Using 4 worker process(es) with chunk size 10000
Generating passwords: 100%|████████████████████████| 238328/238328 pass [00:12<00:00, 19174.67 pass/s]
2025-02-18 12:00:12,345 - INFO - Passwords have been generated and saved to: ./passwords.txt
2025-02-18 12:00:12,346 - INFO - Total passwords generated: 238,328
```


## License
```
This project is licensed under the MIT License.
```
