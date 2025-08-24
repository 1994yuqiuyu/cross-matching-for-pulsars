import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def process_files_in_folder(folder_name='data'):
    # Ensure folder exists
    if not os.path.exists(folder_name):
        print(f"Folder '{folder_name}' does not exist, skipping data processing")
        return []

    # Get all files in folder
    files = os.listdir(folder_name)

    # Filter for .txt files
    txt_files = [f for f in files if f.endswith('.txt')]

    output_files = []
    for index, file_name in enumerate(txt_files, start=1):
        # Build full file path
        file_path = os.path.join(folder_name, file_name)

        # Build output filename
        output_file_name = f"test{index}.txt"
        output_files.append(output_file_name)

        # Process input and output files
        with open(file_path, 'r') as in_file, open(output_file_name, 'w') as out_file:
            lines = in_file.readlines()
            for line in lines:
                # Check if line contains "M3"
                if "M3" in line:
                    out_file.write(line)

    return output_files


def process_file(file_path):
    data_list = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                sub_str_list = line.strip().split()
                filtered_list = [s for s in sub_str_list if re.search(r"\d+\.?\d*", s)]
                if filtered_list:
                    data_list.append(filtered_list)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return data_list


def group_data(file_paths):
    all_data_lists = []
    for file_path in file_paths:
        data_list = process_file(file_path)
        all_data_lists.append(data_list)

    line_to_group = {}
    group_dict = defaultdict(list)
    group_id_counter = 1
    line_str_to_data = {}

    # Create mapping from line string to original data
    for m, data_list in enumerate(all_data_lists):
        for i, line_data in enumerate(data_list):
            line_str = str(line_data)
            line_str_to_data[line_str] = line_data

    # Match data and create groups
    for m in range(len(all_data_lists)):
        for n in range(m + 1, len(all_data_lists)):
            for i in range(len(all_data_lists[m])):
                for j in range(len(all_data_lists[n])):
                    # Check if period difference ratio is less than 1%
                    if abs(float(all_data_lists[m][i][7]) - float(all_data_lists[n][j][7])) / float(
                            all_data_lists[m][i][7]) < 0.01:
                        # Calculate dispersion ratio
                        val1 = float(all_data_lists[m][i][1])
                        val2 = float(all_data_lists[n][j][1])
                        ratio1 = (val1 - val2) / val1 if val1 != 0 else 0
                        ratio2 = (val1 - val2) / val2 if val2 != 0 else 0

                        if (val1 > val2 and abs(ratio1) < 0.01) or \
                                (val1 < val2 and abs(ratio2) < 0.01) or \
                                (val1 == val2):
                            line1_str = str(all_data_lists[m][i])
                            line2_str = str(all_data_lists[n][j])

                            current_group = None
                            if line1_str in line_to_group:
                                current_group = line_to_group[line1_str]
                            elif line2_str in line_to_group:
                                current_group = line_to_group[line2_str]

                            if current_group is None:
                                current_group = group_id_counter
                                group_id_counter += 1

                            line_to_group[line1_str] = current_group
                            line_to_group[line2_str] = current_group

    # Assign data to groups
    for line_str, group_id in line_to_group.items():
        if line_str in line_str_to_data:
            group_dict[group_id].append(line_str_to_data[line_str])

    # Create groups directory
    if not os.path.exists("groups"):
        os.makedirs("groups")

    # Write group files
    with open("process_all_M3_0.01.txt", 'w') as fw:
        for group_id, lines in group_dict.items():
            group_filename = os.path.join("groups", f"group_{group_id}.txt")
            with open(group_filename, 'w') as group_file:
                for line_data in lines:
                    # Write to group file (data only)
                    group_file.write(" ".join(line_data) + "\n")
                    # Write to summary file (with group number)
                    fw.write(f"Group {group_id}: {' '.join(line_data)}\n")

    print(f"Total of {len(group_dict)} groups saved to groups folder")
    return group_dict


def sort_groups():
    if not os.path.exists("process_all_M3_0.01.txt"):
        print("Group file does not exist, skipping sorting")
        return

    with open("process_all_M3_0.01.txt", "r") as f:
        lines = f.readlines()

    # Sort by group number
    sorted_lines = sorted(lines, key=lambda x: int(x.split("Group ")[1].split(":")[0]))

    # Write sorted file
    with open("process_all_M3_0.01_sorted.txt", "w") as f:
        for line in sorted_lines:
            f.write(line)

    print("File sorted by group number and saved as process_all_M3_0.01_sorted.txt")


