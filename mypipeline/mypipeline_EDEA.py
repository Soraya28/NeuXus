#conda activate neuxus
#cd C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\code\MRI_EEG\NeuXus


#open LSL Viewer
#open LabRecorder

#https://github.com/Soraya28/NeuXus/tree/master/utils/train-LSTM-model


from neuxus.nodes import *
from bsl import StreamReceiver
import time

##=========================== Settings

# data_path = r'./data/sub-01_ses-inside2_task-neurowMIMO_run-02.vhdr'
weight_path = r'C:\Users\BROSS\OneDrive - unige.ch\EEG - fMRI visual attention - 2022 - 2025\code\MRI_EEG\NeuXus\mypipeline\model\weights-input-500.pkl' #'./model/weights-input-500.pkl'
MRI_marker = 'R128' # 'Response/R128' is the marker of the start of every MRI volume for BrainVision
sfreq = 5000 #initial sampling frequency
downsampling_freq = int(sfreq/ 250) #to have 500Hz
#used to be sfreq/250
stream_name= 'BrainAmpSeries-Dev_1'
bufsize=1
winsize=1

##=========================== Pipeline
## Receive a signal from RDA stream
#https://laseeb.github.io/NeuXus/io.html
#rdaport = 51244 #output port
#signal = io.RdaReceive(rdaport=rdaport) 
# # signal = read.Reader(data_path)
## Attributes:
##       - output (Port): output port
##       - marker_output (Port): output marker portraw

# Connects to all available streams
receiver= StreamReceiver(bufsize=bufsize, winsize=winsize, stream_name=stream_name)
time.sleep(bufsize)
# Update each stream buffer with new data
receiver.acquire()
# Retrieve buffer/window for the stream named 'StreamPlayer'
#data, timestamps = sr.get_window(stream_name=stream_name)
raw, timestamps = receiver.get_buffer(return_raw=True)


raw.set_channel_types({'ECG': 'ecg'})
if 'TRIGGER' in raw.ch_names:  # which is the case if using BSL
    raw.drop_channels('TRIGGER')  # drop channel trigger of BSL
#raw.pick(picks='eeg')
raw.set_montage('standard_1020')



# ## Create Marker channels
# marker_output = bsl.triggers.LSLTrigger
from neuxus.chunks import Port
marker_output = Port()
marker_output.set_parameters(
            data_type='marker',
            channels=['Markers'],
            sampling_frequency=0,
            meta='')

# Node.log_instance(self, {
#     'marquers output': self.marker_output.id,
#     'channels': self._channels,
#     'sampling frequency': self._frequency})



## Send to a LSL stream
signal_m_lsl = io.LslSend(marker_output, #signal.marker_output
                          'marker', 
                          type='Markers', 
                          format='string')



## ===== Correct the signal from GA
#https://github.com/Soraya28/NeuXus/blob/master/neuxus/nodes/correct.py

#Set attribute for GA correction
# output.set_parameters(data_type='signal',
#             channels=channels,
#             sampling_frequency=sfreq,
#             meta='')
raw.data_type='signal'
raw.channels = raw.info['ch_names']
raw.sampling_frequency = raw.info['sfreq']
raw.meta = ''
raw.epoching_frequency = None #1/1.76 #todeduce from MRI trigger

signal_ga = correct.GA(raw, #signal.output
                       start_marker= MRI_marker, 
                       marker_input_port= marker_output #signal.marker_output
                       )  

#Visualize it
#https://laseeb.github.io/NeuXus/_modules/neuxus/nodes/display.html#Graz
# output.id = 1
# display.Graz(output)                        

signal_ds = filter.DownSample(signal_ga.output, downsampling_freq)


signal_pa = correct.PA(signal_ds.output, 
                       weight_path, 
                       marker_input_port=signal_ga.marker_output, 
                       start_marker='Start of GA subtraction', 
                       stride=50)


## Send to a LSL stream
#send as EEG and string markers
signal_pa_lsl = io.LslSend(signal_pa.output, 
                           'signal_pa', 
                           type='EEG')

signal_pa_m_lsl = io.LslSend(signal_pa.marker_output, 
                             'marker_pa', 
                             type='Markers', 
                             format='string')


#now retrieve LSL to compute LSL metric