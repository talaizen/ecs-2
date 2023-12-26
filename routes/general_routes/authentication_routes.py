import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.pydantic_forms import TokenResponse, LoginForm
from utils.dependecy_functions import get_mongo_db
from utils.helpers import authenticate_user, get_landing_page_url, create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 60

logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Route to serve the index.html file.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the index.html content.
    """
    logger.info("entering index.html")
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    response: Response, login_data: LoginForm, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Authenticate a user and return a redirect URL.

    This endpoint authenticates a user using their personal ID and password.
    If authentication is successful, it generates an access token, sets it in an HTTP-only cookie,
    and provides a URL to redirect the user to the appropriate landing page based on their user type.

    Args:
        response (Response): The response object used to set the cookie.
        login_data (LoginForm): A form containing the user's personal ID and password.
        mongo_db (MongoDB): The MongoDB connection instance.

    Returns:
        dict: A dictionary with a `redirect_url` key containing the URL to redirect the authenticated user.

    Raises:
        HTTPException: 401 error if authentication fails (incorrect username or password).
    """
    user = await authenticate_user(
        mongo_db, login_data.personal_id, login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.personal_id), "pwd": user.password},
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,
        samesite="Lax",
    )
    redirect_url = get_landing_page_url(user.type)

    return {"redirect_url": redirect_url}
