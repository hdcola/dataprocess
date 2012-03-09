#!/usr/bin/env python
# encoding: utf-8

import sys
import unittest
import process

class AOPDataTestCase(unittest.TestCase):
    """使用AOP 100行数据进行测试"""
    def testAOP(self):
        sys.argv.append("aop.data")
        process.main()
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(AOPDataTestCase("testAOP"))
    return suite

if __name__ == "__main__":
  unittest.main(defaultTest = 'suite')