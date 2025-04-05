# JSON Parser

A Python-based JSON parser and scanner that reads tokenized input from `.txt` files, builds a parse tree, and outputs valid JSON or a structured error message.

## 🧠 Features

- Custom scanner to tokenize JSON-like inputs
- Recursive descent parser
- Handles objects, arrays, strings, numbers, booleans, and nulls
- Type validation for arrays (homogeneous elements)
- Detects and reports:
  - Invalid tokens
  - Duplicate keys in objects
  - Type mismatches in arrays
  - Malformed numbers and strings
  - Extra trailing commas
- Outputs valid `.json` files or JSON-formatted error messages

## 📁 Project Structure

- json_scanner.py | Defines TokenType, Token, and Lexer classes 
- json_parser.py | Main parser logic 
- test0X.txt | Example input files 
- output0X.json | Output files (created after running)


## 🧪 Input Format

Input `.txt` files contain pre-tokenized lines. Examples:

```
<{> 
<str,"name"> 
<:> 
<str,"Ben"> 
<,> 
<str,"age"> 
<:> 
<num,21> 
<}>
```

## 🧾 Output Format

On success:
```json
{
  "name": "Ben",
  "age": 21
}
```

On error:
```json
{
  "error": "Error type 5 at \"name\": Duplicate keys found."
}
```


## 🚀 Getting Started
0. Ensure you have [python3](https://www.python.org/downloads/) installed.
1. Clone the repo
```
git clone https://github.com/your-username/json-parser.git
cd json-parser
```
2. Adjust test files to your liking in test.00.txt, test.01.txt, etc.

3. Run the parser
```bash
python3 json_parser.py
```

## ⚠️ Error Types
Specific Types:
1.	Malformed number (starts/ends with a dot)
2.	Empty string
3.	Number starts with + or leading 0
4/7.	Reserved words used as strings (e.g. "true")
5.	Duplicate keys in objects
6.	Mixed types in arrays

Other:
- Extra comma	Trailing commas in arrays or objects

## 📃 License
MIT License
