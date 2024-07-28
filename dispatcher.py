import os
import subprocess
import atexit
from fastapi import FastAPI, Request, Depends, Query, HTTPException, WebSocket, APIRouter, Response
from urllib.parse import unquote
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import config
import subprocess
import random
import nginx
import uvicorn

from proxy_server import create_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

processes = {}
busy_ports = []


class DeployRoomRequest(BaseModel):
    token: str
    guid: str
    port: str
    bid: float
    player_amount: int


class RequestRoomSchema(BaseModel):
    token: str


class RoomSchema(BaseModel):
    guid: str
    port: str
    player_amount: int


class RemoveRoomRequest(BaseModel):
    token: str
    guid: str


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.post('/room')
async def deploy_room(request: DeployRoomRequest):
    if request.port in [value[2] for key, value in processes]:
        return HTTPException(status_code=400, detail='Given port is busy')
    if request.token == config.TOKEN:
        try:
            proxy_port = random.randint(50000, 50100)
            while proxy_port in busy_ports:
                proxy_port = random.randint(50000, 50100)
            busy_ports.append(proxy_port)
            listen_port = int(request.port)
            nginx_config = create_config(listen_port, proxy_port)
            config_path = f'C:\\nginx-1.26.1\\conf\\proxy\\proxy_{listen_port}_{proxy_port}.conf'
            nginx.dumpf(nginx_config, config_path)

            os.system(f"C:\\nssm-2.24\\nssm-2.24\\win64\\nssm.exe restart nginx")
            process = subprocess.Popen([f"C:\\Users\Administrator\Desktop\Builds\server.exe",
                                        f"-serverId={request.guid}",
                                        f"-port={proxy_port}",
                                        f"-maxPlayers={request.player_amount}",
                                        f"-isFree={True if request.bid == 0 else False}"])
            processes[request.guid] = (process, config_path, listen_port, request.player_amount)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")


@app.delete('/room')
async def remove_room(request: RemoveRoomRequest):
    if request.token == config.TOKEN:
        try:
            last_process = processes.pop(request.guid)
            last_process[0].kill()
            os.remove(last_process[1])
            os.system('C:\\nssm-2.24\\nssm-2.24\\win64\\nssm.exe restart nginx')
            return True
        except:
            return False
    else:
        raise HTTPException(status_code=400, detail="Incorrect token")


@app.get('/room')
async def get_rooms(request: RequestRoomSchema) -> list[RoomSchema]:
    if request.token == config.TOKEN:
        rooms = [RoomSchema(guid=key, port=value[2], player_amount=value[3]) for key, value in processes]
        return rooms


debug_endpoints = APIRouter(tags=["Debug"])
debug_room = None


@debug_endpoints.post('/deployTestRoom')
def deploy_test_room(player_amount):
    nginx_config = create_config(7777, 50101)
    config_path = f'C:\\nginx-1.26.1\\conf\\proxy\\proxy_{7777}_{50101}.conf'
    nginx.dumpf(nginx_config, config_path)

    os.system(f"C:\\nssm-2.24\\nssm-2.24\\win64\\nssm.exe restart nginx")
    process = subprocess.Popen([f"C:\\Users\Administrator\Desktop\Builds\server.exe",
                                f"-serverId=debug",
                                f"-port=50101",
                                f"-maxPlayers={player_amount}",
                                f"-isFree=True"])
    global debug_room
    debug_room = process


@debug_endpoints.delete("/closeTestRoom")
def close_test_room():
    if debug_room is not None:
        os.remove(f'C:\\nginx-1.26.1\\conf\\proxy\\proxy_{7777}_{50101}.conf')
        os.system(f"C:\\nssm-2.24\\nssm-2.24\\win64\\nssm.exe restart nginx")
        debug_room.kill()
        return Response()
    return Response("Room isn't deployed", status_code=400)


app.include_router(debug_endpoints)


def on_close():
    if os.path.exists(f'C:\\nginx-1.26.1\\conf\\proxy\\proxy_{7777}_{50101}.conf'):
        os.remove(f'C:\\nginx-1.26.1\\conf\\proxy\\proxy_{7777}_{50101}.conf')
    if debug_room is not None:
        debug_room.kill()
    for key, value in processes:
        value[0].kill()
        os.remove(value[1])
    os.system('C:\\nssm-2.24\\nssm-2.24\\win64\\nssm.exe restart nginx')


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="game.tondurakgame.com", port=8008,
                    ssl_keyfile="C:\\Users\Administrator\Desktop\Builds\Certs\privkey1.pem",
                    ssl_certfile="C:\\Users\\Administrator\\Desktop\\Builds\\Certs\\fullchain1.pem")
    except KeyboardInterrupt:
        on_close()
    atexit.register(on_close)
