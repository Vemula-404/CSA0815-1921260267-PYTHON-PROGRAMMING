import re
import os

# =================================================================
# TASK 6: COLLEGE FEST REGISTRATION SYSTEM (Final Solution)
# =================================================================

class FestRegistrationSystem:
    def __init__(self):
        self.master_list = []       # Stores clean, validated records
        self.event_map = {}         # Stores { 'EventName': [student_names] }
        self.error_log = []         # Stores all errors found
        self.seen_reg_nos = set()   # For O(1) Duplicate Detection

    def validate_email(self, email):
        """Validates email format using Regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def process_files(self, file_paths):
        """
        Main processing loop. 
        Implements Stage 1, 2, & 3: Reading, Validating, and Error Handling.
        """
        for path in file_paths:
            # Rule: Program must never stop if a file is missing
            if not os.path.exists(path):
                self.error_log.append(f"FILE ERROR: '{path}' not found. Skipping.")
                continue

            try:
                with open(path, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        self._process_line(line, line_num, path)
            except Exception as e:
                self.error_log.append(f"CRITICAL ERROR: Could not read '{path}': {str(e)}")

    def _process_line(self, line, line_num, filename):
        """Internal method to validate individual lines (Stage 3)."""
        line = line.strip()
        if not line:
            return

        parts = line.split(',')
        
        # Validation: Damaged Lines (Field Count)
        if len(parts) != 5:
            self.error_log.append(f"[{filename}:{line_num}] Damaged line: Expected 5 fields, found {len(parts)}")
            return

        reg_no, name, dept, email, events_raw = parts

        # Validation: Email Format
        if not self.validate_email(email):
            self.error_log.append(f"[{filename}:{line_num}] Invalid email: '{email}'")
            return

        # Rule: Duplicate Detection (Stage 3)
        if reg_no in self.seen_reg_nos:
            # We don't log duplicates as 'errors' usually, but we skip them
            return 
        
        # If all checks pass, it's a valid registration
        self.seen_reg_nos.add(reg_no)
        events = [e.strip() for e in events_raw.split(';') if e.strip()]
        
        record = {
            'reg_no': reg_no,
            'name': name,
            'dept': dept,
            'email': email,
            'events': events
        }
        
        self.master_list.append(record)

        # Map students to events for the event-wise reports
        for event in events:
            if event not in self.event_map:
                self.event_map[event] = []
            self.event_map[event].append(f"{name} ({reg_no})")

    def write_outputs(self):
        """Stage 4: Writing the required Output Files."""
        
        # 1. Clean Master List
        with open("fest_master_list.txt", "w") as f:
            f.write("REG_NO | NAME | DEPT | EMAIL | EVENTS\n")
            f.write("-" * 50 + "\n")
            for r in self.master_list:
                f.write(f"{r['reg_no']} | {r['name']} | {r['dept']} | {r['email']} | {', '.join(r['events'])}\n")

        # 2. Event-wise Participant Lists
        for event, participants in self.event_map.items():
            safe_name = event.replace(" ", "_").lower()
            with open(f"event_{safe_name}.txt", "w") as f:
                f.write(f"Participants for {event}:\n")
                f.write("\n".join(participants))

        # 3. Summary Report
        with open("fest_summary_report.txt", "w") as f:
            f.write("COLLEGE FEST REGISTRATION SUMMARY\n")
            f.write("=" * 30 + "\n")
            f.write(f"Total Unique Registrations: {len(self.master_list)}\n")
            f.write(f"Total Events Organized: {len(self.event_map)}\n")
            f.write(f"Total Errors Logged: {len(self.error_log)}\n")

        # 4. Error Log
        with open("fest_error_log.txt", "w") as f:
            if self.error_log:
                f.write("\n".join(self.error_log))
            else:
                f.write("No errors detected during processing.")

# =================================================================
# STAGE 5: IMPLEMENTATION AND DEMONSTRATION
# =================================================================

def setup_demo_files():
    """Creates test files to prove the program works as requested."""
    # File 1: Clean Data
    with open("dept_cs.txt", "w") as f:
        f.write("101,Alice,CS,alice@test.com,Dance;Music\n")
        f.write("102,Bob,CS,bob@test.com,Music\n")

    # File 2: Duplicates and Invalid Emails
    with open("dept_ece.txt", "w") as f:
        f.write("201,Eve,ECE,eve@test.com,Coding\n")
        f.write("101,Alice,CS,alice@test.com,Dance\n")       # DUPLICATE
        f.write("202,Frank,ECE,frank_at_test.com,Coding\n") # INVALID EMAIL

    # File 3: Damaged Lines
    with open("dept_me.txt", "w") as f:
        f.write("301,Grace,ME,grace@test.com,Design;Coding\n")
        f.write("302,Broken,ME,broken@test.com\n")           # DAMAGED (Missing field)

    return ["dept_cs.txt", "dept_ece.txt", "dept_me.txt", "missing_file.txt"]

if __name__ == "__main__":
    # 1. Prepare the environment
    files_to_process = setup_demo_files()
    
    # 2. Initialize and run the system
    system = FestRegistrationSystem()
    
    print("Starting Fest Registration Processor...")
    system.process_files(files_to_process)
    system.write_outputs()
    
    # 3. Final Confirmation
    print("\n" + "="*30)
    print("PROCESSING COMPLETE")
    print("="*30)
    print(f"Master List:  fest_master_list.txt")
    print(f"Event Files:  event_*.txt")
    print(f"Summary:      fest_summary_report.txt")
    print(f"Error Log:    fest_error_log.txt")
    print("="*30)
    print("Check your folder for the generated files!")