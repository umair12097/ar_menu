# Fix Image & 3D Model URLs — Backend Returns Full URLs, Frontend Handles Correctly

## Goal
Fix restaurant logo, menu images, and 3D models so they display correctly both locally and when deployed.

## Root Cause
The backend stores **relative paths** like `/uploads/logos/xxx.jfif`. The frontend prepends `API_URL` (`http://localhost:8000`) to build full URLs. When deployed on Vercel, `localhost:8000` is unreachable.

## Changes (4 steps)

### 1. Backend — `app/routers/upload.py`
**File:** `C:\Users\Hp\ar_menu\app\routers\upload.py:175-185`

Update `_get_file_url` to return full URLs using `settings.BASE_URL`:

```python
async def _get_file_url(file: UploadFile, directory: str, url_path: str) -> str:
    filename = await _save_file(file, directory)
    if filename:
        return f"{settings.BASE_URL}{url_path}/{filename}"  # ← prepend settings.BASE_URL
    # Last resort: base64
    print(f"[WARNING] Disk save failed, using base64 for {file.filename}")
    return await _to_base64(file)
```

Add `from ..config import settings` import (check if already imported).

### 2. Frontend — `lib/api.ts`
**File:** `C:\Users\Hp\ar_menu_nextjs\lib\api.ts`

Add a helper function after `API_URL` definition:

```typescript
export function getFullUrl(url?: string): string | undefined {
  if (!url) return undefined;
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) return url;
  return `${API_URL}${url}`;
}
```

### 3. Frontend — `app/menu/[restaurantId]/page.tsx`
**File:** `C:\Users\Hp\ar_menu_nextjs\app\menu\[restaurantId]\page.tsx`

Import `getFullUrl` from `@/lib/api`. Replace all ~6 image/model source occurrences:
- Line 81: `src={`${API_URL}${item.model_3d_url}`}` → `src={getFullUrl(item.model_3d_url)}`
- Line 82: `poster={item.image_url ? `${API_URL}${item.image_url}` : undefined}` → `poster={getFullUrl(item.image_url)}`
- Line 90: `src={`${API_URL}${item.image_url}`}` → `src={getFullUrl(item.image_url)}`
- Line ~205 (cart): replace `API_URL` prefix
- Line ~313 (card): replace `API_URL` prefix
- Line ~501 (logo): replace `API_URL` prefix

### 4. Database — Fix Existing Records
Run Python script to update existing records with relative paths:

```python
from app.database import SessionLocal
from app.models import MenuItem, Restaurant
from app.config import settings

db = SessionLocal()
for item in db.query(MenuItem).filter(MenuItem.image_url.like("/uploads/%")).all():
    item.image_url = f"{settings.BASE_URL}{item.image_url}"
for item in db.query(MenuItem).filter(MenuItem.model_3d_url.like("/uploads/%")).all():
    item.model_3d_url = f"{settings.BASE_URL}{item.model_3d_url}"
for r in db.query(Restaurant).filter(Restaurant.logo_url.like("/uploads/%")).all():
    r.logo_url = f"{settings.BASE_URL}{r.logo_url}"
db.commit()
db.close()
```

## Verification
1. Upload new menu item with image + 3D model
2. Check API returns full URLs in `image_url`, `model_3d_url`, `logo_url`
3. Open menu page — images and 3D models display correctly