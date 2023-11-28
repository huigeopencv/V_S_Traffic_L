import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# r=pd.read_csv("/home/jt/flow_w_bottleneck/data/free_ramp_vsl_20230404-1147261680580046.8229532-0_emission.csv")
# # r=pd.read_csv("/home/jt/flow_w_vsl/1.csv")
# # r1=pd.read_csv("/home/jt/flow_w_vsl/3_vsl.csv")
# #
# # rmax=r["episode_reward_max"]
# # rmin=r["episode_reward_min"]
# # rmean=r["episode_reward_mean"]
# x=[i for i in range(1501)]
# sum1=sum( np.array(r['m_speed'][550:1160]))/(610)
# sum2=sum(np.array(r1['m_speed'][550:1160]))/610
# print(sum((np.array(r1['m_speed'][550:1160])-np.array(r['m_speed'][550:1160]))/np.array(r['m_speed'][550:1160]))/610)
# print(sum1,sum2,(sum2-sum1)/sum1)
# plt.plot(x,r['m_speed'])
# plt.plot(x,r1['m_speed'])
# plt.xlabel('step')

# plt.ylabel('speed(m/s)')
# plt.legend(['None','VSL'])
# # plt.fill_between(x,rmax,rmin,facecolor="green",alpha=0.3)
# plt.show()
# # print(rmax)

# r = pd.read_csv('/home/jt/0630/free_ramp_uncontrol_25002250250.csv')
# r1 = pd.read_csv("/home/jt/0630/free_ramp_uncontrol_17001530170.csv")
# r2 = pd.read_csv('/home/jt/0630/bottleneck_DRL_2500.csv')
# r3 = pd.read_csv('/home/jt/0630/bottleneck_DRL_1700.csv')
# x = [i*0.2 for i in range(1501)]
# plt.plot(x, r['m_speed'][0:1501])
# plt.plot(x, r1['m_speed'][0:1501])
# plt.plot(x, r2['m_speed'][0:1501])
# plt.plot(x, r3['m_speed'][0:1501])
# plt.legend(['Uncontrol_2500veh/h','Uncontrol_1700veh/h','DRL_Egoism_2500veh/h','DRL_Egoism_1700veh/h'])
# plt.xlabel("Time(s)")
# plt.ylabel("average_speed (m/s)")
# plt.grid()
# # plt.title("Bottleneck")
# plt.show()


# r = pd.read_csv('/home/jt/0712/Bottleneck_3000_speed_emission.csv')
# # r1 = pd.read_csv("/home/jt/0630/free_ramp_uncontrol_17001530170.csv")
# # r2 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230718-0939411689644381.6101058-0_speed_emission.csv')
# r2 = pd.read_csv('/home/jt/0712/Litaxing_3000_first_0714/bottleneck_litaxing_5_speed_emission.csv')
# # r3 = pd.read_csv('/home/jt/0630/bottleneck_DRL_1700.csv')
# x = [i*0.2 for i in range(1501)]
# plt.plot(x, r['m_speed'][0:1501])
# # plt.plot(x, r1['m_speed'][0:1501])
# plt.plot(x, r2['m_speed'][0:1501])
# # plt.plot(x, r3['m_speed'][0:1501])
# # plt.legend(['Uncontrol_2500veh/h','DRL_Altruism_2500veh/h'])#利他性
# plt.legend(['Uncontrol_3000veh/h','DRL_Egoism_3000veh/h'])#利己性
# plt.xlabel("Time(s)")
# plt.ylabel("Average_speed (m/s)")
# plt.grid()
# # plt.title("Bottleneck")
# plt.show()
# r = pd.read_csv('/home/jt/0712/Bottleneck_3000_speed_emission.csv')
# # r1 = pd.read_csv("/home/jt/0630/free_ramp_uncontrol_17001530170.csv")
# # r2 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230718-0939411689644381.6101058-0_speed_emission.csv')
# r2 = pd.read_csv('/home/jt/0712/Litaxing_3000_first_0714/bottleneck_litaxing_5_speed_emission.csv')
# r3 = pd.read_csv('/home/jt/0712/bottleneck_lijixing_1_speed_emission.csv')
# x = [i*0.2 for i in range(1501)]
# plt.plot(x, r['m_speed'][0:1501])
# # plt.plot(x, r1['m_speed'][0:1501])
# plt.plot(x, r2['m_speed'][0:1501])
# plt.plot(x, r3['m_speed'][0:1501])
# plt.legend(['Uncontrol_3000veh/h','DRL_Altruism_3000veh/h','DRL_Egoism_3000veh/h'])#利他性
# # plt.legend(['Uncontrol_2000veh/h','DRL_Egoism_2000veh/h'])#利己性
# plt.xlabel("Time(s)")
# plt.ylabel("Average_speed (m/s)")
# plt.grid()
# # plt.title("Bottleneck")
# plt.show()

