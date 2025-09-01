# import librosa, numpy as np

# def mcd(x, y, sr=22050, n_mfcc=13):
#     # Normalize waveforms
#     # x = x / np.max(np.abs(x))
#     # y = y / np.max(np.abs(y))

#     # # Use log-mel spectrogram before MFCC
#     # mel_x = librosa.feature.melspectrogram(y=x, sr=sr, n_mels=40, fmax=sr//2)
#     # mel_y = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40, fmax=sr//2)

#     # logmel_x = librosa.power_to_db(mel_x)
#     # logmel_y = librosa.power_to_db(mel_y)

#     # Extract MFCCs from log-mel (skip 0th coeff)
#     mfcc_x = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=n_mfcc)[1:, :]
#     mfcc_y = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)[1:, :]

#     # Align by truncating
#     # min_frames = min(mfcc_x.shape[1], mfcc_y.shape[1])
#     # mfcc_x, mfcc_y = mfcc_x[:, :min_frames], mfcc_y[:, :min_frames]

#     # Compute cost matrix
#     # D, wp = librosa.sequence.dtw(X=mfcc_x, Y=mfcc_y, metric='euclidean')

#     # # Warp MFCCs according to DTW path
#     # mfcc_x_aligned = mfcc_x[:, wp[:, 0]]
#     # mfcc_y_aligned = mfcc_y[:, wp[:, 1]]

#     # Compute MCD
#     diff = mfcc_x - mfcc_y
#     dist = np.sqrt((diff**2).sum(axis=0))
#     mcd_value = (10.0 / np.log(10)) * np.sqrt(2.0) * np.mean(dist)
#     return mcd_value, mfcc_x, mfcc_y


# # ---------------------------
# # Load your files
# # ---------------------------
# src_path = "D:\\Voice Conversion\\testing_rvc\\input_en_1.wav"
# conv_path = "D:\\Voice Conversion\\testing_rvc\\monitor_en_1.wav"

# src, sr = librosa.load(src_path, sr=22050)
# conv, _ = librosa.load(conv_path, sr=22050)

# # Compute MCD with debugging
# mcd_val, mfcc_src, mfcc_conv = mcd(src, conv, sr)

# print(f"MCD: {mcd_val:.3f} dB")
# print(f"Input length: {len(src)}, Converted length: {len(conv)}")
# print(f"MFCC shapes: src {mfcc_src.shape}, conv {mfcc_conv.shape}")
# print(f"MFCC src mean/std: {np.mean(mfcc_src):.2f} / {np.std(mfcc_src):.2f}")
# print(f"MFCC conv mean/std: {np.mean(mfcc_conv):.2f} / {np.std(mfcc_conv):.2f}")
# print(f"First 5 frame distances: {np.sqrt(((mfcc_src - mfcc_conv)**2).sum(axis=0))[:5]}")

# import librosa
# import numpy as np
# from scipy import signal

# def calculate_mcd_approx(x, y, sr=22050, n_mfcc=13, use_dtw=False):
#     """
#     A better approximation of MCD using MFCCs.
#     WARNING: This is an approximation. For research papers, use a proper MCEP extraction method.
#     """
    
#     # 1. LOUDNESS NORMALIZATION - CRITICAL STEP
#     x = x / np.max(np.abs(x))
#     y = y / np.max(np.abs(y))
    
#     # 2. PRE-EMPHASIS (HP Filter) - Emphasizes high frequencies like MCEP extraction does
#     x = signal.lfilter([1, -0.97], 1, x)
#     y = signal.lfilter([1, -0.97], 1, y)
    
#     # 3. Extract MFCCs - Use more coefficients and hop_length for stability
#     n_mels = 80 # Use more mel bands for better resolution
#     hop_length = 256
    
#     mfcc_x = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=n_mfcc, n_mels=n_mels, hop_length=hop_length)
#     mfcc_y = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, n_mels=n_mels, hop_length=hop_length)
    
#     # 4. IGNORE THE 0th COEFFICIENT (log energy)
#     mfcc_x = mfcc_x[1:, :]
#     mfcc_y = mfcc_y[1:, :]
    
