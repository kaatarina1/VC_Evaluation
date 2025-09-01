# pip install praat-parselmouth numpy
from scipy.spatial.distance import euclidean
from scipy import stats
from fastdtw import fastdtw
import numpy as np
import librosa
import pyworld as pw

src_path = "D:\\Voice Conversion\\testing_rvc\\inputs\\m\\input_en_1.wav"
conv_path = "D:\\Voice Conversion\\testing_rvc\\data\\m\\beatrice_1\\monitor_en_1.wav"

# Load and process audio
def extract_f0(audio_path, sr=24000):
    y, sr = librosa.load(audio_path, sr=sr)
    y = y.astype(np.float64)
    f0, time_axis = pw.dio(y, sr, frame_period=5.0)
    return pw.stonemask(y, f0, time_axis, sr)

f0_src = extract_f0(src_path)
f0_conv = extract_f0(conv_path)

# Truncate to the shorter length
min_length = min(len(f0_src), len(f0_conv))
f0_src = f0_src[:min_length]
f0_conv = f0_conv[:min_length]

print(f"Original shapes - src: {f0_src.shape}, conv: {f0_conv.shape}")

# Create boolean masks for voiced frames
voiced_src = f0_src > 0
voiced_conv = f0_conv > 0

# Find the intersection: frames that are voiced in BOTH sequences
valid_voiced_frames = voiced_src & voiced_conv

# Apply the mask and FORCE proper 1D array conversion
f0_src_voiced = np.array(f0_src[valid_voiced_frames], dtype=np.float64).flatten()
f0_conv_voiced = np.array(f0_conv[valid_voiced_frames], dtype=np.float64).flatten()

print(f"After masking - src: {f0_src_voiced.shape}, conv: {f0_conv_voiced.shape}")
print(f"Sample values - src: {f0_src_voiced[:5]}, conv: {f0_conv_voiced[:5]}")

# Check if we have enough data
if len(f0_src_voiced) < 10 or len(f0_conv_voiced) < 10:
    print(f"Not enough voiced frames (src: {len(f0_src_voiced)}, conv: {len(f0_conv_voiced)})")
    f0_correlation = 0.0
else:
    # Reshape for DTW - ensure proper 2D arrays
    f0_src_voiced = f0_src_voiced.reshape(-1, 1)
    f0_conv_voiced = f0_conv_voiced.reshape(-1, 1)
    
    print(f"2D shapes - src: {f0_src_voiced.shape}, conv: {f0_conv_voiced.shape}")
    
    # Perform DTW
    try:
        distance, path = fastdtw(f0_src_voiced, f0_conv_voiced, dist=euclidean)
        
        aligned_f0_src = []
        aligned_f0_conv = []
        for i, j in path:
            aligned_f0_src.append(f0_src_voiced[i, 0])  # Use proper 2D indexing
            aligned_f0_conv.append(f0_conv_voiced[j, 0])
        
        aligned_f0_src = np.array(aligned_f0_src)
        aligned_f0_conv = np.array(aligned_f0_conv)
        
        f0_correlation, p_value = stats.pearsonr(aligned_f0_src, aligned_f0_conv)
        print(f"F0 Correlation (with DTW): {f0_correlation:.4f}")
        
    except Exception as e:
        print(f"DTW failed: {e}")
        # Fallback to simple correlation
        f0_correlation, p_value = stats.pearsonr(f0_src_voiced, f0_conv_voiced)
        print(f"F0 Correlation (no DTW): {f0_correlation:.4f}")

print(f"Final F0 Correlation: {f0_correlation:.4f}")