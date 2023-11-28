# import csv
# import json
# def fk_rl(str):
#     if str == 'FAKE':
#         return 0
#     else:
#         return 1
# def transcsv(jsonpath, csvpath, strpath):
#     json_file = open(jsonpath, 'r', encoding='utf8')
#     csv_file = open(csvpath, 'w')
#     writer = csv.writer(csv_file)
#     writer.writerow(["video_id", "labels"])
#     # 读文件
#     ls = json.load(json_file)  # 将json格式的字符串转换成python的数据类型，解码过程
#     data = list((key, item) for key, item in ls.items())  # 获取列名,即key
#     for line in data:
#         writer.writerow([strpath + line[0], fk_rl(list(line[1].items())[0][1])])
#     # 关闭文件
#     json_file.close()
#     csv_file.close()
#
# transcsv('/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq/result.json','/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq/result.csv','/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq')

# import json
# import csv
#
# """
# 需求：将json中的数据转换成csv文件
# """
# def csv_json():
#     # 1.分别 读，创建文件
#     json_fp = open("/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq/result.json", "r",encoding='utf-8')
#     csv_fp = open("/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq/result.csv", "w",encoding='utf-8',newline='')
#
#     # 2.提出表头和表的内容
#     data_list = json.load(json_fp)
#     sheet_title = data_list[0].keys()
#     # sheet_title = {"姓名","年龄"}  # 将表头改为中文
#     sheet_data = []
#     for data in data_list:
#         sheet_data.append(data.values())
#
#     # 3.csv 写入器
#     writer = csv.writer(csv_fp)
#
#     # 4.写入表头
#     writer.writerow(sheet_title)
#
#     # 5.写入内容
#     writer.writerows(sheet_data)
#
#     # 6.关闭两个文件
#     json_fp.close()
#     csv_fp.close()
#
#
# if __name__ == "__main__":
#     csv_json()

# -*- coding: utf-8 -*-
import json

# 主程序，执行入口
if __name__ == '__main__':
    # try except Python的异常处理机制
    try:
        # with Python中的上下文管理器，会帮我们释放资源，比如 关闭文件句柄
        # open 函数为Python内建的文件读取函数，r代表只读
        with open('/home/jt/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_0350baea_2023-02-27_16-02-00ib62ypkx/params.json', 'r',encoding='utf8') as f:
            # 解析一个有效的JSON字符串并将其转换为Python字典
            data = json.load(f)
        # 使用 ，连接列表中的值
        # data[0]是一个字典类型，一个星号代表展开键，两个星号（**）代表展开字典的值
        dic_str = json.loads(str(data).replace("'", "\""))
        for json_dict in dic_str:
            _id = json_dict['_id']
            print("The id is {}".format(_id))
    #     output = ','.join([*papers[0]])
    #     # 遍历 字典列表data
    #     for obj in data:
    #         # 将结果转化为字符串，累加到output中
    #         # f 为f-string格式化，将大括号中的表达式替代
    #         output += f'\n{obj["name"]},{obj["height"]},{obj["weight"]}'
    #     # 将结果写到到output.csv中
    #     with open('/home/wu/ray_results/free_ramp_example/PPO_MultiAgentHighwayPOEnv-v0_f145b272_2022-12-07_21-06-201a44m0jq/result.csv', 'w') as f:
    #         f.write(output)
    except Exception as ex:
        print(f'Error: {str(ex)}')