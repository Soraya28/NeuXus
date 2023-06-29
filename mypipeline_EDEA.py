#conda activate test

#cd C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\code\MRI_EEG\NeuXus
#neuxus mypipeline_EDEA.py -l DEBUG
#to use neuxus downloaded via pip


#bug for now
#modifying neuxus from venv
#C:\Users\BROSS\anaconda3\envs\test\Lib\site-packages\neuxus

#to use local neuxus
#nfbmri
#cd C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\code\MRI_EEG\NeuXus\mypipeline
#python mypipeline_EDEA.py

#open LSL Viewer
#open LabRecorder

#https://github.com/Soraya28/NeuXus/tree/master/utils/train-LSTM-model

#notes
#debug print on https://github.com/LaSEEB/NeuXus/blob/81d1779c02e8dcda0236f2698f9490799714598f/neuxus/node.py#L46


#to use local neuxus forked and modified
# import sys
# mypath = r"C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\code\MRI_EEG\NeuXus\neuxus"
# sys.path.insert(0, mypath)

from neuxus.nodes import read, correct, filter, select, io, log
#from neuxus.nodes import *
import time

##=========================== Settings

data_path = r"\\nasac-m2\m-GVuilleumier\GVuilleumier\groups\sorayab\DATABASE\02.eeg_with_irm_test\sub-pilot020\ses-02\eeg\pilot020ses02.vhdr" 
#r"\\nasac-m2\m-GVuilleumier\GVuilleumier\groups\sorayab\DATABASE\02.eeg_with_irm_test\sub-pilot020\ses-01\eeg\pilot20.vhdr" #_ses02
#r"C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\test\pilot020ses02.vhdr"
#"\\nasac-m2\m-GVuilleumier\GVuilleumier\groups\sorayab\DATABASE\02.eeg_with_irm_test\sub-pilot020\ses-02\eeg\pilot020ses02.vhdr"
#vhdr #for replay

weight_path = r'.\model\weights-input-500.pkl' #'./model/weights-input-500.pkl'
MRI_marker = 'Response/R128' 
#'Response/R128' #'R128' # 'Response/R128' is the marker of the start of every MRI volume for BrainVision
#(in case the data is read from a Brain Vision file it is 'Response/R128'; in case it's streamed by Brain Vision Recorder, it is 'R128')
#Response,R128 #"Response/R128"

sfreq = 5000 #initial sampling frequency 5000 Hz
downsampling_freq = int(sfreq/ 250) #sfreq/ 10 to have 500Hz
TR = 0.8 #TR of the MRI sequence 
#TODO offline diff marker





##=========================== Read data
signal = read.Reader(data_path, min_chunk_size=10)
#min_chunk_size (int > 0): default is 4, minimum of rows to send per chunk ???

# signal = io.RdaReceive(rdaport=51244)

## Receive a signal from RDA stream
#https://laseeb.github.io/NeuXus/io.html
#rdaport = 51244 #output port
#signal = io.RdaReceive(rdaport=rdaport) 
# # signal = read.Reader(data_path)
## Attributes:
##       - output (Port): output port
##       - marker_output (Port): output marker portraw


signal_raw = io.LslSend(signal.output, 'raw_signal', type='signal') #to have on lsl for inspection
marker_raw_lsl = io.LslSend(signal.marker_output, 
                            'marker_raw', type='marker', 
                            format='string') #to have on lsl for inspection

#log.Print(signal.output) #to have df


##=========================== GA correction
#input Port2
signal_ga = correct.GA(signal.output, 
                       marker_input_port=signal.marker_output, 
                       start_marker=MRI_marker, 
                       min_wins=10, max_wins=30, 
                       tr=TR, fs=sfreq)



#send markers
marker_ga_lsl = io.LslSend(signal_ga.marker_output, 'marker_ga', type='marker', format='string')


#downsample
signal_dw = filter.DownSample(signal_ga.output, downsampling_freq)
signal_ga_lsl = io.LslSend(signal_dw.output, 'signal_ga', type='signal') #to have on lsl for inspection
#log.Print(marker_ga_lsl.output) 



#https://github.com/Soraya28/NeuXus/blob/master/neuxus/nodes/correct.py

#Set attribute for GA correction
# output.set_parameters(data_type='signal',
#             channels=channels,
#             sampling_frequency=sfreq,
#             meta='')
# raw.data_type='signal'
# raw.channels = raw.info['ch_names']
# raw.sampling_frequency = raw.info['sfreq']
# raw.meta = ''
# raw.epoching_frequency = None #1/1.76 #todeduce from MRI trigger


##=========================== PA correction

signal_dw_ecg = select.ChannelSelector(signal_dw.output, 'name', ['ECG'])
signal_dw_ecg_fi = filter.ButterFilter(signal_dw_ecg.output,  0.5, 30) #not taken into account


signal_pa = correct.PA(signal_dw.output, #signal_dw.output,
                       weight_path, 
                       marker_input_port=signal_ga.marker_output, 
                       start_marker='Start of GA subtraction', 
                       stride=50, 
                       filter_ecg=False, #filter_ecg=True,
                       numba=True)
## will have 2 markers
#R peak
#R peak fixed 
# Optional markers. If you want to record the detected R peaks to use offline, 
# I recommend using the 'R peak fixed'. 
# The normal R peaks are updated every detection, so they can be numerous and regarding the same ECG points. 
# The 'R peak fixed' correspond to the last update (and hence, is also more robust)

## stride
# lim2 becomes a position in the detection window in respect not to its start, but to it's (length - self.stride). Whenever it passes self.stride, a new detection is triggered.
# self.win_len - self.stride - self.margin  # Hold limit. Point in the detection window above which data is held until next detection to be output
#         self.reached_hold_limit = False

# min_wins=10, max_wins=20, min_hc=0.4, max_hc=1.5, 
#                     short_sight='both', margin=0.1, thres=0.05,
# marker_input_port=None, start_marker='Start of GA subtraction', stride=50, min_wins=10, max_wins=20, min_hc=0.4, max_hc=1.5, short_sight='both', margin=0.1, thres=0.05, filter_ecg=False, numba=True)
#numba to False to speed up beginning for test



#send markers
signal_pa_lsl = io.LslSend(signal_pa.output, 'signal_pa', type='signal')
marker_pa_lsl = io.LslSend(signal_pa.marker_output, 'marker_pa', type='marker', format='string')
# print(marker_pa_lsl)