def calculate_difference_ratios_from_average(lst):
    if not lst:
        return []
    average_value = sum(lst) / len(lst)
    # Calculate permille difference
    return [(x - average_value) / average_value * 1000 for x in lst]


def plot_single_group(group_file, group_id):
    """Plot chart for single group"""
    if not os.path.exists(group_file):
        print(f"Group file {group_file} does not exist, skipping plot")
        return

    with open(group_file, 'r') as file:
        lines = file.readlines()

    if len(lines) < 2:
        print(f"Group {group_id} has insufficient data points ({len(lines)}), skipping plot")
        return

    # Parse data
    dates = []
    values = []
    snrs = []
    dms = []

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 8:  # Ensure enough data columns
            continue
        dates.append(parts[0])
        values.append(float(parts[7]))
        snrs.append(float(parts[2]))
        dms.append(float(parts[1]))

    # Calculate permille differences
    period_permille_ratio = calculate_difference_ratios_from_average(values)
    dm_permille_ratio = calculate_difference_ratios_from_average(dms)

    # Fixed point size
    fixed_size = 200

    # Calculate min and max SNR for grayscale mapping
    min_snr = min(snrs)
    max_snr = max(snrs)
    snr_range = max_snr - min_snr

    # Use grayscale for SNR (darker for higher SNR)
    gray_values = []
    for snr in snrs:
        if snr_range > 0:
            normalized = (snr - min_snr) / snr_range
            gray_value = 1 - normalized  # Invert so higher SNR is darker
            gray_values.append((gray_value, gray_value, gray_value))  # Same RGB channels
        else:
            gray_values.append((0.5, 0.5, 0.5))  # Medium gray when all SNR are same

    # Create scatter plot
    plt.figure(figsize=(8, 6))
    for i in range(len(period_permille_ratio)):
        plt.scatter(period_permille_ratio[i], dm_permille_ratio[i],
                    s=fixed_size,
                    color=gray_values[i],
                    alpha=0.8)  # Appropriate transparency

    # Set labels and title
    plt.title(f'M3 fake pulsar ', fontsize=14)
    plt.xlabel('Permille ratio of P difference', fontsize=12)
    plt.ylabel('Permille ratio of DM difference', fontsize=12)

    # Add reference lines
    plt.axhline(y=0, color='r', linestyle='--', linewidth=0.8)
    plt.axvline(x=0, color='r', linestyle='--', linewidth=0.8)

    # Add colorbar
    if snr_range > 0:
        sm = plt.cm.ScalarMappable(cmap='gray_r', norm=plt.Normalize(vmin=min_snr, vmax=max_snr))
        sm.set_array([])
        cbar = plt.colorbar(sm, orientation='vertical', pad=0.1)
        cbar.set_label('SNR', fontsize=10)
        cbar.ax.tick_params(labelsize=8)

    # Save plot
    plot_filename = os.path.join("groups", f"group_{group_id}_plot.png")
    plt.tight_layout()
    plt.savefig(plot_filename, dpi=150)
    plt.close()
    print(f"Group {group_id} plot saved as {plot_filename}")


def plot_all_groups():
    """Plot charts for all groups"""
    # Ensure groups directory exists
    if not os.path.exists("groups"):
        print("Groups directory does not exist, cannot plot")
        return

    # Get all group files
    group_files = [f for f in os.listdir("groups") if f.startswith("group_") and f.endswith(".txt")]

    if not group_files:
        print("No group files found in groups directory")
        return

    # Create plots for each group
    for group_file in group_files:
        group_id = group_file.split("_")[1].split(".")[0]
        try:
            group_id = int(group_id)
            file_path = os.path.join("groups", group_file)
            plot_single_group(file_path, group_id)
        except ValueError:
            print(f"Skipping invalid group file: {group_file}")


def main():
    # 1. Read data
    folder_name = "data"  # Default folder name
    output_files = process_files_in_folder(folder_name)

    if not output_files:
        print("No files found to process")
        return

    # 2. Filter data and create groups
    group_data(output_files)

    # 3. Sort by group number
    sort_groups()

    # 4. Create plots for each group
    plot_all_groups()

    print("All group plots generated")


if __name__ == "__main__":
    main()