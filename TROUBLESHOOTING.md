# Troubleshooting Guide

## Common Issues and Solutions

### 🔴 Backend Issues

#### Issue: "Model weights not found"
```
FileNotFoundError: Model weights not found at ./models/phase1_wpdc_vdc.pth.tar
```

**Solution:**
1. Download model weights from https://github.com/cleardusk/3DDFA_V2/releases
2. Place `phase1_wpdc_vdc.pth.tar` in `server/models/` directory
3. Verify file exists: `ls server/models/` (Linux/Mac) or `dir server\models\` (Windows)

---

#### Issue: "Import Error: No module named 'flask_socketio'"
```
ImportError: No module named 'flask_socketio'
```

**Solution:**
```bash
cd server
pip install -r requirements.txt
```

---

#### Issue: "Address already in use (Port 5000)"
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Kill the process or change port in config.yaml
```

---

#### Issue: "CUDA out of memory" (GPU mode)
```
RuntimeError: CUDA out of memory
```

**Solution:**
1. Reduce input resolution in `config.yaml`:
   ```yaml
   performance:
     input_resolution: 256  # instead of 320
   ```
2. Or fall back to CPU mode:
   ```yaml
   model:
     device: "cpu"
   ```

---

### 🔵 Frontend Issues

#### Issue: "Failed to connect to backend"
```
Error: Failed to connect to backend. Make sure the server is running.
```

**Solution:**
1. Check if Flask server is running:
   ```bash
   curl http://localhost:5000/health
   ```
2. Verify port in `client/src/App.jsx` matches server port
3. Check firewall settings
4. Ensure both frontend and backend are running

---

#### Issue: "Webcam not detected"
```
Failed to access webcam. Please grant camera permissions.
```

**Solution:**
1. Grant camera permissions in browser:
   - Chrome: Settings → Privacy → Camera
   - Firefox: Preferences → Privacy → Permissions → Camera
2. Check if webcam is in use by another application
3. Try different browser
4. Check browser console for detailed error

---

#### Issue: "npm install fails"
```
npm ERR! code ERESOLVE
```

**Solution:**
```bash
cd client
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

---

### ⚡ Performance Issues

#### Issue: "Very low FPS (< 2)"

**Solutions (in order of effectiveness):**

1. **Increase frame skip:**
   ```yaml
   performance:
     frame_skip: 3  # or 4
   ```

2. **Reduce resolution:**
   ```yaml
   performance:
     input_resolution: 256
   ```

3. **Enable ONNX Runtime:**
   ```yaml
   model:
     use_onnx: true
   ```

4. **Convert model to ONNX:**
   ```bash
   cd server
   python utils/convert_to_onnx.py
   ```

5. **Close other applications** to free up CPU

6. **Upgrade to GPU mode** (requires NVIDIA GPU):
   ```yaml
   model:
     device: "cuda"
   ```

---

#### Issue: "High latency (> 300ms)"

**Solutions:**
1. Enable face tracking:
   ```yaml
   performance:
     enable_tracking: true
     redetect_interval: 30
   ```

2. Use binary format:
   ```yaml
   socket:
     binary_format: true
     compression: true
   ```

3. Check CPU usage - close background apps

---

#### Issue: "Mesh not rendering / Black screen in 3D viewer"

**Solutions:**
1. Check browser console for Three.js errors
2. Verify WebGL is enabled:
   - Visit: `chrome://gpu/` or `about:support` (Firefox)
   - Look for "WebGL: Hardware accelerated"
3. Update graphics drivers
4. Try different browser (Chrome recommended)

---

### 🌐 Network Issues

#### Issue: "Socket connection keeps dropping"

**Solutions:**
1. Increase timeout in `config.yaml`:
   ```yaml
   socket:
     ping_timeout: 120
     ping_interval: 50
   ```

2. Check network stability
3. Use wired connection instead of WiFi
4. Disable VPN or proxy

---

#### Issue: "CORS errors in browser console"

**Solution:**
1. Verify CORS is enabled in `server/app.py`:
   ```python
   CORS(app, resources={r"/*": {"origins": "*"}})
   ```

2. Or specify frontend origin:
   ```python
   CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
   ```

---

### 🐳 Docker Issues

#### Issue: "Docker build fails"

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t 3d-face-recon .
```

---

#### Issue: "Can't access webcam in Docker"

**Solution:**
Docker containers cannot access host webcam directly. Run frontend outside Docker:
```bash
# Run only backend in Docker
docker run -p 5000:5000 3d-face-recon

# Run frontend on host
cd client
npm run dev
```

---

### 🖥️ System-Specific Issues

#### Windows: "Python not found"

**Solution:**
1. Install Python from https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Restart terminal
4. Verify: `python --version`

---

#### Mac: "Command not found: python"

**Solution:**
```bash
# Use python3 instead
python3 --version
pip3 install -r requirements.txt

# Or create alias
alias python=python3
alias pip=pip3
```

---

#### Linux: "Permission denied" errors

**Solution:**
```bash
# Fix permissions
chmod +x docker-entrypoint.sh
chmod +x server/utils/convert_to_onnx.py

# Or use sudo
sudo python app.py
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

In `config.yaml`:
```yaml
logging:
  verbose: true
  log_performance: true
  
debug:
  enable_profiling: true
  save_frames: true  # Save frames for debugging
```

### Check Server Health

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "model": true,
    "preprocessor": true,
    "face_detector": true
  }
}
```

### Browser Console

Press `F12` to open browser console and check for:
- Socket connection errors
- JavaScript errors
- Network request failures

### Test Dependencies

```bash
python check_dependencies.py
```

---

## 🆘 Still Having Issues?

1. **Check logs:** Look at terminal output for error messages
2. **Verify versions:** Ensure Python 3.8+, Node.js 16+
3. **Clean install:**
   ```bash
   # Backend
   cd server
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   
   # Frontend
   cd client
   rm -rf node_modules
   npm install
   ```

4. **Test minimal setup:**
   - Run backend only and check http://localhost:5000/
   - Run frontend only (without backend)
   - Test webcam in simple HTML page

5. **Check system resources:**
   - Ensure sufficient RAM (4GB+ recommended)
   - Check CPU isn't throttling
   - Close heavy applications

---

## 📞 Getting Help

If you're still stuck:

1. Check the [GitHub Issues](https://github.com/cleardusk/3DDFA_V2/issues) for 3DDFA_V2
2. Review Flask-SocketIO documentation
3. Check Three.js documentation for rendering issues

Remember to include:
- Error messages (full stack trace)
- System info (OS, Python version, Node version)
- Configuration (config.yaml contents)
- Steps to reproduce

---

**Most issues can be resolved by:**
1. ✅ Verifying all dependencies are installed
2. ✅ Downloading model weights correctly
3. ✅ Ensuring backend and frontend are both running
4. ✅ Granting camera permissions
5. ✅ Adjusting performance settings for your hardware
