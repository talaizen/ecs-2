from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from forms.jason_forms import LoginForm 


app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Mount the 'templates' and 'static' folders as a static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You might want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve the index.html file
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "username": "tal", "age": 22}
    )

@app.post("/login")
async def login(login_data: LoginForm):
    # TODO: Check the username and password against MongoDB
    # If the credentials are valid, return a success response
    # Otherwise, raise an HTTPException with a 401 status code (Unauthorized)
    username = login_data.username
    password = login_data.password
    print(username, password)
    return {"message": "Login successful"}

