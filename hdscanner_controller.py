import asyncio
import json
from typing import Any, Dict, Optional, Callable


class HDScannerController:
    def __init__(self, host="127.0.0.1", port=58207):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._response_callbacks: Dict[str, asyncio.Future] = {}
        self._listener_task: Optional[asyncio.Task] = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self._listener_task = asyncio.create_task(self._listen())
        print(f"[HDScanner] Connected to {self.host}:{self.port}")

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if self._listener_task:
            self._listener_task.cancel()
        print("[HDScanner] Disconnected")

    async def _listen(self):
        buffer = ""
        while True:
            try:
                data = await self.reader.read(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while True:
                    start = buffer.find("{")
                    end = buffer.find("}") + 1
                    if start != -1 and end > start:
                        try:
                            raw = buffer[start:end]
                            buffer = buffer[end:]
                            message = json.loads(raw)
                            await self._handle_message(message)
                        except json.JSONDecodeError:
                            break
                    else:
                        break
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[HDScanner] Listen error: {e}")
                break

    async def _handle_message(self, msg: Dict[str, Any]):
        method = msg.get("method")
        if method in self._response_callbacks:
            future = self._response_callbacks.pop(method)
            if not future.done():
                future.set_result(msg)
        elif method == "ErrorInfo":
            print(f"[HDScanner] ERROR: {msg['result']} (code {msg['code']})")
        else:
            print(f"[HDScanner] Unhandled message:\n{json.dumps(msg, indent=2)}")

    async def _send_command(self, payload: Dict[str, Any], expect: Optional[str] = None) -> Any:
        if not self.writer or not self.reader:
            raise RuntimeError("Not connected to HDScanner")
        message = json.dumps(payload) + "\n"
        future = None
        if expect:
            future = asyncio.get_event_loop().create_future()
            self._response_callbacks[expect] = future
        self.writer.write(message.encode("utf-8"))
        await self.writer.drain()
        return await future if future else None

    async def wait_for(self, method: str, timeout: float = 10.0) -> Dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        self._response_callbacks[method] = future
        return await asyncio.wait_for(future, timeout)

    # === API Methods ===

    async def snap_image(self) -> Dict[str, Any]:
        return await self._send_command({"method": "CameraImage"}, expect="CameraImage")

    async def new_scan(self, expo_wait: int = 1000) -> Dict[str, Any]:
        return await self._send_command({"method": "NewScan", "expoWait": expo_wait})

    async def move_stage(self, x=0.0, y=0.0, z=0.0, ack=False) -> Optional[Dict[str, Any]]:
        return await self._send_command({
            "method": "MoveStage",
            "X": x, "Y": y, "Z": z,
            "ack": ack
        }, expect="StageStopped" if ack else None)

    async def stop(self) -> Dict[str, Any]:
        return await self._send_command({"method": "Stop"})

    async def get_device_info(self) -> Dict[str, Any]:
        return await self._send_command({"method": "DeviceInfo"}, expect="DeviceInfo")

    async def get_stage_info(self) -> Dict[str, Any]:
        return await self._send_command({"method": "StageInfo"}, expect="StageInfo")

    async def control_stage(self, mode: str) -> Dict[str, Any]:
        return await self._send_command({"method": "ControlStage", "mode": mode})

    async def switch_lens(self, mag: str) -> Dict[str, Any]:
        return await self._send_command({"method": "SwitchLen", "mag": mag})

    async def focus_lens(self, mode="Fast") -> Optional[Dict[str, Any]]:
        await self._send_command({"method": "FocusLen", "mode": mode})
        return await self.wait_for("FocusStopped")
