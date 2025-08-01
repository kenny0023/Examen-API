from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import base64

app = FastAPI()

posts = []

class Post(BaseModel):
    author: str
    title: str
    content: str
    creation_datetime: datetime

# Q1: Création du route GET /ping qui retourne "pong" en tant que texte brute
@app.get("/ping", response_class=PlainTextResponse)
async def ping():
    return "pong"

# Q2: Création du route GET /home qui retourne une page
#  HTML contenant "Welcome home!"
@app.get("/home", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home</title>
    </head>
    <body>
        <h1>Welcome home!</h1>
    </body>
    </html>
    """

# Q3: Configuration de l'application pour que cela retourne une page
#  HTML contenant "404 NOT FOUND"
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 Not Found</title>
        </head>
        <body>
            <h1>404 NOT FOUND</h1>
        </body>
        </html>
        """,
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Q4: Création du route POST /posts qui retourne une liste d’objet JSON
@app.post("/posts", status_code=201)
async def create_posts(new_posts: List[Post]):
    global posts
    posts.extend(new_posts)
    return posts

# Q5: Création du route GET /posts - Return all posts in memory
# t qui retourne le contenu de la liste
# d’objets posts actuellement stockés en mémoire avec un code de status 200 OK
@app.get("/posts")
async def get_posts():
    return posts

# Q6: Création d'une requête idempotente à travers une nouvelle route PUT /posts
@app.put("/posts")
async def update_posts(new_posts: List[Post]):
    global posts
    for new_post in new_posts:
        existing_post_index = next((i for i, post in enumerate(posts) if post.title == new_post.title), -1)
        if existing_post_index != -1:
            # Update existing post if any field is different
            if posts[existing_post_index].dict() != new_post.dict():
                posts[existing_post_index] = new_post
        else:
            # Add new post
            posts.append(new_post)
    return posts

# BONUS
@app.get("/ping/auth", response_class=PlainTextResponse)
async def ping_auth(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"Content-Type": "text/plain"})
    
    if not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme", headers={"Content-Type": "text/plain"})
    
    base64_credentials = authorization.split(" ")[1]
    try:
        credentials = base64.b64decode(base64_credentials).decode("ascii")
        username, password = credentials.split(":")
        if username == "admin" and password == "123456":
            return "pong"
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials", headers={"Content-Type": "text/plain"})
    except:
        raise HTTPException(status_code=401, detail="Invalid credentials format", headers={"Content-Type": "text/plain"})


# s'il vous plait, est ce que quelqu'un sait comment désactivere simplewall