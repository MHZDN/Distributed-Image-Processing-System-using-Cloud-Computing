from datetime import datetime

def merge_and_sort_logs(log_file1, log_file2, merged_log_file):
    try:
        # Read contents of both log files
        with open(log_file1, 'r') as file1, open(log_file2, 'r') as file2:
            log1 = file1.readlines()
            log2 = file2.readlines()

        # Merge logs
        merged_log = log1 + log2

        # Sort logs by timestamp
        merged_log.sort(key=lambda x: x.split(' - ')[0])
        # Clear the log file
        open(merged_log_file, 'w').close()
        # Write merged and sorted log to a new file
        with open(merged_log_file, 'w') as merged_file:
            merged_file.writelines(merged_log)
    except Exception as e:
        print(f"An error occurred while merging and sorting logs: {e}")



