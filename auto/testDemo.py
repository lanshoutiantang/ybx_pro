# -*- coding: utf-8 -*-

import seldom
from seldom import Steps


class BaiduTest(seldom.TestCase):

    def test_case_one(self):
        """a simple test case """
        self.open("https://www.baidu.com")
        self.type(id_="kw", text="seldom")
        self.click(css="#su")
        self.assertTitle("seldom_baidusousu")

    def test_case_two(self):
        """method chaining """
        Steps().open("https://www.baidu.com").find("#kw").type("seldom").find("#su").click()
        self.assertTitle("seldom_baidusousu")


if __name__ == '__main__':
    seldom.main(browser="chrome")
