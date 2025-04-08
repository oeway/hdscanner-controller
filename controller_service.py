import asyncio
from typing import Optional, Callable
from functools import wraps

import imageio.v3 as iio
import numpy as np

from hypha_rpc import connect_to_server
from hdscanner_controller import HDScannerController


def log_call(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"[CALL] {func.__name__}({kwargs})")
        try:
            result = await func(*args, **kwargs)
            print(f"[RESULT] {func.__name__} => {type(result)}")
            return result
        except Exception as e:
            print(f"[ERROR] {func.__name__}: {e}")
            raise
    return wrapper


class ScannerService:
    def __init__(self):
        self.controller: Optional[HDScannerController] = None

    async def setup(self):
        self.controller = HDScannerController()
        await self.controller.connect()

    async def _load_image(self, path: str) -> np.ndarray:
        print(f"[INFO] Reading image from: {path}")
        return iio.imread(path)

    @log_call
    async def snap_image(self) -> np.ndarray:
        """
        Capture a still image from the current camera view.

        Returns:
            np.ndarray: The captured image as a NumPy array (H, W, C).
        """
        result = await self.controller.snap_image()
        return await self._load_image(result["result"])

    @log_call
    async def get_device_info(self) -> dict:
        """Returns current device state."""
        return await self.controller.get_device_info()

    @log_call
    async def new_scan(self, expo_wait: int = 1000) -> np.ndarray:
        """
        Start a new scan session and return the preview image.

        Args:
            expo_wait (int): Exposure stabilization wait time in ms.

        Returns:
            np.ndarray: Preview image as a NumPy array (H, W, C).
        """
        await self.controller.new_scan(expo_wait)
        result = await self.controller.wait_for("PreviewImage")
        return await self._load_image(result["result"])

    @log_call
    async def move_stage(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, ack: bool = False) -> dict:
        """Move the stage to specified coordinates."""
        return await self.controller.move_stage(x, y, z, ack)

    @log_call
    async def stop(self) -> dict:
        """Stop all active operations."""
        return await self.controller.stop()

    @log_call
    async def get_stage_info(self) -> dict:
        """Query current stage position."""
        return await self.controller.get_stage_info()

    @log_call
    async def control_stage(self, mode: str) -> dict:
        """Execute a stage control command (e.g. 'SlideOut')."""
        return await self.controller.control_stage(mode)

    @log_call
    async def switch_lens(self, mag: str) -> dict:
        """Switch to the specified objective lens."""
        return await self.controller.switch_lens(mag)

    @log_call
    async def focus_lens(self, mode: str = "Fast") -> dict:
        """Focus the current lens using the specified mode."""
        return await self.controller.focus_lens(mode)


async def start_server(server_url: str):
    server = await connect_to_server({"server_url": server_url})
    scanner = ScannerService()
    await scanner.setup()

    svc = await server.register_service({
        "name": "HDScanner Controller",
        "id": "hdscanner",
        "config": {
            "visibility": "public"
        },
        "snap_image": scanner.snap_image,
        "get_device_info": scanner.get_device_info,
        "new_scan": scanner.new_scan,
        "move_stage": scanner.move_stage,
        "stop": scanner.stop,
        "get_stage_info": scanner.get_stage_info,
        "control_stage": scanner.control_stage,
        "switch_lens": scanner.switch_lens,
        "focus_lens": scanner.focus_lens,
    })

    workspace = server.config.workspace
    service_id = svc.id.split("/")[-1]

    print(f"[INFO] Scanner service registered at workspace: {workspace}, id: {svc.id}")
    print(f"[INFO] Try: {server_url}/{workspace}/services/{service_id}/snap_image")

    await server.serve()


if __name__ == "__main__":
    server_url = "https://hypha.aicell.io"
    asyncio.run(start_server(server_url))
