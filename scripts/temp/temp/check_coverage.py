import json

with open('coverage.json') as f:
    data = json.load(f)

print(f"Total coverage: {data['totals']['percent_covered']:.2f}%")
print(f"Files covered: {len(data['files'])}")
print("\nFiles:")
for file_path in list(data['files'].keys())[:10]:
    file_data = data['files'][file_path]
    pct = file_data['summary']['percent_covered']
    print(f"  {file_path}: {pct:.2f}%")
