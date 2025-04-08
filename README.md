# HDScanner Controller API (via Hypha)

This project exposes an asynchronous controller for the HDScanner scanning software over a [Hypha RPC](https://hypha.io) server.

It allows you to remotely interact with the scanner using high-level API calls like `snap_image`, `move_stage`, `switch_lens`, etc.

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Dependencies:
  ```bash
  pip install numpy imageio hypha-rpc
  ```

### Run the Scanner Service

```bash
python scanner_service.py
```

This will connect to the HDScanner software on `localhost:58207`, register the service on your Hypha server, and expose public RPC methods.

---

## 🔌 Connecting to the Service via Client

Here is an example client that connects and uses the `snap_image` method:

```python
import asyncio
from hypha_rpc import connect_to_server

async def main():
    server = await connect_to_server({"server_url": "http://localhost:9527"})

    # Replace this with the actual service ID you got from the server output
    svc = await server.get_service("your-workspace/your-service-id:hdscanner")

    # Call the API
    image = await svc.snap_image()
    print("Image shape:", image.shape)

if __name__ == "__main__":
    asyncio.run(main())
```

> 📝 You'll see your full service ID when running `scanner_service.py`. It will look like:
> `workspace-id/service-uid:hdscanner`

---

## 🧠 API Reference

### 📷 `snap_image() → np.ndarray`
Captures an image using the scanner camera.

**Returns:**  
`np.ndarray` — Image as a NumPy array (H, W, C).

---

### 🧪 `get_device_info() → dict`
Returns scanner device status.

**Returns:**
```json
{
  "camera": true,
  "controller": true,
  "taskrunning": false,
  "traystep": 0,
  "errorcode": 0
}
```

---

### 🧫 `new_scan(expo_wait=1000) → np.ndarray`
Creates a new scan session and returns the preview image.

**Arguments:**
- `expo_wait` (int): Time in milliseconds to wait for exposure stabilization (default: 1000).

**Returns:**  
`np.ndarray` — Preview image.

---

### 🧭 `move_stage(x=0.0, y=0.0, z=0.0, ack=False) → dict`
Moves the stage to given coordinates.

**Arguments:**
- `x`, `y`, `z` (float): Target position in microns.
- `ack` (bool): Whether to wait for confirmation from the scanner (default: False).

**Returns (if ack=True):**
```json
{
  "method": "StageStopped",
  "result": 0  # 0 = success, -1 = failure
}
```

---

### 🛑 `stop() → dict`
Stops all active tasks (scanning, focusing, moving).

**Returns:**
```json
{
  "method": "ScanStopped",
  "result": 0  # 0 = success
}
```

---

### 📍 `get_stage_info() → dict`
Returns current stage X/Y/Z position in microns.

**Returns:**
```json
{
  "X": 1000.1,
  "Y": 2000.2,
  "Z": 3000.3
}
```

---

### 🎛️ `control_stage(mode: str) → dict`
Sends a high-level stage command.

**Arguments:**
- `mode` (str): One of:
  - `"SlideOut"`, `"SlideIn"`, `"SlidePrev"`, `"SlideNext"`
  - `"StageLeft"`, `"StageRight"`, `"StageOut"`, `"StageIn"`
  - `"SlideDown"`, `"StageUp"`, `"StageHome"`

**Returns:**  
Command acknowledgment.

---

### 🔬 `switch_lens(mag: str) → dict`
Switches to a specific objective lens.

**Arguments:**
- `mag` (str): Magnification label, e.g. `"20X"`

**Returns:**  
Confirmation of lens switch.

---

### 📡 `focus_lens(mode="Fast") → dict`
Focuses the current objective lens.

**Arguments:**
- `mode` (str): `"Fast"`, `"Auto"`, or `"Manual"`.

**Returns:**
```json
{
  "method": "FocusStopped",
  "result": 0  # 0 = success, -1 = failure
}
```

---

## 🧩 Notes

- All image functions return NumPy arrays. You can directly visualize them with `matplotlib` or save them with `imageio.imwrite(...)`.
- Make sure HDScanner software is running with socket communication enabled (`localhost:58207`).

---

## 📬 Support

For bug reports or feature requests, open an issue or contact Wei Ouyang at [AICell Lab](https://aicell.io).

```
