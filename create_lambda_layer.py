import os
import shutil
import subprocess
import sys
import zipfile

# Define layer-specific variables
LAYER_DIR = "lambda_layer"
LAYER_ZIP_FILE = "lambda_layer.zip"
LAYER_REQUIREMENTS_FILE = "layer_requirements.txt"

# Packages to be included in the layer
LAYER_PACKAGES = [
    "pandas",
    "numpy",
    "mysql-connector-python",
    "openai",
    "anthropic",
]

def create_requirements_file(base_path):
    """Creates the layer_requirements.txt file."""
    requirements_path = os.path.join(base_path, LAYER_REQUIREMENTS_FILE)
    print(f"Creating {LAYER_REQUIREMENTS_FILE}...")
    with open(requirements_path, "w") as f:
        for package in LAYER_PACKAGES:
            f.write(f"{package}\n")
    return requirements_path

def create_lambda_layer():
    """
    Creates a Lambda Layer zip file containing large dependencies.
    """
    print("Starting Lambda Layer creation...")

    base_path = os.path.dirname(os.path.abspath(__file__))
    layer_path = os.path.join(base_path, LAYER_DIR)
    layer_zip_path = os.path.join(base_path, LAYER_ZIP_FILE)

    # 1. Clean up old layer directory and zip file
    print("Cleaning up old layer files...")
    if os.path.isdir(layer_path):
        shutil.rmtree(layer_path)
    if os.path.exists(layer_zip_path):
        os.remove(layer_zip_path)

    # 2. Create the requirements file for the layer
    requirements_file = create_requirements_file(base_path)

    # 3. Create a fresh layer directory with the required structure for Lambda Layers
    #    The packages must be in a 'python' subdirectory.
    python_dir = os.path.join(layer_path, "python")
    os.makedirs(python_dir)

    # 4. Install dependencies into the 'python' subdirectory
    print(f"Installing layer dependencies from {LAYER_REQUIREMENTS_FILE}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--target", python_dir,
            "-r", requirements_file
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error installing layer dependencies: {e}")
        # Clean up created requirements file on failure
        os.remove(requirements_file)
        sys.exit(1)

    # 5. Create the layer zip file
    print(f"Creating layer zip file: {LAYER_ZIP_FILE}...")
    with zipfile.ZipFile(layer_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(layer_path):
            for file in files:
                file_path = os.path.join(root, file)
                # The archive path should be relative to the layer directory's root
                archive_name = os.path.relpath(file_path, layer_path)
                zf.write(file_path, archive_name)

    # 6. Clean up the temporary requirements file
    os.remove(requirements_file)
    print(f"Lambda Layer created successfully: {layer_zip_path}")
    print(f"Next steps: Upload '{LAYER_ZIP_FILE}' to AWS Lambda as a new layer.")

if __name__ == "__main__":
    create_lambda_layer() 