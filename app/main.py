from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


my_posts = [{"title": "title1", "content": "content of post 1", "id": 1},
            {"title": "title2", "content": "content of post 2", "id": 2}]


def find_post(id):
    for p in my_posts:
        print(p['id'])
        if p['id'] == int(id):
            return p


class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # default value
    # rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='ashish',
                                cursor_factory=RealDictCursor)  # RealDictCursor ensure it returns column names when you make any query
        cursor = conn.cursor()

        print("Database connection was succesfull")
        break
    except Exception as err:
        print("Connection to database failed")
        print("Error: ", err)
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/posts")
def get_posts():
    cursor.execute("""select * from new_product""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


# @app.post("/createposts")
# def create_Posts(payload: dict = Body(...)):
#     print(payload)
#     return {"new_post": f"title {payload['title']}, content: {payload['content']}"}

# titile str,content: str
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_Posts(post: Post):
    # post_dict=new_post.model_dump()
    # post_dict['id']=randrange(0,10000000)
    # my_posts.append(post_dict)
    cursor.execute(""" insert into new_product (title, content, published) values (%s,%s,%s) RETURNING
    * """,
                   (post.title, post.content, post.published))

    new_post = cursor.fetchone()

    conn.commit()  # without this it  wont update database with new entry
    return {"data": new_post}

@app.get("/sql")
def test_posts(db: Session = Depends(get_db)):
    return {"status":"success"}


@app.get("/posts/latest")  # make sure this is defined above /posts/{id}
def get_latest_post():
    post = my_posts[-1]
    return {"detail": post}


@app.get("/posts/{id}")  # id : path parameter
# int is keeping a check that string is not passed to it
def get_post(id: int, response: Response):
    # print(id)
    cursor.execute(""" select * from new_product where id = %s""",
                   (str(id)))  # while comparing id has to be in string format
    post = cursor.fetchone()
    print(post)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message':f"post with {id} not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not found")
    return {"post_detail": post}


def find_index_post(id):
    to_remove = -1
    for index, p in enumerate(my_posts):
        if p['id'] == int(id):
            return index
    return to_remove


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """delete from new_product where id = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    # to_remove=find_index_post(id)
    if deleted_post:
        # my_posts.pop(to_remove)
        # on 204 status code don't send any data to browser back. That is expectation
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not exists")


@app.put("/posts/{id}")
def update_posts(id: int, post: Post):
    # "post": is content from user end . Post is kind of constraint that make sure "post" is following it
    # post = post.model_dump()
    cursor.execute(""" update new_product set  title=%s, content=%s, published=%s where id = %s 
    RETURNING * """, (post.title, post.content, post.published, str(id)))
    to_update = cursor.fetchone()
    conn.commit()
    # to_update=find_index_post(id)
    if to_update is not None:
        # for key,val in post.items():
        #     my_posts[to_update][key] = val
        # on 204 status code don't send any data to browser back. That is expectation
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not exists")
