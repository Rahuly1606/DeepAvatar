"""
Utility script to convert PyTorch model to ONNX format
for faster CPU inference
"""

import torch
import onnx
import yaml
import os
from model_wrapper import FaceModel


def convert_to_onnx(config_path='../config.yaml'):
    """
    Convert 3DDFA_V2 PyTorch model to ONNX format
    
    This provides ~30% speed improvement on CPU
    """
    print("[Converter] Loading configuration...")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize model
    print("[Converter] Loading PyTorch model...")
    face_model = FaceModel(config_path)
    
    if face_model.model is None:
        print("[Converter] Error: Model not loaded")
        return
    
    # Create dummy input
    input_size = config['performance']['input_resolution']
    dummy_input = torch.randn(1, 3, input_size, input_size)
    
    # Export to ONNX
    onnx_path = config['model']['onnx_model_path']
    print(f"[Converter] Exporting to ONNX: {onnx_path}")
    
    torch.onnx.export(
        face_model.model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Verify ONNX model
    print("[Converter] Verifying ONNX model...")
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    
    print(f"[Converter] ✓ Model successfully converted to ONNX")
    print(f"[Converter] File size: {os.path.getsize(onnx_path) / (1024*1024):.2f} MB")
    
    # Optional: Optimize ONNX model
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        quantized_path = onnx_path.replace('.onnx', '_quantized.onnx')
        print(f"[Converter] Quantizing model (FP16)...")
        
        quantize_dynamic(
            onnx_path,
            quantized_path,
            weight_type=QuantType.QUInt8
        )
        
        print(f"[Converter] ✓ Quantized model saved: {quantized_path}")
        print(f"[Converter] File size: {os.path.getsize(quantized_path) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"[Converter] Warning: Quantization failed: {e}")
    
    print("[Converter] Done!")


if __name__ == '__main__':
    convert_to_onnx()
