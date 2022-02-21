from dataclasses import dataclass, fields
from datetime import datetime
import numpy as np
import pandas as pd

ROTARY_ENCODER_UNITS_PER_TURN = 8845.0
format_string = "%Y-%m-%d %H:%M:%S.%f" # for parsing the time strings

@dataclass
class Reward:
    """Holds information about a reward event in a logfile"""
    date_time: datetime
    X: float
    Z: float
    reward_type: str = None

    def __eq__(self, other):
        if isinstance(other, Reward):
            return self.X == other.X and self.Z == other.Z
        return NotImplemented
    def __key(self):
        return (self.X, self.Z)
    def __hash__(self):
        return hash(self.__key())
    def __lt__(self, other):
        if isinstance(other, Reward):
            return self.date_time < other.date_time
        return NotImplemented

@dataclass
class LogFilePositionLine:
    """Class for keeping track of position information on a line of a logfile"""
    date_time: datetime
    X: float
    Z: float
    Theta: float
    MX: float = 0.0
    MY: float = 0.0
    GainX: float = 0.0
    GainY: float = 0.0
    Fading: int = 0
    RealTimeGainX: int = 0
    RealTimeGainY: int = 0
    Dark: int = 0

    def __iter__(self):
        for field in fields(self):
            yield getattr(self, field.name)
    def __key(self):
        return (self.date_time)
    def __hash__(self):
        return hash(self.__key())
    def __eq__(self, other):
        if isinstance(other, LogFilePositionLine):
            return self.__key() == other.__key()
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other, LogFilePositionLine):
            return self.date_time < other.date_time
        return NotImplemented

class LogFileParser:
    def __init__(self, log_file_name: str):
        with open(log_file_name, 'r') as logfile:
            lines = logfile.readlines()
        # 1) deal with all the lines containing the position of the mouse
        log_pos_lines = [line for line in lines if 'GainX' in line]
        loglines = []
        for line in log_pos_lines:
            items = line.split()
            date_time = items[0] + " " + items[1]
            dt = datetime.strptime(date_time, format_string)
            X = self.__get_float_val__(items[2])
            Z = self.__get_float_val__(items[3])
            theta = np.rad2deg(self.__get_float_val__(items[4]) / ROTARY_ENCODER_UNITS_PER_TURN)
            MX = self.__get_float_val__(items[6])
            MY = self.__get_float_val__(items[7])
            GainX = self.__get_float_val__(items[8])
            GainY = self.__get_float_val__(items[9])
            Fading = self.__get_float_val__(items[10])
            RealTimeGainX = self.__get_int_val__(items[11])
            RealTimeGainY = self.__get_int_val__(items[12])
            Dark = RealTimeGainX = self.__get_int_val__(items[13])
            loglines.append(LogFilePositionLine(
                dt, X, Z, theta, MX, MY,
                GainX, GainY, Fading, RealTimeGainX, RealTimeGainY, Dark))
        # now get the unique entries in the position data
        # this is only possible due to the custom methods defined
        # for the LogFilePositionLine class (__lt__, __eq__ & __hash__)
        self.PosLines = list(set(loglines)) # unordered so...
        self.PosLines.sort()
        # 2) extract all the reward-related information - all unique timestamps
        log_reward_lines = [line for line in lines if 'Reward'in line]
        rewards = []
        delivered_rewards= []
        for line in log_reward_lines:
            if 'RewardPositioned' in line:
                r = self.__get_reward__(line)
                r.reward_type = 'Automatic'
                rewards.append(r)
            if 'Manual Reward_activated' in line:
                r = self.__get_reward__(line)
                r.reward_type = 'Manual'
                rewards.append(r)
            if 'Reward_delivered' in line:
                r = self.__get_reward__(line)
                r.reward_type = 'Delivered'
                delivered_rewards.append(r)
        self.Rewards = rewards
        self.DeliveredRewards = delivered_rewards
    def make_dataframe(self):
        # Get the unique times for all events in the logfile
        # be they position or reward occurences. These are used
        # as the indices for the pandas DataFrame
        pos_lines_set = set([line.date_time for line in self.PosLines])
        reward_set = set([line.date_time for line in self.Rewards])
        delivered_reward_set = set([line.date_time for line in self.DeliveredRewards])
        unique_times = list(set.union(pos_lines_set, reward_set, delivered_reward_set))
        unique_times.sort()
        first_time = unique_times[0]
        unique_times = [times - first_time for times in unique_times]
        d = {'PosX': pd.Series([line.X for line in self.PosLines], index=[line.date_time - first_time for line in self.PosLines]),
             'PosY': pd.Series([line.Z for line in self.PosLines], index=[line.date_time - first_time for line in self.PosLines]),
            'Rewards': pd.Series([line for line in self.Rewards], index=[line.date_time - first_time for line in self.Rewards]),
            'DeliveredRewards': pd.Series([line for line in self.DeliveredRewards], index=[line.date_time - first_time for line in self.DeliveredRewards])
        }
        return pd.DataFrame(d, index=unique_times)
    def __get_float_val__(self, line: str) -> float:
        return float(line.split("=")[-1])
    def __get_int_val__(self, line: str) -> int:
        return int(line.split("=")[-1])
    def __get_reward__(self, line: str) -> Reward:
        items = line.split()
        date_time = items[0] + " " + items[1]
        dt = datetime.strptime(date_time, format_string)
        X = self.__get_float_val__(items[-2])
        Z = self.__get_float_val__(items[-1])
        return Reward(dt, X, Z)
    def getX(self) -> list:
        return [line.X for line in self.PosLines]
    def getZ(self) -> list:
        return [line.Z for line in self.PosLines]
    def getTheta(self) -> list:
        return [line.Theta for line in self.PosLines]
    def getPosTimes(self) -> list:
        return [line.date_time for line in self.PosLines]
    def summarise(self):
        times = self.getPosTimes()
        print(f"Trial duration(s): {(times[-1]-times[0]).total_seconds()}")
        total_rewards = len(self.Rewards)
        print(f"Total number of rewards: {total_rewards}")
        print(f"Number of rewards delivered: {len(self.DeliveredRewards)}")