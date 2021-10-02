from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from models import Blog, Certificate, Project
from pony.orm import *
from slugify import slugify
import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

async def authorize(credentials: HTTPBasicCredentials):
    #print(f"Username: {credentials.username}, Password: {credentials.password}")
    if credentials.username == "admin" and credentials.password == "password":
        return True
    else:
        return False


@app.get("/all_projects")
async def all_projects():
    projects = []
    for project in list(select(b for b in Project)):
        projects.append(project.to_dict())
    return {"projects": projects}


@app.post("/create_project")
async def create_project(title, description, url, img, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            project = Project(title=title, description=description, github=url, img=img)
            return {"Project Created": project.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create project",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.post("/delete_project")
async def delete_project(id, credentials: HTTPBasicCredentials = Depends(security)):
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
async def edit_project(id, title:str, description:str, url:str, img:str, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        project = Project.get(id=id)
        if project is not None:
            with db_session:
                project.set(title=title, description = description, github=url, img=img)
        else:
            return {"Error": "Project not found"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit project",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.get('/all_blogs')
async def all_blogs():
    blogs = []
    for blog in list(select(b for b in Blog)):
        blogs.append(blog.to_dict())
    return {"blogs": blogs}


@app.post('/create_blog')
async def create_blog(title, description, content,
                      credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            slug = slugify(" ".join(title.split()[:5]))
            blog = Blog(title=title, slug=slug, description=description, content=content,
                        date=datetime.datetime.now())
            return {"Blog Created": blog.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create blog",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post('/delete_blog')
async def delete_blog(slug: str, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            blog = Blog.get(slug=slug)
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

@app.post('/edit_blog')
async def edit_blog(slug: str, title:str, description:str, content:str, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            blog = Blog.get(slug=slug)
            if blog is not None:
                blog.set(title=title, description=description, content=content)
            else:
                return {"Error": "Blog with the given slug not found."}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit blog",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.get('/all_certificates')
async def all_certificates():
    certificates = []
    for certificate in list(select(b for b in Certificate)):
        certificates.append(certificate.to_dict())

    return {"certificates": certificates}

@app.post('/create_certificate')
async def create_certificate(name, src, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            certificate = Certificate(name=name, src=src)
            return {"Certificate Created": certificate.to_dict()}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create certificate",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post('/delete_certificate')
async def delete_certificate(name, credentials: HTTPBasicCredentials = Depends(security)):
    if await authorize(credentials):
        with db_session:
            certificate = Certificate.get(name=name)
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