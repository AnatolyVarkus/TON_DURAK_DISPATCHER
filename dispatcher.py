import os

from fastapi import FastAPI, Request, Depends, Query, HTTPException, WebSocket
from urllib.parse import unquote
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import config
import subprocess
import random
import nginx

from proxy_server import create_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processes = {}
busy_ports = []


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
            proxy_port = random.randint(50000, 50100)
            while proxy_port in busy_ports:
                proxy_port = random.randint(50000, 50100)
            busy_ports.append(proxy_port)
            listen_port = int(request.port)
            nginx_config = create_config(listen_port, proxy_port)
            config_path = f'C:\\nginx-1.26.\proxy_{listen_port}_{proxy_port}.conf'
            nginx.dumpf(nginx_config,config_path)

            os.system('C:\\nssm-2.24\nssm-2.24\win64\nssm.exe restart nginx')
            process = subprocess.Popen([f"C:\\Users\Administrator\Desktop\Builds\.\Server.exe "
                                        f"-serverId={request.guid} "
                                        f"-port={proxy_port} "
                                        f"-maxPlayers={request.player_amount} "
                                        f"-isFree={True if request.bid == 0 else False}"])
            processes[request.guid] = (process,config_path)
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
            last_process[0].kill()
            os.remove(last_process[1])
            os.system('C:\\nssm-2.24\nssm-2.24\win64\nssm.exe restart nginx')
            return True
        except:
            return False
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")


uvicorn.run(app, host="178.20.44.32", port=8000)
