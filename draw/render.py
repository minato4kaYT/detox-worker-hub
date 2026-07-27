

from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from . import ddb

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
W, H = 720, 1120


def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(f"{_FONT_DIR}/{name}", size)
    except OSError:
        return ImageFont.load_default()


def _text_center(draw, cx, y, text, font, fill):
    box = draw.textbbox((0, 0), text, font=font)
    w = box[2] - box[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def _row(draw, x, y, label, value, right):
    draw.text((x, y), label, font=_font(False, 26), fill=(140, 146, 156))
    box = draw.textbbox((0, 0), value, font=_font(True, 28))
    draw.text((right - (box[2] - box[0]), y - 2), value, font=_font(True, 28), fill=(30, 33, 40))


def _watermark(img: Image.Image) -> None:

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    font = _font(True, 60)
    step_x, step_y = 360, 220
    for gy in range(-H, H * 2, step_y):
        for gx in range(-W, W * 2, step_x):
            d.text((gx, gy), " · DEMO", font=font, fill=(120, 120, 120, 70))
    layer = layer.rotate(30, resample=Image.BICUBIC, center=(W / 2, H / 2))
    img.alpha_composite(layer)


def render_receipt(kind: str, amount: float, recipient: str, sender: str = "") -> bytes:
    tpl = ddb.template(kind) or ddb.TEMPLATES["card"]
    accent = tpl["accent"]

    img = Image.new("RGBA", (W, H), (245, 247, 250, 255))
    d = ImageDraw.Draw(img)


    d.rectangle([0, 0, W, 210], fill=accent)
    _text_center(d, W / 2, 46, tpl["brand"], _font(True, 40), (255, 255, 255))
    _text_center(d, W / 2, 104, tpl["title"], _font(False, 26), (255, 255, 255))
    _text_center(d, W / 2, 150, datetime.now().strftime("%d.%m.%Y  %H:%M"),
                 _font(False, 24), (255, 255, 255))


    cx, cy, r = W / 2, 330, 66
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
    d.line([(cx - 30, cy + 2), (cx - 8, cy + 26), (cx + 34, cy - 26)],
           fill=(255, 255, 255), width=12, joint="curve")
    _text_center(d, W / 2, cy + r + 20, "Перевод выполнен", _font(True, 34), (30, 33, 40))


    unit = tpl["unit"]
    amount_str = (f"{amount:,.2f}".replace(",", " ") if unit == "TON"
                  else f"{amount:,.0f}".replace(",", " "))
    _text_center(d, W / 2, cy + r + 70, f"{amount_str} {unit}", _font(True, 64), accent)


    box_top = 620
    d.rounded_rectangle([40, box_top, W - 40, H - 140], radius=28, fill=(255, 255, 255))
    x, right = 76, W - 76
    y = box_top + 40
    rows = [
        (tpl["recipient_label"], recipient[:34] or "—"),
        ("Отправитель", (sender[:34] or "—")),
        ("Статус", "Успешно"),
        ("Комиссия", "0.00 " + unit),
        ("Идентификатор", ddb.gen_ref()),
    ]
    for label, value in rows:
        _row(d, x, y, label, value, right)
        y += 64
        d.line([(x, y - 14), (right, y - 14)], fill=(238, 240, 244), width=2)

    _text_center(d, W / 2, H - 116, "Документ сформирован автоматически",
                 _font(False, 22), (150, 156, 166))
    _text_center(d, W / 2, H - 84, "⚠️ ОБРАЗЕЦ — не является платёжным документом",
                 _font(True, 22), (200, 70, 70))

    _watermark(img)

    buf = BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()
