# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# driver = webdriver.Firefox()
# driver.get('http://www.python.org')
# # driver.get('http://www.baidu.com')
# assert "Python" in driver.title
# # assert "百度" in driver.title
# elem = driver.find_element_by_name("q")
# # elem = driver.find_element_by_id("su")
# elem.send_keys("python")
# elem.send_keys(Keys.RETURN)
# print driver.page_source


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        # self.driver = webdriver.Chrome()
        self.driver = webdriver.Firefox()

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://www.python.org")
        self.assertIn("Python", driver.title)
        elem = driver.find_element_by_name("q")
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source
        fp = open("pycon.html", "w")
        fp.write(driver.page_source.encode("utf-8"))
        fp.close()


    def tearDown(self):
        self.driver.close()
    #
    # def get_cookies(self):
    #     self.driver.get_cookies()
    #
    # def set_cookies(self, cookies):
    #     self.driver.add_cookie(cookies)


if __name__ == "__main__":
    unittest.main()
