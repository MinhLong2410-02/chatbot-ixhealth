from fastapi import FastAPI, HTTPException, Request, Depends, Form, UploadFile, File, status
from fastapi.responses import JSONResponse
from base import *
from stream_chat import StreamChat
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from py_trans import Async_PyTranslator
import os
from os.path import join, dirname
from dotenv import load_dotenv
from chatbot.chatbot import Chatbot

dotenv_path = join('.env')
load_dotenv(dotenv_path)

GETSTREAM_API_SECRET = os.environ.get("GETSTREAM_API_SECRET")
GETSTREAM_API_KEY = os.environ.get("GETSTREAM_API_KEY")
server_client = StreamChat(api_key=GETSTREAM_API_KEY, api_secret=GETSTREAM_API_SECRET)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


tr = Async_PyTranslator()
app = FastAPI()
llm = Chatbot()

@app.get("/get_user_tokens")
def get_user_tokens(user_login: UserLogin):
    token = server_client.create_token(user_id=str(user_login.user_id))
    return {"token": token}

@app.post("/getstream_webhooks")
async def getstream_webhooks(request: Request):
    valid = server_client.verify_webhook(request.body, request.headers.get("x-signature"))
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    data = await request.json()
    if 'message' in data:
        message_content = data['message']
        user_id = message_content['user_id']
        channel_type, channel_id = message_content['cid'].split(":")

        if 'command' in message_content:
            command = message_content['command']
            session_id = user_id    
            args = message_content['args']
            response = await llm.ask(args, session_id=session_id) 
            channel = server_client.channel(channel_type=channel_type, channel_id=channel_id)
            channel.send_message({"text": response}, message_content['user_id'])
            return {"result": "command executed"}

    return {"data": data}


@app.get("/")
def webhooks_health_check():
    return {"health status": 'excellent'}



# async def generator(query: str, session_id: str, internet_search:bool) -> AsyncGenerator[str, None]:
#     content = ""
#     query = await tr.translate_dict(query, "en")
#     print(query)
#     for chunk in llm.stream(query['translation'], session_id, internet_search=internet_search):
#         content += chunk
#         if "\n" in chunk:
#             res =  await tr.translate_dict(content, "vi")
#             yield res['translation']+'\n'
#             content = ""
#     if content != "":
#         res =  await tr.translate_dict(content, "vi")
#         yield res['translation']+'\n'

# @app.get("/chat/")
# async def chat(query: str,internet_search: bool, current_user: User = Depends(get_current_active_user), session_id: str = ""):
#     if session_id == "":
#         session_id = current_user.username
#     return StreamingResponse(generator(query, session_id, internet_search))
    


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8055)