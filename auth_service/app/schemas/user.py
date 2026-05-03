from pydantic import BaseModel

class UserCreate(BaseModel):   #Request Schema register
    username:str
    password:str
    email:str

class UserResponse(BaseModel):  #Response Schema login
    id:int
    username:str
    email:str
    
    class Config:
        orm_mode = True
  

  