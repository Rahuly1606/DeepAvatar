# Model Weights Directory

This directory should contain the 3DDFA_V2 pretrained model weights.

## Required Files

1. **phase1_wpdc_vdc.pth.tar** (~70 MB)
   - Main model weights for 3DDFA_V2
   - Download from: https://github.com/cleardusk/3DDFA_V2/releases

2. **similarity_Lm3D_all.mat** (optional)
   - 3D landmark template
   - Download from: https://github.com/cleardusk/3DDFA_V2/releases

## Download Instructions

### Option 1: Manual Download

1. Visit: https://github.com/cleardusk/3DDFA_V2/releases
2. Download `phase1_wpdc_vdc.pth.tar`
3. Place it in this directory (`server/models/`)

### Option 2: Using wget (Linux/Mac)

```bash
cd server/models
wget https://github.com/cleardusk/3DDFA_V2/releases/download/v1.0/phase1_wpdc_vdc.pth.tar
```

### Option 3: Using curl

```bash
cd server/models
curl -L -O https://github.com/cleardusk/3DDFA_V2/releases/download/v1.0/phase1_wpdc_vdc.pth.tar
```

## Expected Directory Structure

After downloading, your directory should look like:

```
server/models/
├── README.md (this file)
├── phase1_wpdc_vdc.pth.tar
└── similarity_Lm3D_all.mat (optional)
```

## ONNX Conversion

After running the ONNX conversion script, additional files will be created:

```
server/models/
├── phase1_wpdc_vdc.pth.tar
├── face_recon_optimized.onnx (generated)
└── face_recon_optimized_quantized.onnx (optional, generated)
```

## Troubleshooting

### File not found error
- Verify the file is in `server/models/` directory
- Check file name matches exactly: `phase1_wpdc_vdc.pth.tar`
- Ensure file size is approximately 70 MB

### Download issues
- Check your internet connection
- Try using a VPN if GitHub is blocked
- Download manually via browser if command-line fails

## Alternative Models

While this application is designed for 3DDFA_V2, you can experiment with other 3D face reconstruction models by:

1. Modifying `model_wrapper.py` to load your model
2. Adjusting the preprocessing pipeline in `utils/preprocessor.py`
3. Updating the mesh generation code

## Security Note

⚠️ **Important:** Model files are excluded from version control (via `.gitignore`) due to their large size. Never commit model weights to Git repositories.

---

For more information, see the main README.md in the project root.
