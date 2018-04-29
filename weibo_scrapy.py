import os
import re
import requests
import sys
import traceback
from datetime import datetime
from datetime import timedelta
from lxml import etree

from time import sleep

import numpy as np
import pandas as pd

class Weibo:
    cookie = {"Cookie": "personal account key hidden for privacy"}

    def __init__(self, user_id, filter=0):
        self.user_id = user_id 
        self.filter = filter  
        self.username = ''  
        self.weibo_num = 0  
        self.following = 0  
        self.followers = 0  
        self.sex = 'NaN'
        self.loc = 'NaN'
        self.dob = 'NaN'
        self.term = 'NaN'

    def get_username(self):
        try:
            id_exist = True
            url = "https://weibo.cn/%d/info" % (self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            username = selector.xpath("//title/text()")[0]
            self.username = username[:-3]
            if self.username == '':
                id_exist = False                           
                print ('no such id number:', self.user_id)
            else:
                print ("user id number: ", self.user_id)                 
                print (u"用户名: " + self.username)
            
        except Exception as e:
            print ("Error: ", e)
            traceback.print_exc()
            
        return self.user_id, id_exist 
            
    def get_user_bio(self):
        try:
            url = "https://weibo.cn/%d/info" % (self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            
            pattern = r"^性别:(.*)"
            str_sex = selector.xpath("//text()[substring-after(., '性别:')]")[0]
            guid = re.findall(pattern, str_sex, re.M)
            self.sex = guid[0]
            print (u"性别: " + str(self.sex))
            
            pattern = r"^地区:(.*)"
            str_loc = selector.xpath("//text()[substring-after(., '地区:')]")[0]
            guid = re.findall(pattern, str_loc, re.M)
            self.loc = guid[0]
            print (u"地区: " + str(self.loc))
            
            pattern = r"^生日:(.*)"
            str_dob = selector.xpath("//text()[substring-after(., '生日:')]")[0]
            guid = re.findall(pattern, str_dob, re.M)
            self.dob = guid[0]
            print (u"生日: " + str(self.dob))
            
        except Exception as e:
            print ("Error: ", e)
            traceback.print_exc() 
            
        return self.sex, self.loc, self.dob
            
    def get_term_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            
            str_term = selector.xpath("//text()[substring-after(., '来自')]")[0]
            guid = str_term.split("来自",1)[1] 
            self.term = guid 
            print (u"来自: " + str(self.term))
            
        except Exception as e:
            print ("Error: ", e)
            traceback.print_exc()
        
        return self.term

    def get_user_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            pattern = r"\d+\.?\d*"

            str_wb = selector.xpath(
                "//div[@class='tip2']/span[@class='tc']/text()")[0]
            guid = re.findall(pattern, str_wb, re.S | re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.weibo_num = num_wb
            print (u"微博数: " + str(self.weibo_num))

            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.following = int(guid[0])
            print (u"关注数: " + str(self.following))

            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.followers = int(guid[0])
            print (u"粉丝数: " + str(self.followers))

        except Exception as e:
            print ("Error: ", e)
            traceback.print_exc()
            
        return self.weibo_num, self.following, self.followers
           
    def write_txt(self):
        try:
            result = (u"user_nickname：" + self.username +
                      u"\nuser_id：" + str(self.user_id) +
                      u"\ngender：" + str(self.sex) +
                      u"\nlocation：" + str(self.loc) +
                      u"\nbirthday：" + str(self.dob) +
                      u"\nn_posts：" + str(self.weibo_num) +
                      u"\nn_following：" + str(self.following) +
                      u"\nn_followers：" + str(self.followers) +
                      u"\nterminal：" + str(self.term) 

                     )
                        
            file_dir = os.path.split(os.path.realpath("__file__"))[
                0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "%d" % self.user_id + ".txt"
            f = open(file_path, "wb")
            f.write(result.encode(sys.stdout.encoding))
            f.close()
            print (file_path)
        except Exception as e:
            print ("Error: ", e)
            traceback.print_exc()
            
    def start(self):
        try:
            user_id, id_exist = self.get_username()  
            sex = ''
            loc = ''
            dob = ''
            weibo_num, following, follower = '', '', ''
            term = ''
            if id_exist == True:
                sex, loc, dob = self.get_user_bio()
                weibo_num, following, follower = self.get_user_info()
                term = self.get_term_info()
                #self.write_txt()
            print ("===========================================================================")
        except Exception as e:
            print ("Error: ", e)
        
        return id_exist, user_id, sex, loc, dob, weibo_num, following, follower, term
    
def main():
    try:
        dt = 500
        for batch in range(0,200):
            print("batch ", batch)
            user_list = np.loadtxt('./users/user_id_list_%d.txt' % batch, dtype='int64')

            user_id_list = []
            sex_list = []
            loc_list = []
            dob_list = []
            weibo_num_list = []
            following_list = []
            follower_list = []
            term_list = []
            i = 0
            for user_id in user_list:
                i = i + 1
                print(i)
                filter = 1  
                wb = Weibo(user_id, filter) 
                id_exist, user_id, sex, loc, dob, weibo_num, following, follower, term = wb.start()
            
                if id_exist == True:
                    user_id_list.append(int(user_id))
                    if sex == '男':
                        sex_list.append('M')
                    elif sex == '女':
                        sex_list.append('F')
                    else:
                        sex_list.append('NaN')

                    loc_list.append(loc)
                    dob_list.append(dob)
                    weibo_num_list.append(int(weibo_num))
                    following_list.append(int(following))
                    follower_list.append(int(follower))
                    term_list.append(term)
            
            weibo_data = np.stack((user_id_list, sex_list, loc_list, dob_list, weibo_num_list, following_list, follower_list, term_list), axis=1)

            np.savetxt('./data/weibo_data_%d.csv' % batch,weibo_data, delimiter=',', header = 'user_id,sex,loc,dob,weibo_num,following,follower,term', fmt = '%s', comments='') 
            
            print("batch ", batch, "is finished")
            print("wait ", dt, "s ...")
            sleep(dt)
        
    except Exception as e:
        print ("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()

