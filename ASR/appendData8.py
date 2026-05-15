import requests
import os
import pandas as pd


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    # da1 = pd.read_excel(r"C:/Users/Administrator/Desktop/20条语料/20语条料.xlsx")
    # print(da1)
    # da2 = pd.read_excel(r"C:/Users/Administrator/Desktop/da2_output4.xlsx")
    # # 合并数据
    # da3 = pd.merge(da2, da1, how='left', left_on='trainBeforeName', right_on='序号')
    # with open(r"C:/Users/Administrator/Desktop/kunmingjust 22.txt", "r", encoding='utf-16-be') as f:
    #     data = f.readline().encode("utf-8").decode("utf-8-sig")
    #     print(data)
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # with open(r"C:/Users/Administrator/Desktop/kunmingjust 22.txt", "r") as f:
    #     data = f.readline()
    #     print(data)
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # 手打excel表
    # df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    # i = 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "我思故我在"}, ignore_index= True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "无巧不成书"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "如果是玫瑰它总会开花的"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "千里之行始于足下"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "人生是没有毕业的学校"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "近朱者赤近墨者黑"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "条条大路通罗马"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "理想是寻觅目标的思维"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "路遥知马力日久见人心"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "光阴似箭日月如梭"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "一万年太久只争朝夕"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "知识就是力量"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "黄金时代在我们面前而不在我们背后"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "滴水穿石不是力量大而是功夫深"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "生活没有目标就像航海没有指南针"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "天才是百分之一的灵感加上百分之九十九的汗水"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "闪光的未必都是金子而沉默的也不一定是石头"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "即使跌倒一百次也要一百零一次地站起来"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "把语言转化为行动比把行动转化为语言困难得多"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "当你为错过太阳而哭泣的时候那么你也要错过群星了"}, ignore_index=True)
    # df.rename(columns={"trainBeforeName":"序号", "trainLaterName":"描述"}, inplace= True)
    # print(df)
    # df.to_excel('C:/Users/Administrator/Desktop/20条语料/20语条料-df.xlsx')

    # 30s语音
    df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    i = 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "春天里，春姑娘唤醒了桃花，它急忙穿上了新装。她又摸了摸柳树，柳树立刻醒了过来，发出了嫩芽，在微风的吹拂下翩翩起舞。她又走过了迎春花的身旁，迎春花被惊醒了，它揉了揉眼睛，探出了一个个小脑袋。它们都在欢迎春姑娘的到来。"}, ignore_index= True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "春姑娘带着春风走到了小草的旁边，小草就被春风吹得摇摇晃晃，这个刚出生的小家伙好像站不稳似的。仙客来有了春风的光顾，他不停的点头哈腰。春雨呢？太懒了。即使人间有许多美好的东西，也不愿意到人间来玩一玩。庄稼太需要他了，真是“春雨贵如油”呀！春天小燕子又飞回来了，到处都是春天的气息。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "满天的乌云，黑沉沉地压下来。树上的叶子一动不动，蝉一声也不出。忽然一阵大风，吹得树枝乱摆。一只蜘蛛从网上垂下来，逃走了。闪电越来越亮，雷声越来越响。哗，哗，哗，雨下起来了。雨越下越大。往窗外望去，树啊，房子啊，都看不清了。渐渐地，渐渐地，雷声小了，雨声也小了。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "我忽然觉得自己仿佛就是一朵荷花，穿着雪白的衣裳，站在阳光里。一阵微风吹过来，我就翩翩起舞，雪白的衣裳随风飘动。不光是我一朵，一池的荷花都在舞蹈。风过了，我停止了舞蹈，静静地站在那儿。蜻蜓飞过来，告诉我清早飞行的快乐。小鱼在脚下游过，告诉我昨夜做的好梦……"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "人总是要死的，但死的意义有不同。中国古时候有个文学家叫做司马迁的说过：“人固有一死，或重于泰山，或轻于鸿毛。”为人民利益而死，就比泰山还重；替法西斯卖力，替剥削人民和压迫人民的人去死，就比鸿毛还轻。张思德同志是为人民利益而死的，他的死是比泰山还要重的。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "明月几时有？把酒问青天。不知天上宫阙，今夕是何年。我欲乘风归去，又恐琼楼玉宇，高处不胜寒。起舞弄清影，何似在人间。转朱阁，低绮户，照无眠。不应有恨，何事长向别时圆？人有悲欢离合，月有阴晴圆缺，此事古难全。但愿人长久，千里共婵娟。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "独立寒秋，湘江北去，橘子洲头。看万山红遍，层林尽染；漫江碧透，百舸争流。鹰击长空，鱼翔浅底，万类霜天竞自由。怅寥廓，问苍茫大地，谁主沉浮？携来百侣曾游，忆往昔，峥嵘岁月稠。恰同学少年，风华正茂；书生意气，挥斥方遒。指点江山，激扬文字，粪土当年万户侯。曾记否，到中流击水，浪遏飞舟。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "在漫长的人生道路上，尽管沉沉黑夜没有灯火照明，没有向导导航，但只要心中有梦想，你就能看清前方的路，你就能穿过黑夜走向黎明在漫长的人生道路上，尽管风雨交加，一路坎坷泥泞，但只要心中有梦想，你就会发现，你在风雨中走过的每一步都会留下深深的脚印，你就会在风雨过后迎来绚丽的彩虹。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "我不能想象这样一个人，他认为开棋的时候先走马而不是先走卒对他来说是英勇的壮举，而在象棋指南的某个犄角里占上一席可怜的位置，就意味着声名不朽，我不能想象，一个聪明人竟然能够在十年、二十年、三十年、四十年之中一而再、再而三地把他全部的思维能力都献给一种荒诞的事情——想尽一切办法把木头棋子王赶到木板棋盘的角落里，而自己却没有发狂成为疯子。"}, ignore_index=True)
    i = i + 1
    df = df.append({'trainBeforeName': i, 'trainLaterName': "失败并不可怕，关键是失败中蕴含了成功的先机，失去成功的先机最为可怕，一只手，常常是放错了地方，抬起这只自己的手，朝着自己的强项去发展，这只手带来的不就是简单的标准件的结果，更为重要的是这是一只能主动创造市场的手，这只手能充分发挥它的潜能，从而创造了这只手的最大价值，这就是一只摊开是放飞的想象，张开是创造的力量之手，有了这只手，一切都是新的。"}, ignore_index=True)

    df.rename(columns={"trainBeforeName":"序号", "trainLaterName":"描述"}, inplace= True)
    print(df)
    df.to_excel('C:/Users/Administrator/Desktop/10条_30s语料-df.xlsx')


    # # 15s
    # df = pd.DataFrame(columns=['trainBeforeName', 'trainLaterName'])
    # i = 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "咱也不明白，咱也不敢问——原意指看到不理解或者没办法解释的事情时的调侃，之后演变为调侃某个人或者某件事比较中二，逗比。"}, ignore_index= True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "断舍离——断舍离表达的是一种生活态度，意思是把那些不必需不适宜过时的东西统统断绝舍弃，并切断对它们的眷恋。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "有内味了——在北方口音中，常将“那”读成“内”，意思是有那种味道感觉了。一般用于表示前文出现过的事物是否地道正宗。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "其实，每个人都有一颗初心的种子，都应当寻找初心牢记初心坚持初心，为实现自我的小目标努力奋斗，为实现中国梦添砖加瓦。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "真香——是指一个人下定决心不去或去做一件事情，最终的行为却截然相反。主要用来表示某人预计的事情和最终的结果截然不一样。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "美男明白吧?情窦初开明白吧?涉世不深明白吧?嗯，明白就好，再加上长相俊俏、肌肉健硕、皮肤水嫩，好了，这就是“小鲜肉”。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "这么说话的原因只是为了不那么严肃、让自我与别人简便些而已，还有一个原因就是许多人用的是拼音输入法，选字频率上靠前选。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "一种对无奈，郁闷，无语情绪的轻微表达方式。通常表示对人物或事物，无法理喻、无法交流和无力吐槽。多可与“无力吐槽”换用。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "挺努力的意思，可是即使很努力了，却没有成功，具有反讽刺意味。本是一句很简单的口头语，在网络上被大家所熟知并广泛传播。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "不忍直视指的是网络上头很惨的事件，让人看了以后心里不舒服，而不是有愉悦感，不忍心一向盯着看，目光无法停留。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "起源是老头的被骗事件，直到骗了五十万后骗子被警察抓到为止!这件事被报道出去后，被网友评论:因为有钱，所以任性!"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "上天台：是说买足彩的人把身家都投在了足彩上，却因冷门而一贫如洗，就产生上天台跳楼的念头。可是更多是调侃，真跳的是少数。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "是个狼人意思是“比狠人再狠‘一点’”。通常用来调侃某人做事不按常理出牌，却又能取得奇效，给人一种出乎意外的很厉害的感觉。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "融梗，就是把别人精彩的创意融合进自我的作品中。近年来，因多部文艺作品涉嫌“抄袭”，网络上出现过好几次的团体讨论。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "原指一种激烈的说唱音乐风格。近年来，其含义进一步引申，人们常用“硬核”形容“很厉害”“很彪悍”，如“硬核规定”“硬核妈妈”等等。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "不忘初心的意思就是，不要忘记自我最初的心愿，其实，每个人都有一颗初心的种子，都应当寻找初心牢记初心坚持初心。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "一则名为《感激一个极品的朋友给我带来一个悲情的国庆》的帖子中，”小月月”横空出世，以极其诡异的言行雷倒众生。"}, ignore_index=True)
    # i = i + 1
    # df = df.append({'trainBeforeName': i, 'trainLaterName': "“鸭梨”是“压力”的谐音。百度贴吧中某才子有意无意间将“压力”打成“鸭梨”，引得贴吧中无数人模仿。而“鸭梨山大”也逐渐走红。"}, ignore_index=True)
    # df.rename(columns={"trainBeforeName":"序号", "trainLaterName":"描述"}, inplace= True)
    # print(df)
    # df.to_excel('C:/Users/Administrator/Desktop/20条语料/10条_15s语料-df.xlsx')
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/