from hypha_rpc import connect_to_server

server = await connect_to_server({"server_url": "https://hypha.aicell.io"})

# Replace this with the actual service ID you got from the server output
hdscanner = await server.get_service("ws-user-corner-salesman-21379351/fJsGLp2jM7YpAE8SJAHCji:hdscanner")

# Call the API
#image = await hdscanner.snap_image()
#print("Image shape:", image.shape)

print("""
You can use the `hdscanner` object to access the microscopy scanner.

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
As an example, you can run the following to get snap an image:
```
image = await hdscanner.snap_image()
print("Image shape:", image.shape)
```

All image functions return NumPy arrays. You can directly visualize them with `matplotlib` or save them with `imageio.imwrite(...)`.

Note that it's a jupyter notebook environment whichs upports top-level await, you can just await and get results, no need to do asyncio.run or loop_until_complete.
""")
