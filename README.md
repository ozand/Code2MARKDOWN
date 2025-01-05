# Code2MARKDOWN

Code2MARKDOWN is a Streamlit-based web application that generates structured Markdown documentation from your project's source code. It provides an easy way to create comprehensive project overviews, README files, or documentation for code repositories.

## Features

- Analyzes project structure and generates a tree view
- Reads and includes content from source code files
- Supports multiple template options for different documentation needs
- Excludes files and folders based on common patterns and .gitignore rules
- Provides a user-friendly web interface for easy interaction
- Allows copying generated Markdown to clipboard

## Installation

1. Clone the repository:

   git clone https://github.com/yourusername/Code2MARKDOWN.git
   cd Code2MARKDOWN

2. Create a virtual environment (optional but recommended):

   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required dependencies:

   pip install -r requirements.txt

## Usage

1. Start the Streamlit app:

   streamlit run app.py

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter the path to your project folder in the text input field.

4. Select a template from the dropdown menu.

5. Click the "Generate Markdown" button to create the documentation.

6. Use the "Copy to Clipboard" button to copy the generated Markdown content.

7. Click "Refresh" to clear the current output and start over.

## Configuration

The application uses several default configurations that can be modified in the `app.py` file:

- `extensions`: List of file extensions to include in the documentation
- `exclude_folders`: List of folder names to exclude from the documentation
- `exclude_files`: List of file names to exclude from the documentation

You can customize these lists to better suit your project's needs.

## Templates

Code2MARKDOWN comes with several pre-defined templates for different documentation purposes:

- Default template
- Binary exploitation CTF solver
- Claude XML
- Code cleanup
- Cryptography CTF solver
- Code documentation
- Security vulnerability finder
- Bug fixing
- Performance improvement
- Code refactoring
- Reverse engineering CTF solver
- Web CTF solver
- Git commit message writer
- GitHub pull request writer
- GitHub README writer

You can add new templates or modify existing ones in the `templates/` directory.

## Contributing

Contributions to Code2MARKDOWN are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive commit messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure that your code follows the existing style and includes appropriate tests.

## Testing

To run the tests for Code2MARKDOWN, use the following command:

python -m unittest discover tests

(Note: Actual test files are not present in the provided codebase. You may want to add tests in the future.)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [pyperclip](https://pypi.org/project/pyperclip/) for clipboard functionality
- [pathspec](https://pypi.org/project/pathspec/) for .gitignore parsing
- [pybars3](https://pypi.org/project/pybars3/) for Handlebars template rendering

