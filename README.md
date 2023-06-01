# NeuXus

NeuXus is a modular software written in Python that allows to easily create and execute pipelines in real time. NeuXus is specifically designed for BCI real-time processing and classification.

It offers a lot of possibilities, many basic functions are already implemented so that the first pipelines can be quickly created. For more specific functions, users can develop and use their own functions.


## Installation

### Set the venv

NeuXus requires Python 3.7+, verify your Python version with:
```
python --version
```
Create environment : 
```
conda create --name neuxus --clone nfb

conda activate neuxus
```

Install NeuXus with:
```
pip install neuxus

pip install numba
```

Download [BrainVision LSL Viewer] (https://www.brainproducts.com/downloads/more-software/)

Download [LabRecorder] (https://github.com/labstreaminglayer/App-LabRecorder/releases/tag/v1.16.4)
## Train the LSTM for PA correction
Cf [train-LSTM] (https://github.com/Soraya28/NeuXus/tree/master/utils/train-LSTM-model)

## Run

### Run EDEA pipeline from NeuXus
See for more information, read the [Documentation](https://laseeb.github.io/NeuXus/index.html) or the published [paper](https://arxiv.org/abs/2012.12794)


```
cd mypipeline
neuxus mypipeline_EDEA.py -l DEBUG -f
```

optional arguments:
  -h, --help            show this help message and exit
  -f, --file            Store logs in a log file, default is on cmd window
  -l {DEBUG,INFO}, --loglevel {DEBUG,INFO}
                        Specify the log level, default is INFO
  -e, --example         To run an example from NeuXus

Open LSL Viewer to see the different stream of data

image.png

## Citation
### When using for your research, please cite:
```
@misc{vourvopoulos2020neuxus,
      title={NeuXus: A Biosignal Processing and Classification Pipeline for Real-Time Brain-Computer Interaction}, 
      author={Athanasios Vourvopoulos and Simon Legeay and Patricia Figueiredo},
      year={2020},
      eprint={2012.12794},
      archivePrefix={arXiv},
      primaryClass={cs.HC}
}
```
