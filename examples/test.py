import matplotlib.pyplot as plt
import numpy as np
import torchaudio
import torch

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled   = True

from lpctorch import LPCCoefficients
from librosa.core import lpc

'''
código disponível em:
https://pytorch.org/tutorials/beginner/audio_preprocessing_tutorial.html#audio-i-o
'''
def plot_waveform(waveform, sample_rate, title="Waveform", xlim=None, ylim=None):
  waveform = waveform.numpy()

  num_channels, num_frames = waveform.shape
  time_axis = torch.arange(0, num_frames) / sample_rate

  figure, axes = plt.subplots(num_channels, 1)
  if num_channels == 1:
    axes = [axes]
  for c in range(num_channels):
    axes[c].plot(time_axis, waveform[c], linewidth=1)
    axes[c].grid(True)
    if num_channels > 1:
      axes[c].set_ylabel(f'Channel {c+1}')
    if xlim:
      axes[c].set_xlim(xlim)
    if ylim:
      axes[c].set_ylim(ylim)
  figure.suptitle(title)
  plt.show(block=False)

# Load audio file
sr             = 16000 # 16 kHz
path           = './examples/sample.wav'
data, _sr      = torchaudio.load(path) #""", normalization = lambda x: x.abs( ).max( ) )"""
data           = torchaudio.transforms.Resample( _sr, sr )( data )
duration       = data.size( 1 ) / sr

# Get audio sample worth of 512 ms
worth_duration = .512 # 512 ms ( 256 ms before and 256 ms after )
worth_size     = int( np.floor( worth_duration * sr ) )
X              = data[ :, :worth_size ]
X_duration     = X.size( 1 ) / sr
X              = torch.cat( [ X for i in range( 4 ) ] )

# ====================== ME ====================================================
# Divide in 64 2x overlapping frames
frame_duration = .016 # 16 ms
frame_overlap  = .5
K              = 32
lpc_prep       = LPCCoefficients(
    sr,
    frame_duration,
    frame_overlap,
    order = ( K - 1 )
).eval( ).cpu() # cuda()
alphas         = lpc_prep( X.cpu( ) ).detach( ).cpu( ).numpy( )

# resposta em frequência do filtro com os coeficientes
framesCoefs = {}
#frameCoefs = {'frame', 'coefs'}
for i in range(K):
    framesCoefs[i]=np.array(alphas[0][i]),
import scipy.signal as sig
f = 20 # número do frame
tups = sig.freqz(1, framesCoefs[f][0])
 
# Print details
print( f'[Init]   [Audio]  src: { path }, sr: { sr }, duration: { duration }' )
print( f'[Init]   [Sample] size: { X.shape }, duration: { X_duration }' )
print( f'[Me]     [Alphas] size: { alphas.shape }' )


# ====================== NOT ME ================================================
def librosa_lpc( X, order ):
    try:
        return lpc( X, order )
    except:
        res      = np.zeros( ( order + 1, ) )
        res[ 0 ] = 1.
        return res

frames  = lpc_prep.frames( X.cpu( ) )
frames  = frames[ 0 ].detach( ).cpu( ).numpy( )
_alphas = np.array( [ librosa_lpc( frames[ i ], K - 1 ) for i in range( frames.shape[ 0 ] ) ] )
print( f'[Not Me] [Alphas] size: { _alphas.shape }' )

print( f'Error [Me] vs [Not Me]: { ( alphas[ 0 ] - _alphas ).sum( axis = -1 ).mean( ) }' )

# Draw frames
fig = plt.figure( )
ax  = fig.add_subplot( 211 )
plt.plot(tups[0], abs(tups[1]))
# ax.imshow( alphas[ 0 ] )
ax  = fig.add_subplot( 212 )
plt.plot(frames[f]) 
# ax.imshow( _alphas )
fig.canvas.draw( )
plt.show( )

key = cv2.waitKey(0)

# if the `q` key was pressed, break from the loop
# if key == ord("q"): break
print('finalizado')

# # Draw frames
# fig = plt.figure( )
# ax  = fig.add_subplot( 211 )
# ax.imshow( alphas[ 0 ] )
# ax  = fig.add_subplot( 212 )
# ax.imshow( _alphas )
# fig.canvas.draw( )
# plt.show( )
