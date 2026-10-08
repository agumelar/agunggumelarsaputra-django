import os
import re
import sys
import json

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
APPS_DIR = os.path.join(PROJECT_ROOT, 'apps')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

report = {
    "hard_gate": {},
    "purpose_gate": {},
    "quality_locks": {},
    "ui_visual": {},
    "copywriting": {},
    "human_accessibility": {},
    "mobile_layout": {},
    "code_comments": {}
}

# ---------------------------------------------------------
# 1. HARD GATE: R-02 Em Dash (—)
# ---------------------------------------------------------
em_dashes = []
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    if '—' in line:
                        em_dashes.append({
                            "file": rel,
                            "line": idx,
                            "snippet": line.strip()
                        })

for root, _, files in os.walk(APPS_DIR):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    if '—' in line:
                        em_dashes.append({
                            "file": rel,
                            "line": idx,
                            "snippet": line.strip()
                        })

report["hard_gate"]["R-02_em_dash"] = {
    "status": "FAIL" if len(em_dashes) > 0 else "PASS",
    "count": len(em_dashes),
    "items": em_dashes
}

# ---------------------------------------------------------
# 2. HARD GATE: R-24 & R-26 Dead Links (href="#" or href="")
# ---------------------------------------------------------
dead_links = []
href_pattern = re.compile(r'href\s*=\s*["\'](#|javascript:void\(0\)|)["\']', re.IGNORECASE)
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    # Exclude alpine @click links or htmx links if they have actions
                    if href_pattern.search(line):
                        if not any(attr in line for attr in ['hx-', '@click', 'x-on:click']):
                            dead_links.append({
                                "file": rel,
                                "line": idx,
                                "snippet": line.strip()
                            })

report["hard_gate"]["R-24_R-26_dead_links"] = {
    "status": "FAIL" if len(dead_links) > 0 else "PASS",
    "count": len(dead_links),
    "items": dead_links
}

# ---------------------------------------------------------
# 3. HARD GATE & ACCESSIBILITY: R-32 Keyboard Accessibility (outline-none without focus ring)
# ---------------------------------------------------------
outline_none_without_focus = []
outline_pattern = re.compile(r'\b(outline-none|focus:outline-none)\b')
focus_visible_pattern = re.compile(r'\b(focus:ring|focus-visible:ring|focus:border|focus-visible:outline)\b')
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    if outline_pattern.search(line) and not focus_visible_pattern.search(line):
                        # Filter out non-interactive elements if any
                        if any(tag in line for tag in ['<button', '<input', '<select', '<textarea', '<a ']):
                            outline_none_without_focus.append({
                                "file": rel,
                                "line": idx,
                                "snippet": line.strip()
                            })

report["human_accessibility"]["R-32_outline_none_no_replacement"] = {
    "status": "FAIL" if len(outline_none_without_focus) > 0 else "PASS",
    "count": len(outline_none_without_focus),
    "items": outline_none_without_focus
}

# ---------------------------------------------------------
# 4. PURPOSE-GATE / UI: R-04 Emoji as Decoration in Templates
# ---------------------------------------------------------
# Range of common emojis
emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50]')
emoji_in_ui = []
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    # Check text content outside script/svg/style
                    m = emoji_pattern.findall(line)
                    if m:
                        # Exclude comments
                        clean_l = re.sub(r'<!--.*?-->', '', line).strip()
                        if clean_l and not clean_l.startswith('//') and not clean_l.startswith('/*'):
                            emoji_in_ui.append({
                                "file": rel,
                                "line": idx,
                                "emojis": list(set(m)),
                                "snippet": clean_l[:100]
                            })

report["ui_visual"]["R-04_emoji_as_decoration"] = {
    "status": "FAIL" if len(emoji_in_ui) > 0 else "PASS",
    "count": len(emoji_in_ui),
    "items": emoji_in_ui
}

# ---------------------------------------------------------
# 5. PURPOSE-GATE: R-08 Button Arrows (→, ➔, ↗)
# ---------------------------------------------------------
button_arrows = []
arrow_pattern = re.compile(r'(→|➔|↗|&rarr;|&nearr;)')
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    if arrow_pattern.search(line):
                        if any(k in line for k in ['<button', '<a ', 'm3-btn', 'btn']):
                            button_arrows.append({
                                "file": rel,
                                "line": idx,
                                "snippet": line.strip()[:100]
                            })

report["ui_visual"]["R-08_button_arrows"] = {
    "status": "FAIL" if len(button_arrows) > 0 else "PASS",
    "count": len(button_arrows),
    "items": button_arrows
}

# ---------------------------------------------------------
# 6. PURPOSE-GATE: R-10 Excessive Glassmorphism (backdrop-blur)
# ---------------------------------------------------------
glass_elements = []
glass_pattern = re.compile(r'backdrop-blur(-[a-z0-9]+)?')
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                file_glass = 0
                for idx, line in enumerate(fp, 1):
                    if glass_pattern.search(line):
                        file_glass += 1
                        glass_elements.append({
                            "file": rel,
                            "line": idx,
                            "snippet": line.strip()[:100]
                        })

report["ui_visual"]["R-10_glassmorphism"] = {
    "status": "FAIL" if len(glass_elements) > 15 else "PASS",
    "count": len(glass_elements),
    "items": glass_elements
}

