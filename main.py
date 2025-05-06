from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from datetime import datetime
from datetime import date
from pydantic import BaseModel
import socket
import uvicorn

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


EMPLOYEE_CSV = "data/employeedetails.csv"
USER_CSV = "data/users.csv"
SALES_CSV = "data/sales.csv"
ATTENDANCE_CSV = "data/attendance.csv"
PRODUCTS_CSV = "data/products.csv"


if not os.path.exists("data"):
    os.makedirs("data")

for file_path, columns in {
    EMPLOYEE_CSV: ["emp_code", "name", "doj"],
    USER_CSV: ["username", "password"],
    SALES_CSV: ["date", "total_cost"],
    ATTENDANCE_CSV: ["emp_code", "date"],
}.items():
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)




@app.get("/", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "error": None})


@app.post("/login")
async def login_user(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    users = pd.read_csv(USER_CSV)

    if any((users["username"] == username) & (users["password"] == password)):
        if username.lower() == "admin":
            return RedirectResponse(url="/admindashboard", status_code=303)
        else:
            return RedirectResponse(url="/empdashboard", status_code=303)

    return templates.TemplateResponse(
        "index.html", {"request": request, "error": "Invalid username or password!"}
    )


@app.get("/admindashboard", response_class=HTMLResponse)
async def show_admin_dashboard(request: Request):
    return templates.TemplateResponse("admindashboard.html", {"request": request})


@app.get("/empdashboard", response_class=HTMLResponse)
async def show_employee_dashboard(request: Request):
    return templates.TemplateResponse("empdashboard.html", {"request": request})


@app.get("/pos", response_class=HTMLResponse)
async def show_employee_dashboard(request: Request):
    return templates.TemplateResponse("pos.html", {"request": request})


@app.get("/pg", response_class=HTMLResponse)
async def show_employee_dashboard(request: Request):
    return templates.TemplateResponse("pg.html", {"request": request})


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)





@app.get("/api/employees")
async def get_employees():
    df = pd.read_csv(EMPLOYEE_CSV)
    return df.to_dict(orient="records")



@app.post("/api/employees")
async def add_employee(
    emp_code: str = Form(...), name: str = Form(...), doj: str = Form(...)
):
    # Load employee data
    emp_df = pd.read_csv(EMPLOYEE_CSV)

    # Check if Employee Code exists
    if emp_code in emp_df["emp_code"].astype(str).values:
        return JSONResponse(
            content={"message": "Employee Code already exists"}, status_code=400
        )

    # Add new employee
    emp_df = emp_df._append(
        {"emp_code": emp_code, "name": name, "doj": doj}, ignore_index=True
    )
    emp_df.to_csv(EMPLOYEE_CSV, index=False)

    # Load user credentials data
    user_df = pd.read_csv(USER_CSV)

    # Check if username (emp_code) already exists in users.csv
    if emp_code not in user_df["username"].astype(str).values:
        new_user = pd.DataFrame([{"username": emp_code, "password": f"{emp_code}@123"}])
        user_df = pd.concat([user_df, new_user], ignore_index=True)
        user_df.to_csv(USER_CSV, index=False)

    return JSONResponse(
        content={"message": "Employee added successfully"}, status_code=201
    )


# Delete Employee
@app.delete("/api/employees/{emp_code}")
async def delete_employee(emp_code: str):
    df = pd.read_csv(EMPLOYEE_CSV)
    df = df[df["emp_code"] != emp_code]
    df.to_csv(EMPLOYEE_CSV, index=False)
    return {"message": "Employee deleted successfully"}


# ---------------------- Sales and Attendance ----------------------


@app.get("/api/today")
def fetch_today_data():
    today_str = date.today().strftime("%Y-%m-%d")

    try:
        sales_df = pd.read_csv(SALES_CSV)
        sales_df["date"] = sales_df["date"].astype(str)
        today_sales = sales_df[sales_df["date"] == today_str]
        total_sales = today_sales["total_cost"].sum() if not today_sales.empty else 0
    except FileNotFoundError:
        total_sales = 0
    try:
        attendance_df = pd.read_csv(ATTENDANCE_CSV)
        attendance_df["date"] = attendance_df["date"].astype(str)
        total_attendance = attendance_df[attendance_df["date"] == today_str].shape[0]
    except FileNotFoundError:
        total_attendance = 0

    return {
        "date": today_str,
        "total_sales": int(total_sales),
        "total_attendance": total_attendance,
    }


