from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile
import time
import urllib.request


# -------------------------------------------------
# Project paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TESSERACT_DIR = PROJECT_ROOT / "tesseract"
TESSERACT_EXE = TESSERACT_DIR / "tesseract.exe"

# -------------------------------------------------
# Ollama Configuration
# -------------------------------------------------

MODELS_DIR = PROJECT_ROOT / "models"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_HOST = "http://127.0.0.1:11434"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# -------------------------------------------------
# Install Python dependencies
# -------------------------------------------------

def install_python_dependencies() -> None:

    if not REQUIREMENTS_FILE.exists():
        raise FileNotFoundError(
            f"requirements.txt not found: {REQUIREMENTS_FILE}"
        )

    print("\nInstalling Python dependencies...")
    print(f"Requirements file: {REQUIREMENTS_FILE}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        check=True,
    )

    print("✅ Python dependencies installed.")


# -------------------------------------------------
# Start Ollama with project-local models directory
# -------------------------------------------------

def start_ollama() -> None:

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(MODELS_DIR)

    print("\nStarting Ollama with project-local model storage...")
    print(f"Model directory: {MODELS_DIR}")

    subprocess.Popen(
        ["ollama", "serve"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    # Give the server a few seconds to start.
    for _ in range(15):
        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    (
                        "try { "
                        "Invoke-WebRequest "
                        f"-Uri '{OLLAMA_HOST}/api/tags' "
                        "-UseBasicParsing "
                        "-TimeoutSec 2 | Out-Null; "
                        "exit 0 "
                        "} catch { exit 1 }"
                    ),
                ],
                capture_output=True,
            )

            if result.returncode == 0:
                print("✅ Ollama server is running.")
                return

        except Exception:
            pass

        time.sleep(1)

    raise RuntimeError(
        "Ollama server did not start within the expected time."
    )


# -------------------------------------------------
# Ensure required Ollama model exists
# -------------------------------------------------

def setup_ollama_model() -> None:

    print(f"\nChecking Ollama model: {OLLAMA_MODEL}")

    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(MODELS_DIR)

    result = subprocess.run(
        ["ollama", "list"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    if OLLAMA_MODEL in result.stdout:
        print(f"✅ {OLLAMA_MODEL} is already available.")
        return

    print(f"{OLLAMA_MODEL} not found.")
    print(f"Downloading {OLLAMA_MODEL}...")

    subprocess.run(
        ["ollama", "pull", OLLAMA_MODEL],
        env=env,
        check=True,
    )

    print(f"✅ {OLLAMA_MODEL} downloaded successfully.")


# -------------------------------------------------
# Tesseract version
# -------------------------------------------------

TESSERACT_VERSION = "5.5.3.20260724"

TESSERACT_URL = (
    "https://github.com/tesseract-ocr/tesseract/releases/download/"
    f"5.5.3/tesseract-ocr-w64-setup-{TESSERACT_VERSION}.exe"
)

# SHA256 published for the Windows 64-bit installer
EXPECTED_SHA256 = (
    "BEE9E3434BD94FD65387D9BE28CD467A41F61B1275383B55B0F59A1331270AE4"
)


# -------------------------------------------------
# Helper: calculate SHA256
# -------------------------------------------------

def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest().upper()


# -------------------------------------------------
# Install Tesseract locally
# -------------------------------------------------

def install_tesseract() -> None:

    if TESSERACT_EXE.exists():
        print("✅ Local Tesseract already exists.")
        print(f"Path: {TESSERACT_EXE}")
        return

    print("Tesseract not found in project.")
    print("Downloading Tesseract 5.5.3...")

    TESSERACT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:

        installer_path = (
            Path(temp_dir)
            / f"tesseract-{TESSERACT_VERSION}-installer.exe"
        )

        urllib.request.urlretrieve(
            TESSERACT_URL,
            installer_path,
        )

        print("Download completed.")

        print("Checking installer SHA256...")

        actual_sha256 = calculate_sha256(installer_path)

        if actual_sha256 != EXPECTED_SHA256:
            raise RuntimeError(
                "Tesseract installer SHA256 verification failed.\n"
                f"Expected: {EXPECTED_SHA256}\n"
                f"Actual:   {actual_sha256}"
            )

        print("✅ SHA256 verification passed.")

        print("Installing Tesseract into project folder...")

        # NSIS installers support /S for silent installation.
        # /D= must be the final argument.
        print("Administrator permission is required for the Tesseract installer.")
        print("A Windows UAC prompt may appear. Please click Yes.")

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    "Start-Process "
                    f"-FilePath '{installer_path}' "
                    f"-ArgumentList '/S','/D={TESSERACT_DIR}' "
                    "-Verb RunAs "
                    "-Wait"
                ),
            ],
            check=True,
        )

    if not TESSERACT_EXE.exists():
        raise RuntimeError(
            "Tesseract installation finished, "
            "but tesseract.exe was not found."
        )

    print("\n✅ Tesseract installed successfully!")
    print(f"Path: {TESSERACT_EXE}")


# -------------------------------------------------
# Verify installation
# -------------------------------------------------

def verify_tesseract() -> None:

    print("\nVerifying Tesseract...")

    result = subprocess.run(
        [str(TESSERACT_EXE), "--version"],
        capture_output=True,
        text=True,
        check=True,
    )

    print(result.stdout)


# -------------------------------------------------
# Main
# -------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("Document Intelligence System - Environment Setup")
    print("=" * 60)

    install_python_dependencies()

    install_tesseract()
    verify_tesseract()

    start_ollama()
    setup_ollama_model()

    print("=" * 60)
    print("Environment setup complete.")
    print("=" * 60)