from pydantic import BaseModel


# Schema to send request to assistant
class Assistant(BaseModel):
    text: str
