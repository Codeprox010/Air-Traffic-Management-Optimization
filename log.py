# Read file
with open("/home/mrrobot01/PROJ/TQM/LOG_FILE_UPDATED_2.txt", "r") as f:

    lines = f.readlines()

# Count lines containing "success"
count = sum(1 for line in lines if "success" in line)
count2   = sum(1 for line in lines if "False" in line or "FALSEEE" in line)
count3   = sum(1 for line in lines if any(keyword in line for keyword in ["False", "success", "skipped", "SKIPPED", "FALSEEE"]))


print(f"Total lines: {count3}")
print(f"Lines with 'success': {count}")
print(f"Lines with 'false': {count2}")
