import os
import shutil
import subprocess
import sys
import zipfile

# Define variables
PACKAGE_DIR = "package"
ZIP_FILE = "lambda_package.zip"
REQUIREMENTS_FILE = "requirements_optimized.txt"
SOURCE_FILES = [
    "lambda_function.py",
    "generate_new_feature_plan.py",
    "moodle_students.py",
    "ai_integration.py",
    "database.py",
    "config.py",
    "moodle_study_plans.py",
    "moodle_grades.py",
    "moodle_api.py",
]

def main():
    """
    Creates a deployment package for the AWS Lambda function.
    """
    print("Starting Lambda package creation...")

    # Set the base path to the script's directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    package_path = os.path.join(base_path, PACKAGE_DIR)
    zip_path = os.path.join(base_path, ZIP_FILE)
    requirements_path = os.path.join(base_path, REQUIREMENTS_FILE)

    # 1. Clean up old package directory and zip file
    print("Cleaning up old files...")
    if os.path.isdir(package_path):
        shutil.rmtree(package_path)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 2. Create a fresh package directory
    print("Creating a new package directory...")
    os.makedirs(package_path)

    # 3. Install dependencies into the package directory
    if os.path.exists(requirements_path):
        print(f"Installing dependencies from {REQUIREMENTS_FILE}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--target", package_path,
                "-r", requirements_path
            ])
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print(f"Warning: {REQUIREMENTS_FILE} not found. Skipping dependency installation.")

    # 4. Copy source files into the package directory
    print("Copying source files...")
    for file_name in SOURCE_FILES:
        source_file = os.path.join(base_path, file_name)
        if os.path.exists(source_file):
            shutil.copy(source_file, package_path)
        else:
            print(f"Warning: Source file {file_name} not found. Skipping.")

    # 5. Create the zip file
    print(f"Creating zip file: {ZIP_FILE}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(package_path):
            for file in files:
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(file_path, package_path)
                zf.write(file_path, archive_name)

    print(f"Lambda package created successfully: {zip_path}")

if __name__ == "__main__":
    main() 