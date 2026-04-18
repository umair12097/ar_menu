import qrcode
from io import BytesIO
import base64
import os

def generate_qr_code(restaurant_id: int) -> str:
    """
    Generate QR code.
    Tries /tmp first (Vercel), then local uploads/, then falls back to base64.
    Returns: file path (if saved) or base64 data URL
    """

    qr_data = f"https://ar-menu-nextjs.vercel.app/restaurant/{restaurant_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"restaurant_{restaurant_id}_qr.png"

    # ====================== TRY /tmp FIRST (Vercel writable) ======================
    try:
        tmp_dir = "/tmp/uploads/qrcodes"
        os.makedirs(tmp_dir, exist_ok=True)
        filepath = os.path.join(tmp_dir, filename)
        img.save(filepath)
        print(f"QR saved to /tmp: {filepath}")
        return f"/uploads/qrcodes/{filename}"
    except Exception as e:
        print(f"/tmp save failed: {e}. Trying local uploads dir...")

    # ====================== TRY LOCAL uploads/ (local dev) ======================
    try:
        local_dir = "uploads/qrcodes"
        os.makedirs(local_dir, exist_ok=True)
        filepath = os.path.join(local_dir, filename)
        img.save(filepath)
        print(f"QR saved locally: {filepath}")
        return f"/uploads/qrcodes/{filename}"
    except Exception as e:
        print(f"Local save failed: {e}. Falling back to Base64.")

    # ====================== FALLBACK: BASE64 ======================
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
