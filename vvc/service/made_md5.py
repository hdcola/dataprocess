#!/usr/bin/python
# -*- coding: utf-8 -*- #
############################################################################
##
## Copyright (c) 2013 hunantv.com, Inc. All Rights Reserved
## $Id: cleaning_log.py,v 0.0 2015年11月09日 星期一 16时48分31秒  dongjie Exp $
##
############################################################################
#
###
# # @file   cleaning_log.py
# # @author dongjie<dongjie@e.hunantv.com>
# # @date   2015年11月09日 星期一 16时48分31秒
# # @brief
# #
# ##
import sys
import hashlib

for l in sys.stdin:
    line = l.strip().replace("-", "")
    m2 = hashlib.md5()
    m2.update(line)
    print m2.hexdigest()