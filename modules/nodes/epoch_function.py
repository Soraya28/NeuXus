import sys

import pandas as pd
import numpy as np
from scipy import signal

sys.path.append('../..')

from modules.node import Node


class Average(Node):
    """TO DO
    Attributes:
        input_: get DataFrame and meta from input_ port
        output_: output GroupOfPorts
    Args:
        duration: duration of epochs
    """

    def __init__(self, input_port):
        Node.__init__(self, input_port)

        assert self.input.is_epoched

        self.output.set_parameters(
            channels=self.input.channels,
            frequency=self.input.epoching_frequency,
            meta=self.input.meta)

        self.output.set_non_epoched()

        self.value = np.array([0] * len(self.input.channels))

        Node.log_instance(self, {'output frequency': self.input.epoching_frequency})

        # TO DO terminate

    def update(self):
        for epoch in self.input:
            mean = epoch.mean()
            self.output.set_from_df(pd.DataFrame(
                mean, columns=[epoch.index[-1]]).transpose())
            self.value = np.array(mean.values)


class UnivariateStat(Node):
    """Mean, Variance, Median, etc. on the incoming epoched Signal
    perform calculation on each coming epoch and saved last value in value
    attribute
    Attributes:
      - output: output GroupOfPorts
      - value: last value calculated (on the last epoch come)
    Args:
      - input (Port): port of incoming data
      - stat (str):
    """

    def __init__(self, input_port, stat, q=None, q1=None, q2=None):
        Node.__init__(self, input_port)

        assert self.input.is_epoched

        assert stat in ['mean', 'min', 'max', 'range', 'std', 'median', 'quantile', 'iqr']
        self._stat = stat

        self.output.set_parameters(
            channels=self.input.channels,
            frequency=self.input.epoching_frequency,
            meta=self.input.meta)
        self.output.set_non_epoched()

        self.value = np.array([0] * len(self.input.channels))

        if self._stat == 'quantile':
            assert 0 <= q and q <= 1
            self._q = q
            Node.log_instance(self, {
                'output frequency': self.input.epoching_frequency,
                'stat': self._stat,
                'quantile': self._q})

        elif self._stat == 'iqr':
            assert 0 <= q1 and q1 <= q2 and q2 <= 1
            self._q1 = q1
            self._q2 = q2
            Node.log_instance(self, {
                'output frequency': self.input.epoching_frequency,
                'stat': self._stat,
                'quantile1': self._q1,
                'quantile2': self._q2})
        else:
            Node.log_instance(self, {
                'output frequency': self.input.epoching_frequency,
                'stat': self._stat})

    def update(self):
        for epoch in self.input:
            if self._stat == 'mean':
                stat = epoch.mean()
            elif self._stat == 'min':
                stat = epoch.min()
            elif self._stat == 'max':
                stat = epoch.max()
            elif self._stat == 'std':
                stat = epoch.std()
            elif self._stat == 'range':
                stat = epoch.max() - epoch.min()
            elif self._stat == 'quantile':
                stat = epoch.quantile(q=self._q)
            elif self._stat == 'median':
                stat = epoch.median()
            elif self._stat == 'iqr':
                stat = epoch.quantile(q=self._q2) - epoch.quantile(q=self._q1)
            self.output.set_from_df(pd.DataFrame(
                stat, columns=[epoch.index[-1]]).transpose())
            self.value = np.array(stat.values)


class Windowing(Node):
    """Mean, Variance, Median, etc. on the incoming epoched Signal
    perform calculation on each coming epoch and saved last value in value
    attribute
    Attributes:
      - output: output GroupOfPorts
      - value: last value calculated (on the last epoch come)
    Args:
      - input (Port): port of incoming data
      - stat (str):
    """

    def __init__(self, input_port, window):
        Node.__init__(self, input_port)

        assert self.input.is_epoched

        assert window in ['blackman', 'hanning', 'hamming', 'triang']
        self._window = window

        self.output.set_parameters(
            channels=self.input.channels,
            frequency=self.input.frequency,
            meta=self.input.meta)

        self.output.set_epoched(
            epoching_frequency=self.input.epoching_frequency)

        self._buffered_windows = {}

        Node.log_instance(self, {'window': self._window})

    def update(self):
        for epoch in self.input:
            nb_rows = len(epoch)
            if nb_rows not in self._buffered_windows:
                print('rcalculed')
                if self._window == 'blackman':
                    self._buffered_windows[nb_rows] = signal.blackman(nb_rows)
                elif self._window == 'hanning':
                    self._buffered_windows[nb_rows] = signal.hanning(nb_rows)
                elif self._window == 'hamming':
                    self._buffered_windows[nb_rows] = signal.hamming(nb_rows)
                elif self._window == 'triang':
                    self._buffered_windows[nb_rows] = signal.triang(nb_rows)
            self.output.set_from_df((epoch.transpose() * self._buffered_windows[nb_rows]).transpose())
