import qrcode
from io import BytesIO
import base64
import os
from datetime import datetime

def generate_qr_code(restaurant_id: int) -> str:
    """
    Generate QR code.
    First tries to save as file (for local development).
    If fails (e.g. on Vercel), falls back to base64 string.
    Returns: file path (if saved) or base64 data URL
    """
    
    # Data that will be encoded in QR code
    qr_data = f"https://ar-menu-nextjs.vercel.app/restaurant/{restaurant_id}"  # ← Change to your real frontend URL

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # ====================== TRY TO SAVE AS FILE FIRST ======================
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/qrcodes"
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"restaurant_{restaurant_id}_qr.png"
        filepath = os.path.join(upload_dir, filename)

        img.save(filepath)
        
        # Return relative path (you can serve it later if needed)
        return f"/uploads/qrcodes/{filename}"
        
    except Exception as e:
        # If saving fails (most likely on Vercel), fallback to Base64
        print(f"File save failed: {e}. Falling back to Base64.")
        
        # ====================== FALLBACK: BASE64 ======================
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return f"data:image/png;base64,{img_str}"
