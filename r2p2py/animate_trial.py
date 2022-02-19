import matplotlib.pylab as plt
from matplotlib.patches import Ellipse
import matplotlib.animation as animation
import numpy as np
import pandas as pd
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
    def position(self) -> list:
        """Return a list of X,Y positions to plot"""
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        return (df.PosX, df.PosY)
    def mousehead(self) -> tuple:
        """Return a tuple of X,Y positions to plot the mouses noggin"""
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        return (df.PosX[-1], df.PosY[-1])
    def reward_locations(self):
        """Return a tuple of X,Y positions to plot the reward locations"""
        current_rewards = []
        df = self.df[self.time_elapsed:self.time_elapsed+self.plot_window]
        found_rewards = ~pd.isna(df.Rewards)
        if np.any(found_rewards):
            sub_df = df[found_rewards]
            for _, row in sub_df.iterrows():
                current_rewards.append(row.Rewards)
        delivered_rewards = []
        found_rewards = ~pd.isna(df.DeliveredRewards)
        if np.any(found_rewards):
            sub_df = df[found_rewards]
            for _, row in sub_df.iterrows():
                delivered_rewards.append(row.DeliveredRewards)
        rewards_to_plot = set.intersection(set(current_rewards), set(delivered_rewards))
        rewards_to_plot = list(rewards_to_plot)
        rewards_to_plot.sort()
        return [(line.X, line.Z) for line in rewards_to_plot]
    def step(self, dt):
        self.time_elapsed += pd.Timedelta(dt*5,'seconds')

fname = "/home/robin/Downloads/20220212-204627.txt"
log_animator = LogFileAnimator(fname, 100)
dt = 1./50
x = log_animator.logfile.getX()
z = log_animator.logfile.getZ()
xlims = (np.min(x)-1, np.max(x)+1)
ylims = (np.min(z)-1, np.max(z)+1)

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=xlims, ylim=ylims)
ax.axis('off')
line1, = ax.plot(x, z, '-', lw=1, color=[0.8627, 0.8627, 0.8627])
line, = ax.plot([], [], '-', lw=3, color='orange')
mouse_head = Ellipse([],0.35,0.35,[])
# reward_blobs, = ax.plot([], [], 'bo', ms=6)
time_text = ax.text(0.78, 0.04, '', transform=ax.transAxes)

# initialise the animation
def init():
    """initialize the animation"""
    global log_animator, ax
    x = log_animator.logfile.getX()
    z = log_animator.logfile.getZ()
    line.set_data(x, z)
    mouse_head_pos = log_animator.mousehead()
    mouse_head.center = mouse_head_pos[0:2]
    mouse_head.angle = mouse_head_pos[-1]
    ax.add_patch(mouse_head)
    # reward_blobs.set_data([], [])
    time_text.set_text('')
    return line, mouse_head, time_text

def animate(i):
    """perform animation step"""
    global log_animator, dt, ax
    log_animator.step(dt)
    line.set_data(*log_animator.position())
    mouse_head_pos = log_animator.mousehead()
    mouse_head.center = mouse_head_pos[0:2]
    mouse_head.angle = mouse_head_pos[-1]
    xy = log_animator.reward_locations()
    print(len(xy))
    # reward_blobs.set_data(*log_animator.reward_locations())
    time_text.set_text(f'Time(s): {log_animator.time_elapsed.seconds}')
    return line, mouse_head, time_text

from time import time
t0 = time()
animate(0)
t1 = time()
interval = 1000 * dt - (t1 - t0)

ani = animation.FuncAnimation(fig, animate, frames=300,
                              interval=interval, blit=True, init_func=init)

plt.show()