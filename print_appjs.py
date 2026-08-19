from pathlib import Path

for i, line in enumerate(Path('web/app.js').read_text().splitlines(), start=1):
    print(f'{i}: {line}')
