import os

import qrcode
from PIL import Image

from ..config import settings


def generate_qr_code(restaurant_id: int) -> str:
    """Generate a QR code pointing to the customer-facing menu URL."""
    menu_url = f"{settings.FRONTEND_URL}/menu/{restaurant_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(menu_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e1b4b", back_color="white")

    qr_dir = os.path.join(settings.UPLOAD_DIR, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"restaurant_{restaurant_id}_qr.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)

    return f"/uploads/qrcodes/{filename}"
