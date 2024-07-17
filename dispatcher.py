from fastapi import FastAPI, Request, Depends, Query, HTTPException, WebSocket
from urllib.parse import unquote
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import config
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processes = {}

class DeployRoomRequest(BaseModel):
    token: str
    guid: str
    port: str
    bid: float
    player_amount: int

class RemoveRoomRequest(BaseModel):
    token: str
    guid: str

@app.post('/deployroom')
async def deployRoom(request: DeployRoomRequest):

    if request.token == config.TOKEN:
        try:
            process = subprocess.Popen([f"C:\\Users\Administrator\Desktop\Builds\.\Server.exe "
                                        f"-serverId={request.guid} "
                                        f"-port={request.port} "
                                        f"-maxPlayers={request.player_amount} "
                                        f"-isFree={True if request.bid == 0 else False}"])
            processes[request.guid] = process
            return True
        except:
            return False
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")


@app.post('/removeroom')
async def removeRoom(request: RemoveRoomRequest):
    if request.token == config.TOKEN:
        try:
            last_process = processes.pop(request.guid)
            last_process.kill()
            return True
        except:
            return False
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")

uvicorn.run(app,host="178.20.44.32", port=8000)
