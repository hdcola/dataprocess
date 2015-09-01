#!/usr/bin/env python
# encoding: utf-8

VIDEORATELIST = {'wmjq_mzb1_mpp_sd': 600,
                 'wmjq_mzb2_mpp_sd': 600,
                 'wmjq_mzb3_mpp_sd': 600,
                 'wmjq_mzb4_mpp_sd': 600,
                 'wmjq_mzb5_mpp_sd': 600,
                 'wmjq_mzb6_mpp_sd': 600,
                 'wmjq_mzb7_mpp_sd': 600,
                 'wmjq_mzb1_mpp_hd': 900,
                 'wmjq_mzb2_mpp_hd': 900,
                 'wmjq_mzb3_mpp_hd': 900,
                 'wmjq_mzb4_mpp_hd': 900,
                 'wmjq_mzb5_mpp_hd': 900,
                 'wmjq_mzb6_mpp_hd': 900,
                 'wmjq_mzb7_mpp_hd': 900,
                 'wmjq_mzb1_mpp_hhd': 1.5*1000,
                 'wmjq_mzb2_mpp_hhd': 1.5*1000,
                 'wmjq_mzb3_mpp_hhd': 1.5*1000,
                 'wmjq_mzb4_mpp_hhd': 1.5*1000,
                 'wmjq_mzb5_mpp_hhd': 1.5*1000,
                 'wmjq_mzb6_mpp_hhd': 1.5*1000,
                 'wmjq_mzb7_mpp_hhd': 1.5*1000,
                 'wmjq_mzb1_ott_sd': 1.25*1000,
                 'wmjq_mzb2_ott_sd': 1.25*1000,
                 'wmjq_mzb3_ott_sd': 1.25*1000,
                 'wmjq_mzb4_ott_sd': 1.25*1000,
                 'wmjq_mzb5_ott_sd': 1.25*1000,
                 'wmjq_mzb6_ott_sd': 1.25*1000,
                 'wmjq_mzb7_ott_sd': 1.25*1000,
                 'wmjq_mzb1_ott_hd': 2.5*1000,
                 'wmjq_mzb2_ott_hd': 2.5*1000,
                 'wmjq_mzb3_ott_hd': 2.5*1000,
                 'wmjq_mzb4_ott_hd': 2.5*1000,
                 'wmjq_mzb5_ott_hd': 2.5*1000,
                 'wmjq_mzb6_ott_hd': 2.5*1000,
                 'wmjq_mzb7_ott_hd': 2.5*1000,
                 'wmjq_hdzb1_mpp_sd': 600,
                 'wmjq_hdzb2_mpp_sd': 600,
                 'wmjq_hdzb3_mpp_sd': 600,
                 'wmjq_hdzb4_mpp_sd': 600,
                 'wmjq_hdzb5_mpp_sd': 600,
                 'wmjq_hdzb6_mpp_sd': 600,
                 'wmjq_hdzb7_mpp_sd': 600,
                 'wmjq_hdzb8_mpp_sd': 600,
                 'wmjq_hdzb9_mpp_sd': 600,
                 'wmjq_hdzb10_mpp_sd': 600,
                 'wmjq_hdzb11_mpp_sd': 600,
                 'wmjq_hdzb12_mpp_sd': 600,
                 'wmjq_hdzb1_mpp_hd': 900,
                 'wmjq_hdzb2_mpp_hd': 900,
                 'wmjq_hdzb3_mpp_hd': 900,
                 'wmjq_hdzb4_mpp_hd': 900,
                 'wmjq_hdzb5_mpp_hd': 900,
                 'wmjq_hdzb6_mpp_hd': 900,
                 'wmjq_hdzb7_mpp_hd': 900,
                 'wmjq_hdzb8_mpp_hd': 900,
                 'wmjq_hdzb9_mpp_hd': 900,
                 'wmjq_hdzb10_mpp_hd': 900,
                 'wmjq_hdzb11_mpp_hd': 900,
                 'wmjq_hdzb12_mpp_hd': 900,
                 'wmjq_hdzb1_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb2_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb3_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb4_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb5_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb6_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb7_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb8_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb9_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb10_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb11_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb12_mpp_hhd': 1.5*1000,
                 'wmjq_hdzb1_ott_sd': 1.25*1000,
                 'wmjq_hdzb2_ott_sd': 1.25*1000,
                 'wmjq_hdzb3_ott_sd': 1.25*1000,
                 'wmjq_hdzb4_ott_sd': 1.25*1000,
                 'wmjq_hdzb5_ott_sd': 1.25*1000,
                 'wmjq_hdzb6_ott_sd': 1.25*1000,
                 'wmjq_hdzb7_ott_sd': 1.25*1000,
                 'wmjq_hdzb8_ott_sd': 1.25*1000,
                 'wmjq_hdzb9_ott_sd': 1.25*1000,
                 'wmjq_hdzb10_ott_sd': 1.25*1000,
                 'wmjq_hdzb11_ott_sd': 1.25*1000,
                 'wmjq_hdzb12_ott_sd': 1.25*1000,
                 'wmjq_hdzb1_ott_hd': 2.5*1000,
                 'wmjq_hdzb2_ott_hd': 2.5*1000,
                 'wmjq_hdzb3_ott_hd': 2.5*1000,
                 'wmjq_hdzb4_ott_hd': 2.5*1000,
                 'wmjq_hdzb5_ott_hd': 2.5*1000,
                 'wmjq_hdzb6_ott_hd': 2.5*1000,
                 'wmjq_hdzb7_ott_hd': 2.5*1000,
                 'wmjq_hdzb8_ott_hd': 2.5*1000,
                 'wmjq_hdzb9_ott_hd': 2.5*1000,
                 'wmjq_hdzb10_ott_hd': 2.5*1000,
                 'wmjq_hdzb11_ott_hd': 2.5*1000,
                 'wmjq_hdzb12_ott_hd': 2.5*1000,
                 }