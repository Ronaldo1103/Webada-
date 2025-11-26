from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 
from fastapi.responses import RedirectResponse # <-- Añadido


# ✅ Importa tus routers como deben ser
from routers import web_pages
from routers import practicante_router # Tus rutas actuales API (rostros, etc.)
from routers import admin_router  # ← ahora importamos igual que los otros


from sqlalchemy.orm import Session
from db.database import get_db # Importa tu función de inyección de dependencia
from services.practicante_service import get_dashboard_stats # La nueva función (Ahora descomentada para evitar NameError)

from db.database import create_tables

app = FastAPI(title="Bioasist API Unificada")

# ----------------------------------------------------
# ✅ SOLUCIÓN AL PROBLEMA "NOT FOUND" EN LA RAÍZ (/)
# ----------------------------------------------------
@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirige automáticamente la raíz a /web/login."""
    return RedirectResponse(url="/web/login", status_code=302)


# Nuevo Endpoint para el Dashboard
@app.get("/api/dashboard", tags=["Dashboard"])
def read_dashboard_stats(db: Session = Depends(get_db)):
    """
    Devuelve todas las estadísticas necesarias para el dashboard.
    """
    try:
        stats = get_dashboard_stats(db)
        return stats
    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {e}")

# Templates HTML
templates = Jinja2Templates(directory="templates")

# Archivos estáticos (CSS, Js, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (para tu app móvil Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ RUTAS WEB (Login, menú, panel admin) -- SE INCLUYEN PRIMERO
app.include_router(web_pages.router)


# ✅ API JSON PARA FLUTTER (registro de rostros y otros)
app.include_router(practicante_router.router)

#para los regsitro, de pracincate, etc ec
app.include_router(admin_router.router)  # ← uniforme con los demás


# Crear tablas automáticamente
create_tables()

# Ejecutar:
# uvicorn main:app --host 0.0.0.0 --port 8000
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000