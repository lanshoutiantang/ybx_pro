if __name__ == '__main__':

    # Importing the pandas library and giving it the alias pd.
    import pandas as pd

    # Importing the numpy library and giving it the alias np.
    import numpy as np

    # A module that allows you to print things in a pretty way.
    from pprint import pprint

    # # Reading the excel file and storing it in a dataframe.
    # person_data_frame = pd.read_excel('./person_data.xlsx')
    #
    # # Converting the dataframe into a list.
    # person_data_list = np.array(person_data_frame).tolist()
    #
    # # Printing the list of lists.
    # pprint(person_data_list)

    person_data_list = [['广东', 10432],
     ['山东', 9580], ['河南', 9402], ['四川', 8042], ['江苏', 7865], ['河北', 7185], ['湖南', 6568],
     ['安徽', 5950], ['湖北', 5724], ['浙江', 5442],
     ['广西', 4603], ['云南', 4597], ['江西', 4457], ['云南', 4597], ['江西', 4457], ['辽宁', 4375],
     ['黑龙江', 3840], ['陕西', 3754], ['山西', 3652], ['福建', 3524], ['贵州', 3245],
     ['重庆', 2884], ['吉林', 2736], ['甘肃', 2557], ['内蒙古', 1987], ['台湾', 2316],
     ['上海', 1876], ['新疆', 2181], ['北京', 1961], ['天津', 1294], ['海南', 876],
     ['香港', 712], ['宁夏', 654], ['青海', 578], ['西藏', 315], ['澳门', 56]]


    # Importing all the charts from the pyecharts library.
    from pyecharts.charts import *

    # Importing the options module from the pyecharts library and giving it the alias opts.
    from pyecharts import options as opts


    map = Map(init_opts=opts.InitOpts(theme='light',
                                            width='1250px',
                                            height='650px'))

    map.add('中华人民共和国人口分布（万人）',
                  data_pair=person_data_list,
                  maptype='china')

    map.set_global_opts(visualmap_opts=opts.VisualMapOpts(
        max_=230000,
        is_piecewise=True
    ))

    # Creating a html file called render.html.
    map.render()

