from pathlib import Path

a = str(Path('file.txt'))[:4] + '.pdf'

p = Path("file.txt")
b = str(p)[:4] + '.pdf'
