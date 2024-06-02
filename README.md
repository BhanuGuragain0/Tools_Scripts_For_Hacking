# Password Generator

This Python script generates random passwords within specified length constraints using custom character sets.

## Features

- Generate passwords of variable length.
- Specify custom character sets for password generation.
- Multi-threaded password generation for improved performance.

##  Run the script:

`python password_generator.py`

4. Follow the on-screen prompts to specify the minimum and maximum password lengths, file path to save passwords, and optionally, custom character sets.

## Requirements

- Python 3.x

## How it Works

The script utilizes Python's itertools module to generate combinations of characters based on the specified length constraints and character sets. It employs multi-threading to distribute the workload across multiple threads, enhancing performance by parallelizing the password generation process.

## License

This project is licensed under the MIT License.

