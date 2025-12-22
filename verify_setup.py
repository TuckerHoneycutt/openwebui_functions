#!/usr/bin/env python3
"""
Verification script to check if the PDF Template Formatter is set up correctly
Run this inside your Docker container or local environment to verify installation
"""

import sys
import os

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")
    errors = []

    try:
        import template_extractor
        print("✓ template_extractor imported successfully")
    except ImportError as e:
        errors.append(f"✗ template_extractor: {e}")
        print(f"✗ template_extractor: {e}")

    try:
        import pdf_generator
        print("✓ pdf_generator imported successfully")
    except ImportError as e:
        errors.append(f"✗ pdf_generator: {e}")
        print(f"✗ pdf_generator: {e}")

    try:
        import template_manager
        print("✓ template_manager imported successfully")
    except ImportError as e:
        errors.append(f"✗ template_manager: {e}")
        print(f"✗ template_manager: {e}")

    try:
        import template_function
        print("✓ template_function imported successfully")
    except ImportError as e:
        errors.append(f"✗ template_function: {e}")
        print(f"✗ template_function: {e}")

    return len(errors) == 0


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies...")
    errors = []

    dependencies = {
        "pdfplumber": "PDF extraction",
        "fitz": "PyMuPDF (PDF extraction alternative)",
        "docx": "DOCX processing",
        "reportlab": "PDF generation",
        "PIL": "Pillow (image processing)"
    }

    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {module} ({description})")
        except ImportError:
            errors.append(module)
            print(f"✗ {module} ({description}) - NOT INSTALLED")

    return len(errors) == 0


def check_directories():
    """Check if required directories exist and are writable"""
    print("\nChecking directories...")
    errors = []

    # Get directories from environment or defaults
    template_dir = os.getenv("TEMPLATE_STORAGE_DIR", "templates")
    temp_dir = os.getenv("PDF_TEMP_DIR", "/tmp")

    # Check template directory
    try:
        os.makedirs(template_dir, exist_ok=True)
        if os.access(template_dir, os.W_OK):
            print(f"✓ Template directory '{template_dir}' is writable")
        else:
            errors.append(f"Template directory '{template_dir}' is not writable")
            print(f"✗ Template directory '{template_dir}' is not writable")
    except Exception as e:
        errors.append(f"Cannot create template directory: {e}")
        print(f"✗ Cannot create template directory: {e}")

    # Check temp directory
    try:
        os.makedirs(temp_dir, exist_ok=True)
        if os.access(temp_dir, os.W_OK):
            print(f"✓ Temp directory '{temp_dir}' is writable")
        else:
            errors.append(f"Temp directory '{temp_dir}' is not writable")
            print(f"✗ Temp directory '{temp_dir}' is not writable")
    except Exception as e:
        errors.append(f"Cannot create temp directory: {e}")
        print(f"✗ Cannot create temp directory: {e}")

    return len(errors) == 0


def check_function_schema():
    """Check if function schema can be retrieved"""
    print("\nChecking function schema...")
    try:
        import template_function
        schema = template_function.get_function_schema()
        if schema and "name" in schema:
            print(f"✓ Function schema retrieved: {schema['name']}")
            return True
        else:
            print("✗ Function schema is invalid")
            return False
    except Exception as e:
        print(f"✗ Cannot retrieve function schema: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("PDF Template Formatter - Setup Verification")
    print("=" * 60)
    print()

    results = []

    results.append(("Imports", check_imports()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Directories", check_directories()))
    results.append(("Function Schema", check_function_schema()))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✓ All checks passed! The function should work correctly.")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
