with open("tests/test_timelapse.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith("#"):
        if not stripped.endswith(".") and not stripped.endswith("?") and not stripped.endswith("!") and not stripped.endswith(":") and len(stripped) > 1:
            line = line.rstrip() + ".\n"
    new_lines.append(line)

with open("tests/test_timelapse.py", "w") as f:
    f.writelines(new_lines)
