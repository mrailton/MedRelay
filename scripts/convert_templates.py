#!/usr/bin/env python3
"""Convert Laravel Blade templates to Jinja2."""

import re
import sys
from pathlib import Path

BLADE_ROOT = Path(__file__).resolve().parents[2].parent / "MedRelay" / "resources" / "views"
OUT_ROOT = Path(__file__).resolve().parents[1] / "src" / "medrelay" / "templates"


def convert(content: str) -> str:
    content = re.sub(r"@extends\('([^']+)'\)", r'{% extends "\1" %}', content)
    content = re.sub(r'@extends\("([^"]+)"\)', r'{% extends "\1" %}', content)
    content = content.replace("layouts.app", "layouts/app.html")
    content = re.sub(r"@section\('([^']+)',\s*'([^']*)'\)", r'{% block \1 %}\2{% endblock %}', content)
    content = re.sub(r"@section\('([^']+)'\)", r"{% block \1 %}", content)
    content = content.replace("@endsection", "{% endblock %}")
    content = content.replace("@yield('content')", "{% block content %}{% endblock %}")
    content = re.sub(r"@csrf", '<input type="hidden" name="csrf_token" value="{{ csrf_token }}">', content)
    content = re.sub(
        r"@can\('([^']+)',\s*App\\Models\\(\w+)::class\)",
        r"{% if can(user, '\1', '\2'|lower) %}",
        content,
    )
    content = re.sub(
        r"@can\('admin-only'\)",
        r"{% if can(user, 'admin-only') %}",
        content,
    )
    content = content.replace("@endcan", "{% endif %}")
    content = re.sub(r"\{\{\s*route\('([^']+)'\)\s*\}\}", r"{{ url_for('\1') }}", content)
    content = re.sub(
        r"\{\{\s*route\('([^']+)',\s*\$([^)]+)\)\s*\}\}",
        r"{{ url_for('\1', \2=\2) }}",
        content,
    )
    content = re.sub(
        r"\{\{\s*route\('([^']+)',\s*([^)]+)\)\s*\}\}",
        lambda m: f"{{{{ url_for('{m.group(1)}', **resolve_route_params({m.group(2)})) }}}}",
        content,
    )
    # route with model: route('events.show', $event) -> url_for('events.show', event_id=event.id)
    content = re.sub(
        r"route\('([^']+)',\s*\$(\w+)\)",
        lambda m: f"url_for('{m.group(1)}', {m.group(2)}_id={m.group(2)}.id if hasattr({m.group(2)}, 'id') else {m.group(2)})",
        content,
    )
    content = content.replace("{{ $", "{{ ")
    content = content.replace("$", "")
    content = re.sub(r"@if\s*\(", "{% if ", content)
    content = content.replace("@endif", "{% endif %}")
    content = re.sub(r"@foreach\s*\(", "{% for ", content)
    content = content.replace("@endforeach", "{% endfor %}")
    content = re.sub(r"@forelse\s*\(", "{% for ", content)
    content = content.replace("@empty", "{% else %}")
    content = content.replace("@endforelse", "{% endfor %}")
    content = re.sub(r"@error\('([^']+)'\)", r"{% if errors.get('\1') %}", content)
    content = content.replace("@enderror", "{% endif %}")
    content = re.sub(r"@push\('([^']+)'\)", r"{% block \1 %}{% endblock %}", content)
    content = content.replace("@stack('scripts')", "{% block scripts %}{% endblock %}")
    content = content.replace("@stack('modals')", "{% block modals %}{% endblock %}")
    content = re.sub(
        r"<x-([\w.-]+)([^/]*)/>",
        lambda m: f'{{% include "components/{m.group(1).replace(".", "/")}.html" {m.group(2)} %}}',
        content,
    )
    content = re.sub(
        r"<x-([\w.-]+)([^>]*)>",
        lambda m: f'{{% include "components/{m.group(1).replace(".", "/")}.html" {m.group(2)} %}}',
        content,
    )
    content = content.replace("@vite", "{# vite assets in layout #}")
    content = content.replace("{{ old('email') }}", "{{ email or '' }}")
    content = content.replace("{{ $message }}", "{{ errors.email }}")
    content = re.sub(
        r"App\\Enums\\(\w+)::cases\(\)",
        r"\1",
        content,
    )
    content = re.sub(
        r"@foreach\s*\((\w+)::cases\(\)",
        r"{% for type in \1 %}",
        content,
    )
    return content


def main() -> None:
    if not BLADE_ROOT.exists():
        print(f"Blade root not found: {BLADE_ROOT}", file=sys.stderr)
        sys.exit(1)
    for blade in BLADE_ROOT.rglob("*.blade.php"):
        rel = blade.relative_to(BLADE_ROOT)
        out = OUT_ROOT / str(rel).replace(".blade.php", ".html")
        out.parent.mkdir(parents=True, exist_ok=True)
        text = blade.read_text()
        out.write_text(convert(text))
        print(f"Converted {rel} -> {out.relative_to(OUT_ROOT)}")


if __name__ == "__main__":
    main()
