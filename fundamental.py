import pandas as pd
import numpy as np
import pynverse
import matplotlib.pyplot as plt
r=pd.read_csv("/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230719-1008031689732483.0218832-0_speed_emission.csv")
# r=pd.read_csv("/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230719-1044481689734688.7560048-0_speed_emission.csv")

flow=r["flow_1"]
density=r["density"]
# rmean=r["episode_reward_mean"]
# x=[i for i in range(486)]
# plt.scatter(density,flow)
plt.xlabel('density')
plt.ylabel('flow')
plt.title('fundamental_diagram')
# plt.fill_between(x,rmax,rmin,facecolor="green",alpha=0.3)

# print(rmax)
# x=[0,0.0013,0.0032,0.00507814,0.00722536,0.00856738,0.0107146,0.0117882,0.0131302,0.015,0.0158,0.016,0.0163,0.0165,0.01742,0.0183,0.0194,0.0205,0.0223,0.02655,0.03621,0.04749,0.052317,0.0606376,0.0654688,0.07,0.0746,0.0804994,0.085867,0.0891,0.0961,0.101435,0.1063,0.12,0.12546]
# y=[0,0.051,0.1,0.1487,0.184585,0.225585,0.266585,0.28965,0.315273,0.346,0.37677,0.38,0.39,0.396,0.4165,0.41,0.40,0.39,0.38,0.376774,0.3614,0.3486,0.34474,0.337,0.3268,0.32,0.3127,0.289648,0.276836,0.273,0.24865,0.24,0.2141,0.165,0.1402]
x=[0,0.01,0.0145,0.02,0.0232,0.02674,0.032,0.05329,0.06656,0.0775,0.0867,0.094,0.1]
y=[0,0.254,0.3678,0.464,0.502,0.5228,0.5,0.34,0.32,0.31,0.29,0.25,0.196]
parameter=np.polyfit(x,y,5)
p=np.poly1d(parameter)
# print(p)
# print (0.35128858)/(pynverse.inversefunc(p, y_values=0.35128858, domain=[0.024, 0.11]))
y1=p(x)
plt.plot(x,y1,)
plt.show()