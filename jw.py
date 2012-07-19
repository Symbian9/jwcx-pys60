#coding:utf-8
#-------------------------------------------------------------------------------
# Author:      xkong
# Email:       xiaokong1937@gmail.com
# Created:     17-07-2012
# Copyright:   (c) xkong 2012
# Licence:     LGPL
#-------------------------------------------------------------------------------

import urllib
import urllib2
import cookielib
import sys
import os
import re
import viewState
#-----------------------sys env ------------------------------------------------
systemRoot="C:\\data\\python\\"
if not os.path.isdir(systemRoot):
    os.makedirs(systemRoot)
sys.path.append(systemRoot)
paths=[".","E:\\data\\python\\","C:\\data\\python\\","E:\\python\\","C:\\python\\"]
sys.path.extend(paths)
#-------------------------------------------------------------------------------

#-------------------Force system encoding to UTF-8 -----------------------------
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
sys.setdefaultencoding(default_encoding)
#-------------------------------------------------------------------------------

def uni(s):
    '''Decode words to utf-8'''
    if isinstance(s,unicode):
        return s
    else:
        return s.decode('utf-8')

class Jwpt():
    '''教务系统的主模块'''
    def __init__(self,user,passwd):
        '''Init'''
        self.rootServer="202.194.250.12"
        self.serverRoot="http://%s/(hc0xgq45eqn034u1lhiqw045)"%self.rootServer
        self.user=user
        self.passwd=passwd
        self.build_header()

    def login(self):
        '''Login to the server'''
        loginLink="%s/default2.aspx"%self.serverRoot
        data={
            '__VIEWSTATE':viewState.vsLogin,
            'TextBox1':self.user,
            'TextBox2':self.passwd,}
            #'RadioButtonList1':toGbk("学生"),
            #'Button1':toGbk("  登录  ")}
            # pys60不支持gbk编码，只好使用硬编码了
        data=urllib.urlencode(data)
        data+="&RadioButtonList1=%D1%A7%C9%FA&Button1=++%B5%C7%C2%BC++"
        resp=self.opener.open(loginLink,data)
        resp=self.readgzip(resp.read())
        if resp.find("mainmenu")!=-1:
            return resp
        else:
            return ""
    def getLinksFromLoginResp(self,resp):
        '''RegRead resp,get the required links .'''
        pattern=r'<a href="xscjcx.aspx\?(.*?)\&gnmkdm=N121605"'
        self.userAccount=re.findall(pattern,resp)[0]
        self.userName=self.userAccount.split("xm=")[-1]
        self.xscjcxLink="%s/xscjcx.aspx?%s&gnmkdm=N121605"%(self.serverRoot,
                                                            self.userAccount)
    def xscjcx(self,year,semester,btnType="semester"):
        '''Get  student grade.'''
        self.getXscjcxViewState()
        if btnType=="semester":
            btnName="&btn_xq=%D1%A7%C6%DA%B3%C9%BC%A8"
        elif btnType=="year":
            btnName="btn_xn=%D1%A7%C4%EA%B3%C9%BC%A8"
        elif btnType=="all":
            btnName="btn_zcj=%C0%FA%C4%EA%B3%C9%BC%A8"
        data={
            '__VIEWSTATE':self.vsXscjcx,
            'ddlXN':year,
            'ddlXQ':semester,
            }
        data=urllib.urlencode(data)
        data+=btnName
        resp=self.opener.open(self.xscjcxLink,data)
        return self.readgzip(resp.read())
    def getXscjcxViewState(self):
        '''Get xscjcx view state'''
        resp=self.opener.open(self.xscjcxLink)
        resp=self.readgzip(resp.read())
        pattern='name="__VIEWSTATE" value="(.*?)"'
        self.vsXscjcx=re.findall(pattern,resp)[0]


    def parseStudentGrade(self,resp):
        '''Parse the student's grade,return a list'''

        resp=resp.replace("&nbsp;"," ")
        resp=resp.replace("\n","")
        gradeTableLine=""
        grade=[]
        pattern='id="Datagrid1" width="100%" style="DISPLAY:block">(.*?)</table>'
        #  it sucks.
        resp=re.findall(pattern,resp)[0]

        pattern='<tr class="datagrid1212">(.*?)</tr>'
        lineBlue=re.findall(pattern,resp)
        pattern='<tr>(.*?)</tr>'
        lineBlue+=re.findall(pattern,resp)
        for line in lineBlue:
            ptn='<td>(.*?)</td>'
            gradeTableLine=re.findall(ptn,line)
            #Don't know how to translate....sigh.
            tmp={
                'xueNian':gradeTableLine[0],
                'xueQi':gradeTableLine[1],
                'kcDaima':gradeTableLine[2],
                'kcMingcheng':gradeTableLine[3],
                'kcXingzhi':gradeTableLine[4],
                'kcGuishu':gradeTableLine[5],
                'xueFen':gradeTableLine[6],
                'jiDian':gradeTableLine[7],
                'chengJi':gradeTableLine[8],
                'fuxiuBiaoji':gradeTableLine[9],
                'bukaoChengji':gradeTableLine[10],
                'chongxiuChengji':gradeTableLine[11],
                'xueyuanMingcheng':gradeTableLine[12],
                'beiZhu':gradeTableLine[13],
                'chongxiuBiaoji':gradeTableLine[14],}
            grade.append(tmp)
        pattern='<tr>(.*?)</tr>'

        return grade

    def build_header(self):
        '''Build Request Header.'''
        cj=cookielib.LWPCookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        self.opener.addheaders=[
            ("Accept", " */*"),
            ("Referer", "%s/xkong.aspx"%self.serverRoot),
            ("Accept-Language", "zh-cn"),
            ("Content-Type", "application/x-www-form-urlencoded"),
            ("Accept-Encoding", "gzip,deflate,sdch"),
            ("User-Agent", "Mozilla/88.0 Chrome/2012.0.648.204 Safari/555.16"),
            ("Host", self.rootServer),
            ("Connection", "Keep-Alive"),
            ("Cache-Control","no-cache"),
            ("Accept-Charset", "GBK,utf-8;q=0.7,*;q=0.3")]
    def readgzip(self,resp):
        '''Read gzip files ,if not a gzip type file(i.e,string) ,return itself.'''
        try:
            source=io.StringIO(resp)
            gzipper = gzip.GzipFile(fileobj=source)
            html=gzipper.read()
        except:
            return resp
        else:
            return html
if __name__=="__main__":
    j=Jwpt('studentSerial','passwd')
    res=j.login()
    resp=j.getLinksFromLoginResp(res)
    r=j.xscjcx('2007-2008','1')
    print j.parseStudentGrade(r)

