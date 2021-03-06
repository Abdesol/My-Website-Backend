from typing import ContextManager, Dict
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pony.thirdparty.compiler.ast import List
from pydantic.main import BaseModel
from starlette import responses
from starlette.responses import FileResponse, HTMLResponse
from models import Blog, Certificate, Project
from pony.orm import *
from slugify import slugify
import datetime
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, UploadFile
import os
import random
import string
from fastapi import Body
import json
from decouple import config
from zipfile import ZipFile


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

username = config("admin_username")
password = config("admin_password")
security = HTTPBasic()
async def authorize(credentials: HTTPBasicCredentials):
    if credentials.username == username and credentials.password == password:
        return True
    else:
        return False

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def main(request:Request):
    aboutme_ = open("Database/aboutme.txt", "r")
    aboutme = aboutme_.read()
    aboutme_.close()

    status_ = open("Database/status.txt", "r")
    status = status_.read()
    status_.close()

    data = {"aboutme":aboutme, "status":status}

    return templates.TemplateResponse("index.html", context={"request":request, "data":data})

@app.get("/projects", response_class=HTMLResponse)
async def projects(request:Request):
    projects = await all_projects()
    return templates.TemplateResponse("projects.html", context={"request":request, "projects":projects["projects"]})

@app.get("/certification", response_class=HTMLResponse)
async def certification(request:Request):
    certificates = await all_certificates()
    return templates.TemplateResponse("certification.html", context={"request":request, "certificates":certificates["certificates"]})

@app.get("/blog", response_class=HTMLResponse)
async def blog(request:Request):
    blogs = await all_blogs()
    return templates.TemplateResponse("blog.html", context={"request":request, "blogs":blogs["blogs"]})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request:Request, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        return templates.TemplateResponse("admin.html", context={"request":request})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete certificate",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/set_aboutme")
