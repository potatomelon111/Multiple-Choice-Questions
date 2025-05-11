# Multiple-Choice-Questions
A quick script to generate mutliple choice questions from markdown files.

## Usage
Ensure your questions are in mardown, formatted as such:
```
Question?
- option 1
- option 2
- option 3
- etc
```
Then in the terminal run:
```
pip install reportlab
python mcqs.py "C:/path/to/md/file.md"
```

This will generate a pdf in the same directory with your MCQs.

(Here's an example of what it does - markdown on the left, pdf on the right)
![image](https://github.com/user-attachments/assets/1f87a9b4-bfb9-48dc-9948-b7621eb2919c)

