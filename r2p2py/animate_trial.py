import matplotlib.pylab as plt
from matplotlib.patches import Ellipse
import matplotlib.animation as animation
import numpy as np
from numpy import polysub
import pandas as pd
import argparse
from r2p2py.logfile_parser import LogFileParser, Reward

class LogFileAnimator:
    def __init__(self, fname: str, start_in_seconds: int = 200) -> None:
        self.logfile = LogFileParser(fname)
        self.df = self.logfile.make_dataframe()
        self.start_time = self.df.iloc[0].name # a pandas time delta
        self.user_start = start_in_seconds
        self.time_elapsed = self.start_time + pd.Timedelta(self.user_start, 'sec')
        self.dt = 3
        self.plot_window = pd.Timedelta(self.dt, 'sec') # in seconds
        self.current_rewards = dict()
    def position(self) -> list:
        """Return a list of X,Y positions to plot"""
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        x = df.PosX
        y = df.PosY
        idx = np.logical_or(np.isnan(x), np.isnan(y))
        return (x[~idx], y[~idx])
    def mousehead(self) -> tuple:
        """Return a tuple of X,Y positions to plot the mouses noggin"""
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        return (df.PosX[-1], df.PosY[-1])
    def reward_locations(self):
        """Return a tuple of X,Y positions to plot the reward locations"""
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        found_rewards = ~pd.isna(df.reward_type)
        if np.any(found_rewards):
            sub_df = df[found_rewards]
            for _, row in sub_df.iterrows():
                this_reward = (row.rX, row.rZ)
                if 'Delivered' not in row.reward_type:
                    self.current_rewards[this_reward] = row.reward_type
        if np.any(found_rewards):
            sub_df = df[found_rewards]
            for _, row in sub_df.iterrows():
                this_reward = (row.rX, row.rZ)
                if 'Delivered' in row.reward_type:
                    if this_reward in self.current_rewards:
                        self.current_rewards.pop(this_reward)
        
        return list(self.current_rewards.keys())
    def step(self, dt):
        self.time_elapsed += pd.Timedelta(dt*5,'seconds')

def run_animation(fname: str, start_time: int = 0, duration: int = 100, save: bool = False):
    log_animator = LogFileAnimator(fname, start_time)
    dt = 1./50
    x = log_animator.logfile.getX()
    z = log_animator.logfile.getZ()
    xlims = (np.min(x)-1, np.max(x)+1)
    ylims = (np.min(z)-1, np.max(z)+1)

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                        xlim=xlims, ylim=ylims)
    ax.axis('off')
    ax.plot(x, z, '-', lw=1, color=[0.8627, 0.8627, 0.8627])
    line, = ax.plot([], [], '-', lw=3, color='orange')
    mouse_head = Ellipse([],0.35,0.35,[])
    reward_markersize = 16
    reward_blobs, = ax.plot([], [], 'bo', ms=reward_markersize)
    time_text = ax.text(0.78, 0.04, '', transform=ax.transAxes)

    # initialise the animation
    def init():
        """initialize the animation"""
        x = log_animator.logfile.getX()
        z = log_animator.logfile.getZ()
        line.set_data(x, z)
        mouse_head_pos = log_animator.mousehead()
        mouse_head.center = mouse_head_pos[0:2]
        mouse_head.angle = mouse_head_pos[-1]
        ax.add_patch(mouse_head)
        reward_blobs.set_data([], [])
        time_text.set_text('')
        return line, mouse_head, reward_blobs, time_text

    def animate(i):
        """perform animation step"""
        log_animator.step(dt)
        line.set_data(*log_animator.position())
        mouse_head_pos = log_animator.mousehead()
        mouse_head.center = mouse_head_pos[0:2]
        mouse_head.angle = mouse_head_pos[-1]
        reward_locations = np.array(log_animator.reward_locations())
        if reward_locations.size > 0:
            reward_blobs.set_data(reward_locations[:,0], reward_locations[:,1])
            reward_blobs.set_markersize(reward_markersize)
        time_text.set_text(f'Time(s): {log_animator.time_elapsed.seconds}')
        return line, mouse_head, reward_blobs, time_text

    from time import time
    t0 = time()
    animate(0)
    t1 = time()
    interval = 1000 * dt - (t1 - t0)

    ani = animation.FuncAnimation(fig, animate, frames=duration, repeat=False,
                                interval=interval, blit=True, init_func=init)

    if save:
        # FFwriter = animation.FFMpegWriter(fps=30)
        from pathlib import Path
        savename = Path(fname)
        savename = savename.with_suffix(".mp4")
        ani.save(savename, fps=30, dpi=300, extra_args=['-vcodec', 'libx264']) 
        plt.close()
        return

    plt.show()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--f", type=str, help="Path to the log file")
parser.add_argument("--s", type=int, default=0, help="When in seconds to start the animation from")
parser.add_argument("--length", type=int, default=300, help="Number of seconds to run animation for")
parser.add_argument("--save", action='store_true', help="Whether to save the animation or not")
args = parser.parse_args()
run_animation(args.f, args.s, args.length*10, args.save)