import os

# Replace this with your target directory
directory = "./results"

for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        filepath = os.path.join(directory, filename)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Find the index of the line that contains "Time"
        start_index = next((i for i, line in enumerate(lines) if "Time" in line), None)

        if start_index is not None:
            # Keep only lines from "Time" line onward
            new_lines = lines[start_index:]

            # Clean the header line
            header_line = new_lines[0]

            # Find where "Time" starts in the header line
            time_index = header_line.find("Time")

            # Trim everything before "Time", and remove all spaces
            cleaned_header = header_line[time_index:].replace(" ", "")
            new_lines[0] = cleaned_header

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print(f"Cleaned and trimmed file: {filename}")
        else:
            print(f"'Time' not found in {filename}")
