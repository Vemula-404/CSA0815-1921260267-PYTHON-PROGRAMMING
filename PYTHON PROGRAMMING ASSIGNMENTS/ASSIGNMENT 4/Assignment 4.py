import re
import os

# ==========================================
# CUSTOM EXCEPTIONS
# ==========================================
class InvalidRecord(Exception):
    """Raised when a line of the registration file is not in the expected format."""
    pass

# ==========================================
# CORE LOGIC MODULES (Consolidated)
# ==========================================

class RegistrationProcessor:
    def __init__(self):
        self.all_valid_records = []
        self.all_errors = []

    def validate_email(self, email):
        """Checks if the email follows a standard pattern."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def read_files(self, file_list):
        """Stage: Reading and Validating (Task 6 Stage 4)"""
        for file_path in file_list:
            try:
                with open(file_path, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        parts = line.split(',')
                        
                        # Rule: Check for exactly 5 fields
                        if len(parts) != 5:
                            self.all_errors.append(f"[{file_path}] Line {line_num}: Expected 5 fields, found {len(parts)}")
                            continue
                        
                        reg_no, name, dept, email, events_raw = parts
                        
                        # Rule: Validate Email
                        if not self.validate_email(email):
                            self.all_errors.append(f"[{file_path}] Line {line_num}: Invalid email '{email}'")
                            continue
                        
                        # Parse events
                        events = [e.strip() for e in events_raw.split(';') if e.strip()]
                        
                        self.all_valid_records.append({
                            'reg_no': reg_no,
                            'name': name,
                            'dept': dept,
                            'email': email,
                            'events': events
                        })
            except FileNotFoundError:
                self.all_errors.append(f"[{file_path}] Error: File not found.")
            except Exception as e:
                self.all_errors.append(f"[{file_path}] Unexpected error: {str(e)}")

    def process_data(self):
        """Stage: Deduplication and Event Mapping (Task 6 Stage 4)"""
        seen_reg_nos = set()
        clean_master_list = []
        event_map = {}

        for rec in self.all_valid_records:
            # Rule: Remove Duplicates
            if rec['reg_no'] in seen_reg_nos:
                continue
            
            seen_reg_nos.add(rec['reg_no'])
            clean_master_list.append(rec)
            
            # Grouping by event
            for event in rec['events']:
                if event not in event_map:
                    event_map[event] = []
                event_map[event].append(f"{rec['name']} ({rec['reg_no']})")
                
        return clean_master_list, event_map

    def generate_reports(self, master_list, event_map, error_log):
        """Stage: Output Generation (Task 6 Stage 4)"""
        # 1. Master List
        with open("master_registration.txt", "w") as f:
            for r in master_list:
                f.write(f"{r['reg_no']}, {r['name']}, {r['dept']}, {r['email']}, {r['events']}\n")
        
        # 2. Event-wise files
        for event, participants in event_map.items():
            filename = f"event_{event.replace(' ', '_').lower()}.txt"
            with open(filename, "w") as f:
                f.write("\n".join(participants))
                
        # 3. Error Log
        with open("error_log.txt", "w") as f:
            if error_log:
                f.write("\n".join(error_log))
            else:
                f.write("No errors detected.")

# ==========================================
# EXECUTION AND DEMONSTRATION (Task 6 Stage 5)
# ==========================================

def setup_test_environment():
    """Creates sample files to demonstrate all scenarios requested in Task 6."""
    print("Setting up test files...")
    
    # 1. Clean File
    with open("dept_cs.txt", "w") as f:
        f.write("101,Alice,CS,alice@test.com,Dance;Music\n")
        f.write("102,Bob,CS,bob@test.com,Music\n")

    # 2. File with Duplicates and Invalid Email
    with open("dept_ece.txt", "w") as f:
        f.write("201,Eve,ECE,eve@test.com,Coding\n")
        f.write("101,Alice,CS,alice@test.com,Dance\n")       # DUPLICATE of 101
        f.write("202,Frank,ECE,frank_at_test.com,Coding\n") # INVALID EMAIL

    # 3. File with Damaged Lines
    with open("dept_me.txt", "w") as f:
        f.write("301,Grace,ME,grace@test.com,Design;Coding\n")
        f.write("302,Broken,ME,broken@test.com\n")           # DAMAGED (Missing field)

    return ["dept_cs.txt", "dept_ece.txt", "dept_me.txt", "missing_file.txt"]

def main():
    # Prepare files
    test_files = setup_test_environment()
    
    # Initialize Processor
    processor = RegistrationProcessor()
    
    # Step 1: Read and Validate
    print("Step 1: Reading files...")
    processor.read_files(test_files)
    
    # Step 2: Process (Deduplicate and Group)
    print("Step 2: Processing data...")
    master_list, event_map = processor.process_data()
    
    # Step 3: Report
    print("Step 3: Generating reports...")
    processor.generate_reports(master_list, event_map, processor.all_errors)
    
    # Summary Output
    print("\n" + "="*30)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("="*30)
    print(f"Clean Students Registered: {len(master_list)}")
    print(f"Errors/Damaged lines found: {len(processor.all_errors)}")
    print("-" * 30)
    print("Files Created:")
    print(" - master_registration.txt")
    print(" - error_log.txt")
    print(" - event_*.txt (one per event)")
    print("="*30)

if __name__ == "__main__":
    main()