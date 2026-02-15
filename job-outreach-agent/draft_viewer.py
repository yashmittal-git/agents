"""
Draft Viewer - Generate dynamic HTML view of job outreach drafts

The HTML embeds JSON data but can be regenerated anytime to pick up changes.
"""

import json
import webbrowser
from pathlib import Path


def generate_html_draft(draft_json_path: str) -> str:
    """
    Generate HTML view with embedded JSON data

    Args:
        draft_json_path: Path to draft JSON file

    Returns:
        Path to generated HTML file
    """
    # Load JSON data
    with open(draft_json_path, 'r') as f:
        draft_data = json.load(f)

    # Load dynamic template
    template_path = Path(__file__).parent / "templates" / "draft_viewer_dynamic.html"
    with open(template_path, 'r') as f:
        html_template = f.read()

    # Embed JSON data in HTML
    json_data_str = json.dumps(draft_data, indent=2)
    html_content = html_template.replace(
        '// INJECT_JSON_DATA_HERE',
        f'const embeddedDraftData = {json_data_str};'
    )

    # Also update the jsonFile path
    html_content = html_content.replace(
        "const jsonFile = urlParams.get('json') || window.location.pathname.replace('.html', '.json');",
        f"const jsonFile = '{Path(draft_json_path).name}';"
    )

    # Save HTML file
    html_path = draft_json_path.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(html_content)

    return html_path


def view_draft(draft_json_path: str, auto_open: bool = True):
    """
    Generate and open HTML view of draft

    Args:
        draft_json_path: Path to draft JSON file
        auto_open: Whether to auto-open in browser

    Returns:
        Path to generated HTML file
    """
    html_path = generate_html_draft(draft_json_path)
    print(f"\n✅ HTML draft generated: {html_path}")
    print(f"📝 To see updates, edit JSON and regenerate: python draft_viewer.py {draft_json_path}")

    if auto_open:
        webbrowser.open(f'file://{Path(html_path).absolute()}')
        print("🌐 Opening in browser...")

    return html_path


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python draft_viewer.py <draft_json_path>")
        sys.exit(1)

    draft_path = sys.argv[1]
    view_draft(draft_path)
