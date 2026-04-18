import qrcode
from io import BytesIO
import base64
import os

def generate_qr_code(restaurant_id: int) -> str:
    """
    Generate QR code as base64 data URL.
    On Vercel filesystem is ephemeral, so base64 is the reliable approach.
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

    # ====================== BASE64 (works reliably on Vercel) ======================
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
