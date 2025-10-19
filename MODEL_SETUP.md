# Model Setup Guide

## ✅ Good News!

You already have the 3DDFA_V2 repository downloaded at:
```
c:\Users\alexr\PROJECTS\3DfaceReconstuction\3DDFA_V2-0.12\
```

The model weights are already available in the `weights` folder!

## 📥 Available Models

### Already Downloaded (in 3DDFA_V2-0.12/weights/):
- ✅ `mb05_120x120.pth` - MobileNet v0.5 backbone (smaller, faster)
- ✅ `mb1_120x120.pth` - MobileNet v1 backbone (larger, more accurate)

### Optional ONNX Models (for even faster CPU inference):

You can download pre-converted ONNX models:

#### MobileNet v1 ONNX (Recommended):
- **Google Drive**: https://drive.google.com/file/d/1YpO1KfXvJHRmCBkErNa62dHm-CUjsoIk/view?usp=sharing
- **Baidu Drive**: https://pan.baidu.com/s/1qpQBd5KOS0-5lD6jZKXZ-Q (Password: `cqbx`)

#### MobileNet v0.5 ONNX (Lighter):
- **Google Drive**: https://drive.google.com/file/d/1orJFiZPshmp7jmCx_D0tvIEtPYtnFvHS/view?usp=sharing
- **Baidu Drive**: https://pan.baidu.com/s/1sRaBOA5wHu6PFS1Qd-TBFA (Password: `8qst`)

## 🔧 Quick Setup

### Option 1: Use Existing PyTorch Models (Easiest)

Copy the model to our server directory:

```powershell
# Copy MobileNet v1 model
Copy-Item "c:\Users\alexr\PROJECTS\3DfaceReconstuction\3DDFA_V2-0.12\weights\mb1_120x120.pth" -Destination "c:\Users\alexr\PROJECTS\3DfaceReconstuction\server\models\"

# Also copy the config
Copy-Item "c:\Users\alexr\PROJECTS\3DfaceReconstuction\3DDFA_V2-0.12\configs\mb1_120x120.yml" -Destination "c:\Users\alexr\PROJECTS\3DfaceReconstuction\server\models\"
```

### Option 2: Download ONNX Model (Best for CPU)

1. **Download from Google Drive:**
   - Visit: https://drive.google.com/file/d/1YpO1KfXvJHRmCBkErNa62dHm-CUjsoIk/view?usp=sharing
   - Click "Download"
   - Save to: `c:\Users\alexr\PROJECTS\3DfaceReconstuction\server\models\mb1_120x120.onnx`

2. **Using PowerShell (if you have gdown):**
   ```powershell
   pip install gdown
   cd server\models
   gdown 1YpO1KfXvJHRmCBkErNa62dHm-CUjsoIk
   ```

### Option 3: Use 3DDFA_V2 Directly

Instead of copying, we can integrate the existing 3DDFA_V2 code directly. I'll create an updated model wrapper for this.

## 📊 Model Comparison

| Model | Size | Speed (CPU) | Accuracy | Recommended For |
|-------|------|-------------|----------|-----------------|
| `mb05_120x120.pth` | ~15 MB | Fast | Good | Low-end CPU |
| `mb1_120x120.pth` | ~30 MB | Medium | Better | Balanced |
| `mb1_120x120.onnx` | ~30 MB | **Fastest** | Better | **Best for CPU** |

## 🎯 Recommended: Use ONNX Model

For best CPU performance, use the ONNX version:

1. Download `mb1_120x120.onnx` from Google Drive (link above)
2. Place in `server/models/`
3. Update `server/config.yaml`:
   ```yaml
   model:
     weights_path: "./models/mb1_120x120.onnx"
     use_onnx: true
   ```

## 🔄 Alternative: Integrate Existing 3DDFA_V2

I can update our code to use the existing 3DDFA_V2 repository directly. This is the **easiest option** since all the code and models are already there!

Would you like me to:
1. ✅ Create an integration layer to use the existing 3DDFA_V2 code?
2. ✅ Update our model_wrapper.py to load from 3DDFA_V2-0.12?

This way you don't need to download anything - we'll use what you already have!

## 📝 Next Steps

Let me know which option you prefer:
- **Option A**: Copy existing PyTorch model (quick, simple)
- **Option B**: Download ONNX model (best performance)
- **Option C**: Integrate existing 3DDFA_V2 code (most complete, recommended)

I recommend **Option C** - I'll update the code to use your existing 3DDFA_V2 installation!
