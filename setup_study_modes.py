#!/usr/bin/env python3
"""
Setup script for study modes
Run this to create the necessary database tables for study modes
"""

import subprocess
import sys

def main():
    print("Setting up Study Modes...")
    
    try:
        # Run the study mode table creation script
        print("Creating study mode tables...")
        result = subprocess.run([sys.executable, "scripts/create_study_mode_tables.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK - Study mode tables created successfully!")
            print(result.stdout)
        else:
            print("ERROR - Error creating study mode tables:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR - {e}")
        return False
    
    print("\nStudy modes setup completed!")
    print("\nNext steps:")
    print("1. Start the API server: uvicorn app.main:app --reload")
    print("2. Test the endpoints: python scripts/test_study_modes.py")
    
    return True

if __name__ == "__main__":
    main() 