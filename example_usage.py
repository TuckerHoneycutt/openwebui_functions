"""
Example usage script for testing the PDF Template Formatter function

This script demonstrates how to use the function outside of OpenWebUI
for testing purposes.
"""

import asyncio
import base64
from pathlib import Path
from functions import format_to_pdf_template


async def example_upload_template():
    """Example: Upload a template"""
    print("Example 1: Uploading a template...")

    # Read a sample PDF file (replace with your own)
    template_path = "sample_template.pdf"

    if not Path(template_path).exists():
        print(f"Template file {template_path} not found. Skipping upload example.")
        return None

    with open(template_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("utf-8")

    result = await format_to_pdf_template(
        action="upload_template",
        template_name="Sample Template",
        template_file=file_data,
        file_type="pdf"
    )

    print(f"Upload result: {result}")
    return result.get("template_id")


async def example_list_templates():
    """Example: List all templates"""
    print("\nExample 2: Listing templates...")

    result = await format_to_pdf_template(action="list_templates")

    print(f"Available templates: {result}")
    return result.get("templates", [])


async def example_get_template_info(template_name: str):
    """Example: Get template information"""
    print(f"\nExample 3: Getting info for template '{template_name}'...")

    result = await format_to_pdf_template(
        action="get_template_info",
        template_name=template_name
    )

    print(f"Template info: {result}")
    return result.get("template_info")


async def example_generate_pdf(template_name: str, content: str):
    """Example: Generate PDF from content"""
    print(f"\nExample 4: Generating PDF with template '{template_name}'...")

    result = await format_to_pdf_template(
        action="generate_pdf",
        template_name=template_name,
        content=content
    )

    if result.get("success"):
        # Save the generated PDF
        pdf_data = base64.b64decode(result["pdf_data"])
        output_path = f"output_{template_name.replace(' ', '_')}.pdf"

        with open(output_path, "wb") as f:
            f.write(pdf_data)

        print(f"PDF generated successfully: {output_path}")
        return output_path
    else:
        print(f"Error generating PDF: {result.get('error')}")
        return None


async def main():
    """Run all examples"""
    print("=" * 60)
    print("PDF Template Formatter - Example Usage")
    print("=" * 60)

    # Example content
    sample_content = """
# Executive Summary

This is a sample document generated using the PDF Template Formatter.

## Key Points

- First important point
- Second important point
- Third important point

## Details

This paragraph contains detailed information about the topic.
It demonstrates how regular paragraphs are formatted.

## Conclusion

In conclusion, this example demonstrates the functionality of the PDF Template Formatter.
"""

    try:
        # Upload template (if available)
        template_id = await example_upload_template()

        # List templates
        templates = await example_list_templates()

        if templates:
            # Use first available template
            template_name = templates[0]["template_name"]

            # Get template info
            await example_get_template_info(template_name)

            # Generate PDF
            await example_generate_pdf(template_name, sample_content)
        else:
            print("\nNo templates available. Please upload a template first.")

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
