from PIL import Image
import math

SRC = "myimage.png"   # ชื่อไฟล์ต้นฉบับ
PAD = 8               # เผื่อขอบตอนครอป

# ระดับความกว้างแนวนอน
width_variants = {
    "very_narrow": 0.60,
    "narrow":      0.80,
    "medium":      1.00,
    "wide":        1.25
}

im0 = Image.open(SRC).convert("RGBA")
w0, h0 = im0.size

# พารามิเตอร์ isometric
scale_y = math.cos(math.radians(30))   # ≈ 0.866 (ย่อแกนตั้ง)
k = math.tan(math.radians(30))         # ≈ 0.577 (shear factor)

def autocrop_rgba(img, pad=0):
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(img.width,  x1 + pad); y1 = min(img.height, y1 + pad)
    return img.crop((x0, y0, x1, y1))

# แนวตั้ง: เอียงขึ้น/ลง
def shear_y_up(img, k):
    # y' = y + k*x  → inverse for PIL: y_in = y_out - k*x_out
    new_w = img.width
    new_h = int(round(img.height + k * img.width))
    a, b, c = 1, 0, 0
    d, e, f = -k, 1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, PAD)

def shear_y_down(img, k):
    # y' = y - k*x + offset, offset = k*w
    new_w = img.width
    offset = int(round(k * img.width))
    new_h = img.height + offset
    a, b, c = 1, 0, 0
    d, e, f = k, 1, -offset   # inverse: y_in = k*x_out + y_out - offset
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, PAD)

# แนวนอน: เอียงซ้าย/ขวา
def shear_x_right(img, k):
    # x' = x + k*y  → inverse: x_in = x_out - k*y_out
    new_w = int(round(img.width + k * img.height))
    new_h = img.height
    a, b, c = 1, -k, 0
    d, e, f = 0,  1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, PAD)

def shear_x_left(img, k):
    # x' = x - k*y + offset, offset = k*h
    offset = int(round(k * img.height))
    new_w = img.width + offset
    new_h = img.height
    a, b, c = 1, k, -offset   # inverse: x_in = k*y_out + x_out - offset
    d, e, f = 0, 1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, PAD)

for label, sx in width_variants.items():
    # 1) ปรับความกว้างแกน X ตามระดับ
    w1 = max(1, int(round(w0 * sx)))
    h1 = h0
    im_xscaled = im0.resize((w1, h1), Image.BICUBIC)

    # 2) ย่อแกนตั้งตาม isometric
    h_iso = max(1, int(round(h1 * scale_y)))
    im_iso = im_xscaled.resize((w1, h_iso), Image.BICUBIC)

    # 3) เอียงขึ้น/ลง
    up_img = shear_y_up(im_iso, k)
    dn_img = shear_y_down(im_iso, k)
    up_img.save(f"isometric_up_{label}.png")
    dn_img.save(f"isometric_down_{label}.png")

    # 4) เอียงซ้าย/ขวา
    left_img  = shear_x_left(im_iso, k)
    right_img = shear_x_right(im_iso, k)
    left_img.save(f"isometric_left_{label}.png")
    right_img.save(f"isometric_right_{label}.png")

    # 5) แนวนอน + หมุนทวนเข็ม 30° (anticlockwise 30°)
    left_rot  = autocrop_rgba(left_img.rotate(30, resample=Image.BICUBIC, expand=True), PAD)
    right_rot = autocrop_rgba(right_img.rotate(30, resample=Image.BICUBIC, expand=True), PAD)
    left_rot.save(f"isometric_left_ccw30_{label}.png")
    right_rot.save(f"isometric_right_ccw30_{label}.png")

print("Saved files for up/down/left/right and left/right+CCW30 for all width variants.")
