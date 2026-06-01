# -*- coding: utf-8 -*-
"""一维码（Code 128）生成与打印模块。

- 生成：使用 python-barcode + Pillow，输出 PNG 图片，条码下方自带可读文字。
- 打印：生成自包含的 HTML 打印页（图片以 base64 内嵌），用默认浏览器打开并
  自动调起打印对话框。该方案跨平台、支持「单张/批量」标签排版，最稳妥；
  另在 Windows 下提供直接发送图片到默认打印机的备选方法。
"""

import os
import sys
import base64
import webbrowser

from app import config, i18n

# 条码依赖为可选项：缺失时界面会给出友好提示而非崩溃
try:
    import barcode
    from barcode.writer import ImageWriter
    HAS_BARCODE = True
except Exception:
    HAS_BARCODE = False


def generate_barcode_image(code):
    """生成单个条码 PNG，返回图片路径。"""
    if not HAS_BARCODE:
        raise RuntimeError(i18n.T("barcode_dep_missing"))
    settings = config.load_settings()
    options = {
        "module_height": float(settings.get("barcode_module_height", 12.0)),
        "font_size": int(settings.get("barcode_font_size", 10)),
        "text_distance": 3.0,
        "quiet_zone": 2.0,
        "dpi": 300,  # 高 DPI 保证打印清晰、扫码枪易识别
    }
    path_no_ext = os.path.join(config.BARCODE_DIR, code)
    obj = barcode.get("code128", code, writer=ImageWriter())
    # save() 会自动补上 .png 扩展名并返回完整路径
    return obj.save(path_no_ext, options=options)


def _img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


# HTML 打印页样式（独立字符串，避免与 f-string 大括号冲突）
_PRINT_CSS = """
* { box-sizing: border-box; }
body { font-family: 'Microsoft YaHei','PingFang SC',sans-serif; margin: 8mm; }
h2 { font-size: 14px; }
.sheet { display: flex; flex-wrap: wrap; gap: 6mm; }
.label {
    border: 1px dashed #bbb; padding: 4mm 5mm; text-align: center;
    width: 60mm; page-break-inside: avoid;
}
.label .meta { font-size: 12px; color: #333; margin-bottom: 2mm; }
.label img { width: 100%; height: auto; }
.label .code { font-size: 13px; letter-spacing: 1px; margin-top: 1mm; }
@media print { .label { border: 1px solid #ddd; } }
"""


def build_print_sheet(items, title="Barcode"):
    """根据 items 生成 HTML 打印页并用浏览器打开（自动弹出打印对话框）。

    items: [{barcode, name, group_label, subject_id, image_path}, ...]
    """
    cells = []
    for it in items:
        b64 = _img_to_base64(it["image_path"])
        meta = "%s ｜ %s ｜ %s" % (
            it.get("subject_id", ""), it.get("name", ""), it.get("group_label", ""))
        cells.append(
            '<div class="label"><div class="meta">%s</div>'
            '<img src="data:image/png;base64,%s" />'
            '<div class="code">%s</div></div>'
            % (meta, b64, it.get("barcode", ""))
        )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'><title>%s</title>"
        "<style>%s</style></head><body onload='window.print()'>"
        "<h2>%s</h2><div class='sheet'>%s</div></body></html>"
        % (title, _PRINT_CSS, title, "".join(cells))
    )
    out = os.path.join(config.EXPORT_DIR, "print_sheet.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("file://" + os.path.abspath(out))
    return out


def print_subjects(subjects):
    """为受试者列表生成条码并打开打印页。subjects 为受试者 dict 列表。"""
    if not HAS_BARCODE:
        raise RuntimeError(i18n.T("barcode_dep_missing"))
    items = []
    for s in subjects:
        img = generate_barcode_image(s["barcode"])
        items.append({
            "barcode": s["barcode"],
            "name": s.get("name", ""),
            "subject_id": s.get("subject_id", ""),
            "group_label": i18n.group_label(s.get("group_type", "")),
            "image_path": img,
        })
    return build_print_sheet(items, title=i18n.T("btn_print_barcode"))


def print_image_windows(image_path):
    """Windows 下将图片直接发送到默认打印机（备选方案）。"""
    if sys.platform.startswith("win"):
        os.startfile(image_path, "print")  # type: ignore[attr-defined]
        return True
    return False
