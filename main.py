from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

# Create a FastAPI app instance
app = FastAPI()

# Initialize Jinja2 templates
models.Base.metadata.create_all(bind=engine)
 
templates = Jinja2Templates(directory="templates")
 
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
app.mount("/lib", StaticFiles(directory="templates/lib"), name="lib")
app.mount("/js", StaticFiles(directory="templates/js"), name="js")
app.mount("/scss", StaticFiles(directory="templates/scss"), name="scss")
app.mount("/img", StaticFiles(directory="templates/img"), name="img")


# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authenticate admin user
# @app.("/admin/login")
def authenticate_admin(username: str, password: str):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.desc())
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users})

# Admin login route
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request : Request,  message: str = None):
    # if authenticate_admin(username, password):
    #     # Successful login, redirect to admin dashboard
    #     return RedirectResponse(url="/admin/dashboard")
    # else:
    #     # Invalid credentials
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return templates.TemplateResponse("admin_login.html", {"request": request, "message": message})

# from fastapi import Form

@app.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...)):
    # Authentication logic
    if username == "Arif" and password == "Arif":
        # Redirect to admin dashboard with success message
        return RedirectResponse(url="/admin/dashboard?message=Login%20successful", status_code=303)
    else:
          # Invalid credentials, redirect back to login page with error message
        return RedirectResponse(url="/admin/login?message=Invalid%20username%20or%20password", status_code=303)

# Admin dashboard route (requires authentication)
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request,  message: str = None ,  db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.asc())
    # You can add authentication logic here to ensure only authenticated admin users can access this page
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "users": users}, )

@app.get("/admin/dashboard/addnew", response_class=HTMLResponse)
async def admin_dashboard(request: Request,  message: str = None ):
    # You can add authentication logic here to ensure only authenticated admin users can access this page
    return templates.TemplateResponse("addnew.html", {"request": request, "message": message})

# User dashboard route (for demonstration)
@app.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request,  message: str = None ,  db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.asc())
    # This route can be accessed by any authenticated user
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "users": users},)

@app.get("/user/contact", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    # This route can be accessed by any authenticated user
    return templates.TemplateResponse("contact.html", {"request": request})

#Admin routes

@app.post("/add")
async def add(request: Request, name: str = Form(...), position: str = Form(...), office: str = Form(...), db: Session = Depends(get_db)):
    print(name)
    print(position)
    print(office)
    users = models.User(name=name, position=position, office=office)
    db.add(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("admin_dashboard"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/dashboard/delete/{user_id}")
async def delete(request: Request, user_id: int, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("admin_dashboard"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/dashboard/edit/{user_id}")
async def edit(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})


 
@app.post("/admin/dashboard/update/{user_id}")
async def update(request: Request, user_id: int, name: str = Form(...), position: str = Form(...), office: str = Form(...), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id == user_id).first()
    users.name = name
    users.position = position
    users.office = office
    db.commit()
    return RedirectResponse(url=app.url_path_for("admin_dashboard"), status_code=status.HTTP_303_SEE_OTHER)