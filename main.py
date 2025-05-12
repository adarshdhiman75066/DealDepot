from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from datetime import datetime, date
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Data Paths ----------------------
EMPLOYEE_CSV = "data/employeedetails.csv"
USER_CSV = "data/users.csv"
SALES_CSV = "data/sales.csv"
ATTENDANCE_CSV = "data/attendance.csv"
PRODUCTS_CSV = "data/products.csv"

# ---------------------- Ensure CSV files ----------------------
if not os.path.exists("data"):
    os.makedirs("data")

for file_path, columns in {
    EMPLOYEE_CSV: ["emp_code", "name", "doj"],
    USER_CSV: ["username", "password"],
    SALES_CSV: ["date", "emp_code", "bill_no", "total_cost"],
    ATTENDANCE_CSV: ["emp_code", "date"],
    PRODUCTS_CSV: ["product_name", "image_address", "product_category", "product_price", "product_quantity"]
}.items():
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)

# ---------------------- Routes ----------------------

@app.get("/", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "error": None})

@app.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    users = pd.read_csv(USER_CSV)
    if any((users["username"] == username) & (users["password"] == password)):
        return RedirectResponse(url="/admindashboard" if username.lower() == "admin" else "/empdashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid username or password!"})

@app.get("/admindashboard", response_class=HTMLResponse)
async def show_admin_dashboard(request: Request):
    return templates.TemplateResponse("admindashboard.html", {"request": request})

@app.get("/empdashboard", response_class=HTMLResponse)
async def show_employee_dashboard(request: Request):
    return templates.TemplateResponse("empdashboard.html", {"request": request})

@app.get("/pos", response_class=HTMLResponse)
async def show_pos(request: Request):
    return templates.TemplateResponse("pos.html", {"request": request})

@app.get("/pg", response_class=HTMLResponse)
async def show_pg(request: Request):
    return templates.TemplateResponse("pg.html", {"request": request})

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# ---------------------- API: Employees ----------------------
@app.get("/api/employees")
async def get_employees():
    return pd.read_csv(EMPLOYEE_CSV).to_dict(orient="records")

@app.post("/api/employees")
async def add_employee(emp_code: str = Form(...), name: str = Form(...), doj: str = Form(...)):
    emp_df = pd.read_csv(EMPLOYEE_CSV)
    if emp_code in emp_df["emp_code"].astype(str).values:
        return JSONResponse({"message": "Employee Code already exists"}, status_code=400)
    emp_df = emp_df._append({"emp_code": emp_code, "name": name, "doj": doj}, ignore_index=True)
    emp_df.to_csv(EMPLOYEE_CSV, index=False)
    
    user_df = pd.read_csv(USER_CSV)
    if emp_code not in user_df["username"].astype(str).values:
        user_df = pd.concat([user_df, pd.DataFrame([{"username": emp_code, "password": f"{emp_code}@123"}])], ignore_index=True)
        user_df.to_csv(USER_CSV, index=False)

    return JSONResponse({"message": "Employee added successfully"}, status_code=201)

@app.delete("/api/employees/{emp_code}")
async def delete_employee(emp_code: str):
    df = pd.read_csv(EMPLOYEE_CSV)
    df = df[df["emp_code"] != emp_code]
    df.to_csv(EMPLOYEE_CSV, index=False)
    return {"message": "Employee deleted successfully"}

# ---------------------- Attendance + Sales ----------------------
@app.get("/api/today")
def fetch_today_data():
    today_str = date.today().strftime("%Y-%m-%d")
    try:
        total_sales = pd.read_csv(SALES_CSV).query("date == @today_str")["total_cost"].sum()
    except:
        total_sales = 0
    try:
        total_attendance = pd.read_csv(ATTENDANCE_CSV).query("date == @today_str").shape[0]
    except:
        total_attendance = 0
    return {"date": today_str, "total_sales": int(total_sales), "total_attendance": total_attendance}

# ---------------------- Products ----------------------
class Product(BaseModel):
    product_name: str
    image_address: str
    product_category: str
    product_price: float
    product_quantity: int

@app.get("/api/products")
def get_products():
    df = pd.read_csv(PRODUCTS_CSV)
    return {
        "product": df["product_name"].tolist(),
        "img_add": df["image_address"].tolist(),
        "category": df["product_category"].tolist(),
        "price": df["product_price"].tolist(),
        "quantity": df["product_quantity"].tolist(),
    }

@app.post("/api/add_product")
def add_product(product: Product):
    pd.DataFrame([product.dict()]).to_csv(PRODUCTS_CSV, mode="a", header=not os.path.exists(PRODUCTS_CSV), index=False)
    return {"success": True, "message": "Product added successfully!"}

@app.delete("/api/products/{product_name}")
async def delete_product(product_name: str):
    df = pd.read_csv(PRODUCTS_CSV)
    if product_name not in df["product_name"].values:
        return {"message": "Product not found"}
    df = df[df["product_name"] != product_name]
    df.to_csv(PRODUCTS_CSV, index=False)
    return {"message": "Product deleted successfully"}

# ---------------------- Sales ----------------------
@app.get("/api/sales")
def get_sales():
    df = pd.read_csv(SALES_CSV)
    return df.to_dict(orient="list")

class Sale(BaseModel):
    name: str
    amount: float
    emp_code: str
    date: str
    bill_no: int

@app.post("/api/save_sales")
async def save_sales(sale: Sale):
    df = pd.read_csv(SALES_CSV) if os.path.exists(SALES_CSV) else pd.DataFrame(columns=["date", "emp_code", "bill_no", "total_cost"])
    df.loc[len(df)] = {
        "date": sale.date,
        "emp_code": sale.emp_code,
        "bill_no": sale.bill_no,
        "total_cost": sale.amount,
    }
    df.to_csv(SALES_CSV, index=False)
    return {"message": "Sale saved successfully", "bill_no": sale.bill_no}

# ---------------------- Attendance ----------------------
@app.get("/api/attendance")
def get_attendance():
    df = pd.read_csv(ATTENDANCE_CSV)
    return df.to_dict(orient="list")

@app.post("/mark_attendance")
async def mark_attendance(emp_code: str = Form(...)):
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_csv(ATTENDANCE_CSV) if os.path.exists(ATTENDANCE_CSV) else pd.DataFrame(columns=["date", "emp_code"])
    if not df[(df["emp_code"] == emp_code) & (df["date"] == today)].empty:
        return JSONResponse(
            {"status": "fail", "message": f"Attendance already marked for {emp_code} on {today}."}
        )
    df.loc[len(df)] = {"date": today, "emp_code": emp_code}
    df.to_csv(ATTENDANCE_CSV, index=False)
    return JSONResponse(
        {"status": "success", "message": f"Attendance marked successfully for {emp_code} on {today}."}
    )