#     # 5. DTW ALIGNMENT - ABSOLUTELY NECESSARY
#     if use_dtw:
#         D, wp = librosa.sequence.dtw(X=mfcc_x, Y=mfcc_y, metric='euclidean')
#         # Warp the sequences to the shortest path
#         mfcc_x_aligned = mfcc_x[:, wp[:, 0]]
#         mfcc_y_aligned = mfcc_y[:, wp[:, 1]]
#     else:
#         # If no DTW, just truncate (NOT recommended, but for testing)
#         min_len = min(mfcc_x.shape[1], mfcc_y.shape[1])
#         mfcc_x_aligned = mfcc_x[:, :min_len]
#         mfcc_y_aligned = mfcc_y[:, :min_len]
    
#     # 6. Compute the MCD formula
#     diff = mfcc_x_aligned - mfcc_y_aligned
#     dist = np.sqrt((diff ** 2).sum(axis=0)) # Euclidean distance per frame
#     mcd_value = (10.0 / np.log(10)) * np.sqrt(2.0) * np.mean(dist) # Scale to dB
    
#     return mcd_value

# ---------------------------
# Load your files
# ---------------------------
# src_path = "D:\\Voice Conversion\\testing_rvc\\input_en_1.wav"
# conv_path = "D:\\Voice Conversion\\testing_rvc\\monitor_en_1.wav"

# src, sr = librosa.load(src_path, sr=22050)
# conv, _ = librosa.load(conv_path, sr=22050)

# # Compute the improved MCD approximation
# mcd_val = calculate_mcd_approx(src, conv, sr, n_mfcc=13, use_dtw=True)

# print(f"Approximate MCD: {mcd_val:.3f} dB")
# import matplotlib.pyplot as plt
# import librosa
# import numpy as np

# def simple_frame_distance(x, y, sr=22050, n_mfcc=13):
#     """Calculate the average Euclidean distance between MFCC frames without any DTW. This is a nonsense metric for evaluation but great for debugging."""
    
#     # Extract MFCCs
#     mfcc_x = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=n_mfcc, hop_length=256)[1:, :] # skip 0th coeff
#     mfcc_y = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=256)[1:, :]
    
#     # Truncate to the shorter length
#     min_frames = min(mfcc_x.shape[1], mfcc_y.shape[1])
#     mfcc_x_trunc = mfcc_x[:, :min_frames]
#     mfcc_y_trunc = mfcc_y[:, :min_frames]
    
#     # Calculate the Euclidean distance for each frame
#     dist_per_frame = np.linalg.norm(mfcc_x_trunc - mfcc_y_trunc, axis=0)
    
#     return dist_per_frame, mfcc_x_trunc, mfcc_y_trunc

# src_path = "D:\\Voice Conversion\\testing_rvc\\input_en_1.wav"
# conv_path = "D:\\Voice Conversion\\testing_rvc\\monitor_en_1.wav"

# src, sr = librosa.load(src_path, sr=22050)
# conv, _ = librosa.load(conv_path, sr=22050)
# # Calculate the per-frame distances
# distances, mfcc_src, mfcc_conv = simple_frame_distance(src, conv, sr)

# # Plot the distance for each frame
# plt.figure(figsize=(12, 6))
# plt.plot(distances)
# plt.title('Euclidean Distance between UNALIGNED MFCC Frames')
# plt.xlabel('Frame Index')
# plt.ylabel('Distance')
# plt.axhline(y=np.mean(distances), color='r', linestyle='--', label=f'Mean Distance: {np.mean(distances):.2f}')
# plt.legend()
# plt.show()

# print(f"Mean unaligned frame distance: {np.mean(distances):.2f}")
# print(f"Max unaligned frame distance: {np.max(distances):.2f}")
# print(f"Min unaligned frame distance: {np.min(distances):.2f}")

from pymcd.mcd import Calculate_MCD

# Initialize the calculator
mcd_toolbox = Calculate_MCD(MCD_mode="dtw")

# Calculate MCD
mcd_value = mcd_toolbox.calculate_mcd("D:\\Voice Conversion\\testing_rvc\\inputs\\f\\input_slo_2.wav", "D:\\Voice Conversion\\testing_rvc\\data\\f\\beatrice_2\\monitor_slo_2.wav")
print(f"Correct MCD: {mcd_value} dB")