# r = pd.read_csv('/home/jt/0712/Bottleneck_3000_speed_emission.csv')
# r6 = pd.read_csv('/home/jt/0712/Bottleneck_2500_speed_emission.csv')
# # r1 = pd.read_csv("/home/jt/0630/free_ramp_uncontrol_17001530170.csv")
# # r2 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230718-0939411689644381.6101058-0_speed_emission.csv')
# r2 = pd.read_csv('/home/jt/0712/Litaxing_3000_first_0714/bottleneck_litaxing_5_speed_emission.csv')
# r5 = pd.read_csv('/home/jt/0712/Litaxing_2500_first_0712/bottleneck_litaxin_1_speed_emission.csv')
# r3 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230719-1453511689749631.0292222-0_speed_emission.csv')
# r4 = pd.read_csv('/home/jt/0712/bottleneck_lijixing_1_speed_emission.csv')
# r7 = pd.read_csv('/home/jt/0712/Lijixing_2500_first_0713/bottleneck_lijixing_2_speed_emission.csv')
# # VSL_____2500
# x = [i*0.2 for i in range(1501)]
# # plt.plot(x, r['m_speed'][0:1501])
# # plt.plot(x, r1['m_speed'][0:1501])
# # plt.plot(x, r2['m_speed'][0:1501])
# # plt.plot(x, r3['m_speed'][0:1501])
# # plt.plot(x, r4['m_speed'][0:1501])
# mmm1=sum(r6['m_speed'][0:1501])#不控制2500
# mmm2=sum(r['m_speed'][0:1501])#不控制3000
# mmm3=sum(r7['m_speed'][0:1501])#利己2500
# mmm4=sum(r4['m_speed'][0:1501])#利己3000
# mmm5=sum(r5['m_speed'][0:1501])#利他2500
# mmm6=sum(r2['m_speed'][0:1501])#利他3000
# # mmm7=sum(r7['m_speed'][0:1501])
#
# print((mmm1-mmm3)/mmm1,(mmm2-mmm4)/mmm2,(mmm5-mmm1)/mmm1,(mmm6-mmm2)/mmm2)
# plt.legend(['Uncontrol_3000veh/h','DRL_Altruism_3000veh/h','VSL_3000veh/h','DRL_Egoism_3000veh/h'])#利他性
# # plt.legend(['Uncontrol_2000veh/h','DRL_Egoism_2000veh/h'])#利己性
# plt.xlabel("Time(s)")
# plt.ylabel("Average_speed (m/s)")
# plt.grid()
# # plt.title("Bottleneck")
# plt.show()


# 50%
# r = pd.read_csv("/home/jt/flow_w_vsl/data/Bottleneck_vsl_20231126-1414331700979273.5336773-0_speed_emission.csv")
# r1 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20231126-1408341700978914.146369-0_speed_emission.csv')
# 80%
r = pd.read_csv("/home/jt/flow_w_vsl/data/Bottleneck_vsl_20231126-1754111700992451.9100587-0_speed_emission.csv")
r1 = pd.read_csv('/home/jt/flow_w_vsl/data/Bottleneck_vsl_20231126-1752341700992354.5791001-0_speed_emission.csv')
# r2=pd.read_csv("/home/jt/flow_w_vsl/data/Bottleneck_vsl_20230820-2010251692533425.4211974-0_speed_emission.csv")
# r3 = pd.read_csv('/home/jt/0630/bottleneck_DRL_1700.csv')
x = [i*0.2 for i in range(1501)]
plt.plot(x, r['m_speed'][0:1501])
plt.plot(x, r1['m_speed'][0:1501])
# plt.plot(x, r2['m_speed'][0:1501])
# plt.plot(x, (r2['m_speed'][0:1501]+r1['m_speed'][0:1501])/2)
print((sum(r1['m_speed'][0:1501])-sum(r['m_speed'][0:1501]))/sum(r['m_speed'][0:1501]))
# plt.plot(x, r3['m_speed'][0:1501])
# plt.legend(['Uncontrol_2500veh/h','DRL_Altruism_2500veh/h'])#利他性
plt.legend(['Uncontrol_2500veh/h','VSL_2500veh/h'])#利己性
plt.xlabel("Time(s)")
plt.ylabel("Average_speed (m/s)")
plt.grid()
# plt.title("Bottleneck")
plt.show()