# ---------------------------------------------------------
# 7. QUALITY LOCKS: R-15 Generic CTAs & R-16 AI Buzzwords
# ---------------------------------------------------------
generic_ctas = ["get started", "learn more", "try now", "pelajari selengkapnya", "mulai sekarang", "klik disini", "click here"]
buzzwords = ["ai powered", "next generation", "next-gen", "revolutionary", "revolusioner", "seamless", "cutting edge", "cutting-edge", "game-changer", "canggih"]

cta_hits = []
buzzword_hits = []

for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    lower = line.lower()
                    for cta in generic_ctas:
                        if re.search(r'\b' + re.escape(cta) + r'\b', lower):
                            cta_hits.append({
                                "file": rel,
                                "line": idx,
                                "matched": cta,
                                "snippet": line.strip()[:100]
                            })
                    for bw in buzzwords:
                        if re.search(r'\b' + re.escape(bw) + r'\b', lower):
                            buzzword_hits.append({
                                "file": rel,
                                "line": idx,
                                "matched": bw,
                                "snippet": line.strip()[:100]
                            })

report["copywriting"]["R-15_generic_ctas"] = {
    "status": "FAIL" if len(cta_hits) > 0 else "PASS",
    "count": len(cta_hits),
    "items": cta_hits
}

report["copywriting"]["R-16_buzzwords"] = {
    "status": "FAIL" if len(buzzword_hits) > 0 else "PASS",
    "count": len(buzzword_hits),
    "items": buzzword_hits
}

# ---------------------------------------------------------
# 8. CODE COMMENTS: antislop-code Hygiene
# ---------------------------------------------------------
# Decorative separators: // ===, # ---, etc.
separator_pattern = re.compile(r'(//|#|\/\*)\s*([=\-~*#_]{5,})')
obvious_comment_pattern = re.compile(r'#( Create | Helper | Step \d| Get | Set | Return | Render | Import )', re.IGNORECASE)
code_comment_hits = []

for root, _, files in os.walk(APPS_DIR):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    s = line.strip()
                    if separator_pattern.search(s):
                        code_comment_hits.append({
                            "file": rel,
                            "line": idx,
                            "type": "decorative_separator",
                            "snippet": s[:80]
                        })
                    elif obvious_comment_pattern.search(s):
                        code_comment_hits.append({
                            "file": rel,
                            "line": idx,
                            "type": "restating_obvious",
                            "snippet": s[:80]
                        })

# Check javascript / templates comments
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    s = line.strip()
                    if separator_pattern.search(s):
                        code_comment_hits.append({
                            "file": rel,
                            "line": idx,
                            "type": "decorative_separator",
                            "snippet": s[:80]
                        })

report["code_comments"]["antislop_code"] = {
    "status": "FAIL" if len(code_comment_hits) > 0 else "PASS",
    "count": len(code_comment_hits),
    "items": code_comment_hits
}

# ---------------------------------------------------------
# 9. HUMAN & CONTRAST: Hardcoded low-contrast classes (text-gray-400 / text-gray-500)
# ---------------------------------------------------------
low_contrast_classes = []
lc_pattern = re.compile(r'\b(text-gray-400|text-gray-300|text-slate-400|text-zinc-400)\b')
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PROJECT_ROOT)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    # Check if line does not have dark: variant for text-gray
                    if lc_pattern.search(line):
                        if 'dark:text-' not in line and 'dark' not in line:
                            low_contrast_classes.append({
                                "file": rel,
                                "line": idx,
                                "snippet": line.strip()[:100]
                            })

report["human_accessibility"]["contrast_low_classes"] = {
    "status": "FAIL" if len(low_contrast_classes) > 0 else "PASS",
    "count": len(low_contrast_classes),
    "items": low_contrast_classes
}

# ---------------------------------------------------------
# Output Summary
# ---------------------------------------------------------
output_json_path = os.path.join(PROJECT_ROOT, 'scripts', 'audit_result.json')
with open(output_json_path, 'w', encoding='utf-8') as fp:
    json.dump(report, fp, indent=2)

print("=== AUDIT SUMMARY ===")
print(f"1. R-02 Em Dash (—): {report['hard_gate']['R-02_em_dash']['count']} temuan (Status: {report['hard_gate']['R-02_em_dash']['status']})")
print(f"2. R-24/R-26 Dead Links: {report['hard_gate']['R-24_R-26_dead_links']['count']} temuan (Status: {report['hard_gate']['R-24_R-26_dead_links']['status']})")
print(f"3. R-32 Keyboard Accessibility (outline-none): {report['human_accessibility']['R-32_outline_none_no_replacement']['count']} temuan")
print(f"4. R-04 Emoji as Decoration in UI: {report['ui_visual']['R-04_emoji_as_decoration']['count']} baris mengandung emoji")
print(f"5. R-08 Button Arrows (→, ➔, ↗): {report['ui_visual']['R-08_button_arrows']['count']} temuan")
print(f"6. R-10 Glassmorphism: {report['ui_visual']['R-10_glassmorphism']['count']} kemunculan backdrop-blur")
print(f"7. R-15 Generic CTAs: {report['copywriting']['R-15_generic_ctas']['count']} temuan")
print(f"8. R-16 AI Buzzwords: {report['copywriting']['R-16_buzzwords']['count']} temuan")
print(f"9. Code Comments Hygiene: {report['code_comments']['antislop_code']['count']} temuan (banner separators / obvious restatements)")
print(f"10. Accessibility / Low Contrast Risks: {report['human_accessibility']['contrast_low_classes']['count']} baris tanpa dark mode token")
print(f"Laporan lengkap tersimpan di: {output_json_path}")
