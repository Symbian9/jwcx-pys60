#coding:utf-8
#-------------------------------------------------------------------------------
# Author:      xkong
# Email:       xiaokong1937@gmail.com
# Created:     17-07-2012
# Copyright:   (c) xkong 2012
# Licence:     LGPL
#-------------------------------------------------------------------------------
import sys
import os

#-------------------Init env------------------------------------------------
systemRoot="C:\\data\\python\\"
if not os.path.isdir(systemRoot):
    os.makedirs(systemRoot)
sys.path.append(systemRoot)
paths=["./","E:\\data\\python\\","C:\\data\\python","E:\\python","C:\\python"]
sys.path.extend(paths)
#------------------------------------------------------------------------------

#-------------------Force system encoding to UTF-8 ----------------------------
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
sys.setdefaultencoding(default_encoding)
#------------------------------------------------------------------------------

import jw

import e32
import appuifw


def uni(s):
    '''Force Chinese words to UTF-8 format.'''
    if isinstance(s,unicode):
        return s
    else:
        return s.decode('utf-8')

class S60View():
    '''MainWindow'''
    def __init__(self):
        self.app_lock=e32.Ao_lock()
        appuifw.app.exit_key_handler=self.quit
        appuifw.app.title=u"Jwcx"
        appuifw.app.screen="normal"
        self.listbox=appuifw.Listbox([(u"",u"")],self.listCallback)
        appuifw.app.body=self.listbox

        self.timer=e32.Ao_timer()

        self.user=""
        self.passwd=""
        self.loginResp=""
        self.reLogin=False
        self.configFile="%swin32.sock"%systemRoot

        self.createMenu()
        self.login()

    #---------------UI function block start-----------------------------------
    def createMenu(self):
        cx=((u"查询成绩",self.cxcj),
            (u"查询课表",self.cxkb)
            )
        menu=[(u"查询",cx),
              (u"更换用户",self.changeAccount),
              (u"选择接入点",self.selectAccessPoint),]
        appuifw.app.menu=menu
    #----------------UI func end-----------------------------------------------
    def alert(self,msg):
        return appuifw.note(uni(msg),"info")
    def quit(self):
        self.app_lock.signal()
    def setWindowTitle(self,title):
        appuifw.app.title=title
    #----------------Accounts function----------------------------------------
    def login(self):
        user=passwd=""
        if not self.reLogin:
            user,passwd=self.getSavedAccount()
        if not user or not passwd:
            user,passwd=self.getAccount()
        if self.__login(user,passwd):
            self.jwcx.getLinksFromLoginResp(self.loginResp)
            appuifw.note(uni("登录成功。"),"info")
            self.reLogin=False
            self.setWindowTitle(uni("Jwcx"))
            self.listbox.set_list([(u"请选择相应",u"的操作")])
        else:
            appuifw.note(uni("登陆失败。请重新登录。"),"error")
            self.login()
    def __login(self,user,passwd):
        self.jwcx=jw.Jwpt(user,passwd)
        self.loginResp=self.jwcx.login()
        if self.loginResp:
            self.saveAccount(user,passwd)
            return True
        else:
            return False
    def getSavedAccount(self):
        if not os.path.isfile(self.configFile):
            return "",""
        configFile=open(self.configFile,"r")
        raw=configFile.read()
        user,passwd=raw.split("||")
        return self.decrypt(user),self.decrypt(passwd)
    def saveAccount(self,user,passwd):
        configFile=open(self.configFile,"w")
        configFile.write("%s||%s"%(self.encrypt(user),self.encrypt(passwd)))
        configFile.close()
    def getAccount(self):
        '''GetAccount via multi_query'''
        try:
            user,passwd=appuifw.multi_query(uni("学号："),uni("密码:"))
        except:
            sys.exit()
        else:
            return user,passwd
    #--------------------Account functions block end----------------------------
    #----------------------Public functions-------------------------------------
    def getQueryArgv(self):
        '''查询成绩时选择学年，学期。'''
        yearList=jw.viewState.yearListMap
        self.setWindowTitle(uni("选择学年"))
        year=appuifw.selection_list(yearList)
        semesterList=jw.viewState.semesterListMap
        self.setWindowTitle(uni("选择学期"))
        semester=appuifw.selection_list(semesterList)

        return jw.viewState.yearList[year],jw.viewState.semesterList[semester]
    def decrypt(self,s,key=systemRoot):
        '''Decrypt string 's',key is the secret string used to decrypt.'''
        s=str(s)
        newstring=""
        stringlength=len(s)
        if stringlength%2==0:
            str1=s[:int(stringlength/2)]
            str2=s[int(stringlength/2):]
            s=str1[::-1]+str2[::-1]
        for i in range(stringlength):
            x=i
            if i>=len(key):x=i%len(key)
            a=ord(key[x])^ord(s[i])
            if a<32 or ord(s[i])<0 or a>127 or ord(s[i])>255 :
                a=ord(s[i])
            newstring+=chr(a)
        return newstring
    def encrypt(self,s,key=systemRoot):
        '''Encrypt string 's',key is the secret string used to encrypt.'''
        s=str(s)
        newstring=""
        stringlength=len(s)
        for i in range(stringlength):
            x=i
            if i>=len(key):x=i%len(key)
            a=ord(key[x])^ord(s[i])
            if a<32 or ord(s[i])<0 or a>127 or ord(s[i])>255 :
                a=ord(s[i])
            newstring+=chr(a)
        ll=len(newstring)
        if ll%2==0:
            str1=newstring[:int(ll/2)]
            str2=newstring[int(ll/2):]
            newstring=str1[::-1]+str2[::-1]
        return newstring
    def debug(self,msg):
        '''sysStdErrorRedirect'''
        f=open("%sconsole.txt"%systemRoot,"a")
        f.write("\n")
        f.write(repr(msg))
        f.write("\n")
        f.close()
    #--------------------------------------------------------------------------

    #------------------------slots--------------------------------------------
    def cxcj(self):
        '''查询成绩，需要选择学年，学期'''
        self.setWindowTitle(uni("成绩查询"))
        if not self.loginResp:
            appuifw.note(uni("认证失败，请重新登录。"),"error")
            self.login()
            return
        try:
            year,semester=self.getQueryArgv()
            name=self.jwcx.userName.decode('gbk')
            self.setWindowTitle(uni("成绩查询_%s"%name))
            self.listbox.set_list([(u"开始查询成绩",u"请稍等...")])
            resp=self.jwcx.xscjcx(year,semester)
            grade=self.jwcx.parseStudentGrade(resp)
            listbox=[]
            for cj in grade:
                kcName=cj[u'kcMingcheng'].decode('gbk')
                kcGrade=cj[u'chengJi'].decode('gbk')
                listbox.append(("%s:"%kcName,kcGrade))
            self.setWindowTitle(uni("%s_%s_%s"%(name,year.split("-")[0],semester)))
            self.listbox.set_list(listbox)
        except:
            self.alert("没有匹配的结果")
    def changeAccount(self):
        '''更换用户'''
        if os.path.isfile(self.configFile):
            os.remove(self.configFile)
        self.loginResp=""
        self.reLogin=True
        if self.jwcx:del self.jwcx
        self.login()

    def selectAccessPoint(self):
        '''接入点'''
        try :
            import btsocket as newsocket
        except:
            import socket as newsocket
        else:
            ap_id=newsocket.select_access_point()
            apo=newsocket.access_point(ap_id)
            newsocket.set_default_access_point(apo)
    def cxkb(self):
        '''查询课表'''
        print "cxkb"

    def listCallback(self):
        print "%s"%self.listbox.current()
    #----------------------slots functions end--------------------------------

if __name__=="__main__":
    s=S60View()
    s.app_lock.wait()

