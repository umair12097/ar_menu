<<<<<<< HEAD
# AR Menu — Backend (FastAPI)

## Requirements
- Python 3.11+
- PostgreSQL 14+

## Setup

### 1. Create & activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

Edit `.env` and set:
```
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/ar_menu_db
SECRET_KEY=<generate a long random string>
FRONTEND_URL=http://localhost:3000
```

### 4. Create the database
```sql
CREATE DATABASE ar_menu_db;
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

## Project Structure
```
app/
├── main.py          # FastAPI app entry point & startup
├── config.py        # Settings via pydantic-settings
├── database.py      # SQLAlchemy engine & session
├── models.py        # ORM models (User, Restaurant, MenuItem, Order, …)
├── schemas.py       # Pydantic request/response schemas
├── routers/
│   ├── auth.py      # POST /auth/register  POST /auth/login  GET /auth/me
│   ├── restaurants.py
│   ├── menu.py
│   ├── orders.py
│   └── upload.py
└── utils/
    ├── auth.py          # JWT & password helpers
    └── qr_generator.py  # QR code generation
```

## 3D Model Support (AR)
Upload `.glb` or `.gltf` files per menu item via:
```
POST /upload/model/menu-item/{item_id}
```
Models are served statically from the `uploads/models/` directory and
rendered client-side with Google's `<model-viewer>` web component.
=======
# ar_menu
>>>>>>> 5d41e9fceaecce3d05c0013ac7f5787ee45a00ea