# ---------------------- Product List ----------------------
class Product(BaseModel):
    product_name: str
    image_address: str
    product_category: str
    product_price: float
    product_quantity: int


# Fetch all products
@app.get("/api/products")
def get_products():
    try:
        df = pd.read_csv(PRODUCTS_CSV)
        if df.empty:
            return {
                "product": [],
                "img_add": [],
                "category": [],
                "price": [],
                "quantity": [],
            }
        return {
            "product": df["product_name"].tolist(),
            "img_add": df["image_address"].tolist(),
            "category": df["product_category"].tolist(),
            "price": df["product_price"].tolist(),
            "quantity": df["product_quantity"].tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add a new product
@app.post("/api/add_product")
def add_product(product: Product):
    try:
        new_product = pd.DataFrame([product.dict()])
        new_product.to_csv(
            PRODUCTS_CSV, mode="a", header=not os.path.exists(PRODUCTS_CSV), index=False
        )
        return {"success": True, "message": "Product added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# delete product
@app.delete("/api/products/{product_name}")
async def delete_product(product_name: str):
    df = pd.read_csv(PRODUCTS_CSV)

    # Check if the product exists
    if product_name not in df["product_name"].values:
        return {"message": "Product not found"}

    # Filter out the product to delete
    df = df[df["product_name"] != product_name]
    df.to_csv(PRODUCTS_CSV, index=False)

    return {"message": "Product deleted successfully"}


# ---------------------- Sales Records ----------------------
@app.get("/api/sales")
def get_sales():
    df = pd.read_csv(SALES_CSV)
    return {
        "date": df["date"].to_list(),
        "emp_code": df["emp_code"].to_list(),
        "bill_no": df["bill_no"].to_list(),
        "total_cost": df["total_cost"].to_list(),
    }


class Sale(BaseModel):
    name: str
    amount: float
    emp_code: str
    date: str
    bill_no: int  # New field



@app.post("/api/save_sales")
async def save_sales(sale: Sale):
    if os.path.exists(SALES_CSV):
        df = pd.read_csv(SALES_CSV)
    else:
        df = pd.DataFrame(columns=["date", "emp_code", "bill_no", "total_cost"])

    new_row = {
        "date": sale.date,
        "emp_code": sale.emp_code,
        "bill_no": sale.bill_no,
        "total_cost": sale.amount,
    }

    df.loc[len(df)] = new_row
    df.to_csv(SALES_CSV, index=False)

    return {"message": "Sale saved successfully", "bill_no": sale.bill_no}


# ---------------------- Attendance Records ----------------------
@app.get("/api/attendance")
def get_attendance():
    df = pd.read_csv(ATTENDANCE_CSV)
    return {
        "date": df["date"].to_list(),
        "emp_code": df["emp_code"].to_list(),
    }


# ---------------------- Mark Attendance ---------------------------
@app.post("/mark_attendance")
async def mark_attendance(emp_code: str = Form(...)):
    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing attendance or create new DataFrame
    if os.path.exists(ATTENDANCE_CSV):
        df = pd.read_csv(ATTENDANCE_CSV)
    else:
        df = pd.DataFrame(columns=["date", "emp_code"])

    # Check if today's attendance is already marked for this emp
    if not df[(df["emp_code"] == emp_code) & (df["date"] == today)].empty:
        return JSONResponse(
            content={
                "status": "fail",
                "message": f"Attendance already marked for {emp_code} on {today}.",
            }
        )

    # Mark attendance
    new_row = {"date": today, "emp_code": emp_code}
    df.loc[len(df)] = new_row
    df.to_csv(ATTENDANCE_CSV, index=False)

    return JSONResponse(
        content={
            "status": "success",
            "message": f"Attendance marked successfully for {emp_code} on {today}.",
        }
    )


# -------------------------- New Sales Records ---------------------------


# ---------------------- Socket Connection ----------------------
if __name__ == "__main__":
    # Get local network IP reliably
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    port = 1607

    print(f"\n🚀 Project is Live!\n")
    print(f"🔗 Local:          http://127.0.0.1:{port}")
    print(f"🌍 Network:        http://{local_ip}:{port}\n")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