async def set_aboutme(text:str = Body(...), credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        aboutme_ = open("Database/aboutme.txt", "w+")
        aboutme_.write(text)
        aboutme_.close()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/set_status")
async def set_status(text:str = Body(...), credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        status_ = open("Database/status.txt", "w+")
        status_.write(text)
        status_.close()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create project",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post("/upload_file")
async def upload_file(file:UploadFile = File(...), credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
            file_name = await generate_file_name()
            file_name = file_name + "." + file.filename.split(".")[-1]
            await save_file(file_name, file)

            return {"name": file_name}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.get("/files/{file_name}")
async def get_files(file_name:str):
    try:
        return FileResponse(f"Files/{file_name}")
    except:
        raise HTTPException(status_code=404, detail="File not found")

alphabet = string.ascii_uppercase+string.digits
name_length = 5
async def generate_file_name():
    files = [file.split(".")[0] for file in os.listdir()]
    while True:
        gen_name = "".join(random.choices(alphabet, k=name_length))
        if gen_name not in files:
            break
    return gen_name

@app.get("/get_database")
async def get_database():
    return FileResponse("Database/database.sqlite")

@app.get("/get_files")
async def get_files():
    try:
        os.remove('files.zip')
    except:pass
    zip_file = ZipFile('files.zip', 'w')
    files = os.listdir("Files")
    for file in files:
        zip_file.write(f"Files/{file}")
    zip_file.close()

    return FileResponse('files.zip')

async def save_file(file_name, file:UploadFile):
    with open(f"Files/{file_name}", "wb") as f:
        f.write(file.file.read())

@app.get("/all_projects")
async def all_projects():
    projects = []
    for project in list(select(b for b in Project)):
        projects.append(project.to_dict())
    projects = sorted(projects, key=lambda x: x["likes"], reverse=True)
    return {"projects": projects}

class ProjectModel(BaseModel):
    id:int
    title:str
    description:str
    url:str
    img_name:str
@app.post("/create_project")
async def create_project(request:ProjectModel, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            project = Project(title=request.title, 
                            description=request.description, 
                            github=request.url, 
                            img=request.img_name,
                            likes=0)
            return {"Project Created": project.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/delete_project")
async def delete_project(id:int = Body(..., embed=True), credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        project = Project.get(id=id)
        if project is not None:
            with db_session:
                project.delete()
        else:
            return {"Error": "Project not found"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/edit_project")
async def edit_project(request:ProjectModel, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        project = Project.get(id=request.id)
        if project is not None:
            with db_session:
                if request.title == "":
                    request.title = project.title
                if request.description == "":
                    request.description = project.description
                if request.url == "":
                    request.url = project.github
                if request.img_name == "":
                    request.img_name = project.img

                project.set(title=request.title, description = request.description, github=request.url, img=request.img_name)
        else:
            return {"Error": "Project not found"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/like_project")
async def like_project(id:int = Body(..., embed=True)):
    project = Project.get(id=id)
    if project is not None:
        with db_session:
            project.set(likes=project.likes+1)
    else:
        return {"Error": "Project not found"}

@app.post("/dislike_project")
async def dislike_project(id:int = Body(..., embed=True)):
    project = Project.get(id=id)
    if project is not None:
        with db_session:
            project.set(likes=project.likes-1)
    else:
        return {"Error": "Project not found"}


@app.get('/all_certificates')
async def all_certificates():
    certificates = []
    for certificate in list(select(b for b in Certificate)):
        certificates.append(certificate.to_dict())

    certificates = sorted(certificates, key=lambda x: x["likes"], reverse=True)
    return {"certificates": certificates}

class CertificateModel(BaseModel):
    name:str
    src:str
    url:str
@app.post('/create_certificate')
async def create_certificate(request:CertificateModel, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            certificate = Certificate(name=request.name, src=request.src, url=request.url, likes=0)
            return {"Certificate Created": certificate.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create certificate",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post('/delete_certificate')
async def delete_certificate(id, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            certificate = Certificate.get(id=id)
            if certificate is not None:
                certificate.delete()
            else:
                return {"Error": "Certificate not found."}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete certificate",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post("/like_certificate")
async def like_certificate(id:int = Body(..., embed=True)):
    certificate = Certificate.get(id=id)
    if certificate is not None:
        with db_session:
            certificate.set(likes=certificate.likes+1)
    else:
        return {"Error": "Project not found"}

@app.post("/dislike_certificate")
async def dislike_certificate(id:int = Body(..., embed=True)):
    certificate = Certificate.get(id=id)
    if certificate is not None:
        with db_session:
            certificate.set(likes=certificate.likes-1)
    else:
        return {"Error": "Project not found"}

# --------------------- blogs ----------------------------------
@app.get('/all_blogs')
async def all_blogs():
    blogs = []
    for blog in list(select(b for b in Blog)):
        blogs.append(blog.to_dict())
        
    blogs = sorted(blogs, key=lambda x: x["likes"], reverse=True)
    return {"blogs": blogs}


@app.post('/create_blog')
async def create_blog(title, description, url, img,
                      credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            blog = Blog(title=title, description=description, url=url, img=img, likes=0)
            return {"Blog Created": blog.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create blog",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post('/delete_blog')
async def delete_blog(id:int, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            blog = Blog.get(id=id)
            if blog is not None:
                blog.delete()
            else:
                return {"Error": "Blog with the given slug not found."}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete blog",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/like_blog")
async def like_blog(id:int = Body(..., embed=True)):
    blog = Blog.get(id=id)
    if blog is not None:
        with db_session:
            blog.set(likes=blog.likes+1)
    else:
        return {"Error": "Project not found"}

@app.post("/dislike_blog")
async def dislike_blog(id:int = Body(..., embed=True)):
    blog = Blog.get(id=id)
    if blog is not None:
        with db_session:
            blog.set(likes=blog.likes - 1)
    else:
        return {"Error": "Project not found"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, host='0.0.0.0', reload=True)
