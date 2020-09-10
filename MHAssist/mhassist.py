import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from assistui.assistui import Ui_assist
import win32gui,win32api,win32con
import time
import pyautogui
from cv2 import cv2
import os
import ctypes
from win32process import SuspendThread, ResumeThread


class MyMainForm(QMainWindow, Ui_assist):
    
    def __init__(self,title, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.pb_pause.setEnabled(False)
        self.pb_stop.setEnabled(False)
        self.pb_start.clicked.connect(self.start)
        self.pb_pause.clicked.connect(self.pause)
        self.pb_stop.clicked.connect(self.stop)
        self.pb_clear.clicked.connect(self.clear)

        self.dte_starttime.setDateTime(QDateTime.currentDateTime())
        self.dte_starttime.setMinimumDate(QDate.currentDate().addDays(-1))
        self.dte_starttime.setMaximumDate(QDate.currentDate().addDays(1))

        self.thread = Worker(baselinscore,curdir,curimg)
        self.thread.sig.connect(self.setmessage)
        self.title = title
        self.hwnd_title = dict()

    def start(self):

        self.pb_start.setEnabled(False)
        self.pb_pause.setEnabled(True)
        self.pb_stop.setEnabled(True)
        self.pb_clear.setEnabled(False)

        if self.thread.handle == -1:
            self.tb_logs.setText("")
            mode = list()
            zhuaGuiCount = 0
            fuBenCount = 0
            miJingCount = 0
            enableDoubleStart = False
            enablePlayerMode = False
            zhuaGuiMark = True
            fuBenMark = True
            miJingMark = True            
            
            allWindows = self.get_hwnd()
            print(allWindows)

            #判断是否启用了双开模式
            if self.chb_doubleStart.isChecked():
                enableDoubleStart = True
            #判断是否启用了主号切换模式
            if self.chb_switch.isChecked():
                allWindows.reverse()
                print(allWindows)
            #判断是否启动了队员模式
            if self.chb_playerMode.isChecked():
                enablePlayerMode = True          
            #抓鬼任务
            if (self.chb_zgui.isChecked()):
                mode.append("1")
                zhuaGuiCount = self.spb_zgui.value()
                if zhuaGuiCount <= 0:
                    zhuaGuiMark = False
            #副本任务
            if (self.chb_fben.isChecked()):
                mode.append("2")
                fuBenCount = self.spb_FuBen.value()
                if fuBenCount <=0:
                    fuBenMark = False
            #秘境任务
            if (self.chb_mjing.isChecked()):
                mode.append("4")
                miJingCount = self.spb_MiJing.value()
                if miJingCount <= 0:
                    miJingMark = False
            #打图任务
            if (self.chb_dtu.isChecked()):
                mode.append("5")
            #挖图任务
            if(self.chb_wtu.isChecked()):
                mode.append("6")
            #师门任务
            if (self.chb_smen.isChecked()):
                mode.append("11") 
            #押镖任务
            if (self.chb_ybiao.isChecked()):
                mode.append("3")
            #挖矿任务
            if (self.chb_wkuang.isChecked()):
                mode.append("10")
            #帮派任务
            if (self.chb_bpai.isChecked()):
                mode.append("7")
            #门派任务
            if (self.chb_mpai.isChecked()):
                mode.append("9")
            #海底寻宝
            if (self.chb_haidi.isChecked()):
                mode.append("12")
            #迷魂塔
            if (self.chb_mihunt.isChecked()):
                mode.append("13")
            #经验链任务
            if (self.chb_jylian.isChecked()):
                mode.append("8")
            #初级贸易
            if (self.chb_cjMaoYi.isChecked()):
                mode.append("14")
            #初级贸易
            if (self.chb_gjMaoYi.isChecked()):
                mode.append("15")

            if not allWindows:
                print("未检测到有效的窗口，请开启相应程序后再试！")
                self.tb_logs.append("未检测到有效的窗口，请开启响应程序后再试！")
                self.pb_start.setEnabled(True)
                self.pb_pause.setEnabled(False)
                self.pb_stop.setEnabled(False)
                self.pb_clear.setEnabled(True)
            elif zhuaGuiMark and fuBenMark and miJingMark:
                print("当前选择的任务序列为：", mode)
                self.thread = Worker(baselinscore,curdir,curimg)
                self.thread.sig.connect(self.setmessage)
                self.thread.mode = mode
                self.thread.zhuaGuiCount = zhuaGuiCount
                self.thread.fuBenCount = fuBenCount
                self.thread.miJingCount = miJingCount
                if enableDoubleStart and len(allWindows) == 2:
                    self.thread.enableDoubleStart = True
                else:
                    self.thread.enableDoubleStart = False
                self.thread.enablePlayerMode = enablePlayerMode
                self.thread.allWindows = allWindows
                self.thread.startTime = self.dte_starttime.dateTime().toSecsSinceEpoch()
                print(self.dte_starttime.dateTime().toSecsSinceEpoch())
                self.thread.start()
            else:
                self.tb_logs.append("请检查任务选择情况及任务次数设定后再试！")
                self.pb_start.setEnabled(True)
                self.pb_pause.setEnabled(False)
                self.pb_stop.setEnabled(False)
                self.pb_clear.setEnabled(True)
        else:
            ret = ResumeThread(self.thread.handle)

    
    def get_all_hwnd(self,hwnd,mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            self.hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})

    def get_hwnd(self):
        hwnd = list()
        win32gui.EnumWindows(self.get_all_hwnd, 0)
        for h,t in self.hwnd_title.items():
            if t == self.title:
                hwnd.append(h)
        return hwnd

    def pause(self):        
        self.pb_start.setEnabled(True)
        self.pb_pause.setEnabled(False)
        self.pb_stop.setEnabled(True)
        if self.thread.handle == -1:
            return print('未检测到子进程！')
        else:
            ret = SuspendThread(self.thread.handle)

    def stop(self):
        self.pb_start.setEnabled(True)
        self.pb_pause.setEnabled(False)
        self.pb_stop.setEnabled(False)
        self.pb_clear.setEnabled(True)
        self.spb_zgui.setValue(0)
        self.spb_FuBen.setValue(0)
        self.spb_MiJing.setValue(0)
        if self.thread.handle == -1:
            return print('未检测到子进程！')
        else:
            ret = ctypes.windll.kernel32.TerminateThread(self.thread.handle,0)
            self.thread.handle = -1

    def clear(self):
        self.chb_zgui.setChecked(False)
        self.chb_fben.setChecked(False)
        self.chb_mjing.setChecked(False)
        self.chb_dtu.setChecked(False)
        self.chb_wtu.setChecked(False)
        self.chb_ybiao.setChecked(False)
        self.chb_wkuang.setChecked(False)
        self.chb_smen.setChecked(False)
        self.chb_bpai.setChecked(False)
        self.chb_mpai.setChecked(False)
        self.chb_haidi.setChecked(False)
        self.chb_mihunt.setChecked(False)
        self.chb_jylian.setChecked(False)
        self.chb_cjMaoYi.setChecked(False)
        self.chb_gjMaoYi.setChecked(False)        
        self.chb_others.setChecked(False)
        self.spb_zgui.setValue(0)
        self.spb_FuBen.setValue(0)
        self.spb_MiJing.setValue(0)
    
    def setmessage(self,message):
        self.tb_logs.append(message)
    
    def closeEvent(self, event):
        if self.thread.isRunning():
            self.thread.quit()
        del self.thread
        super(MyMainForm, self).closeEvent(event)

class Worker(QThread):

    sig = pyqtSignal(str)
    handle = -1

    def __init__(self,baselinscore,curdir,curimg,parent=None):
        super(Worker,self).__init__(parent)
                
        self.curdir = curdir
        self.curimg = curimg
        self.baselinscore = baselinscore
        self.zhuaGuidir = self.curdir + r"\image\ZhuaGui"
        self.waTu = self.curdir + r"\image\WaTu"
        self.bangPai = self.curdir + r"\image\BangPai"
        self.closeTips = self.curdir + r"\image\CloseTips"
        self.shiMen = self.curdir + r"\image\ShiMen"
        self.renWuLian = self.curdir + r"\image\RenWuLian"
        self.fuBen = self.curdir + r"\image\FuBen"
        self.yaBiao = self.curdir + r"\image\YaBiao"
        self.daTu = self.curdir + r"\image\DaTu"
        self.menPai = self.curdir + r"\image\MenPai"
        self.waKuang = self.curdir + r"\image\WaKuang"
        self.miJing = self.curdir + r"\image\MiJing"
        self.xunBao = self.curdir + r"\image\xunBao"
        self.miHunTa = self.curdir + r"\image\MiHunTa"
        self.cjMaoyi = self.curdir + r"\image\CJMaoyi"
        self.gjMaoyi =  self.curdir + r"\image\GJMaoyi"

        # 特殊图片定义
        self.rwExpand = self.curdir + r"\image\MainUI\MainUI_ExpandRW.jpg"
        self.rwClosed = self.curdir + r"\image\MainUI\RenWu_Closed.png"
        self.rwClick = self.curdir + r"\image\MainUI\MainUI_RWlocation.png"
        self.rwlLocation = self.curdir + r"\image\Startjob\Location_RWL.png"
        self.mpLocation = self.curdir + r"\image\Startjob\Location_MP.png"
        self.smLocation = self.curdir + r"\image\Startjob\Location_shiMen.png"
        self.zgLocation = self.curdir + r"\image\Startjob\Location_ZhuaGUI.png"
        self.cjMaoYiLocation = self.curdir + r"\image\StartJob\StartJob_CJMaoyi.png"
        self.gjMaoYiLocation = self.curdir + r"\image\StartJob\StartJob_GJMaoyi.png"

    def capture_img(self,handle, imgepath):
        screen = QApplication.primaryScreen()
        img = screen.grabWindow(handle).toImage()
        img.save(imgepath)

    def search_position(self,targetimg, templateimg):
        target = cv2.imread(targetimg, 0)
        template = cv2.imread(templateimg, 0)
        theight, twidth = template.shape[:2]
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        time.sleep(1)
        return max_val, max_loc

    def simulate_mouse(self,xpoction, ypoction):
        time.sleep(1)
        pyautogui.moveTo(xpoction, ypoction)
        print("任务点击！")
        pyautogui.click()

    def roll_mouse(self,xpoction, ypoction):
        pyautogui.moveTo(xpoction, ypoction)
        time.sleep(2)
        scrollcount = 0
        while scrollcount < 20:
            scrollcount += 1
            pyautogui.scroll(10)
    
    def rlsimulate_mouse(self, xpoction, ypoction):
        pyautogui.moveTo(xpoction, ypoction)
        time.sleep(2)
        scrollcount = 0
        while scrollcount < 18:
            scrollcount += 1
            pyautogui.scroll(10)
        print("任务点击！")
        pyautogui.click()
    
    def mouse_DownUp(self,image):
        self.capture_img(self.window, self.curimg)
        mainPos = win32gui.GetWindowRect(self.window)
        matchedScroe, poction = self.search_position(self.curimg, image)
        if matchedScroe >= self.baselinscore:
            win32gui.SetForegroundWindow(self.window)
            print(matchedScroe, self.baselinscore)
            xcurpoc = mainPos[0] + poction[0] + 50
            ycurpoc = mainPos[1] + poction[1] + 50
            pyautogui.mouseDown(xcurpoc,ycurpoc)
            time.sleep(2) 
            pyautogui.mouseUp()

    def click_Image(self,image,mark=1):
        mainPos = win32gui.GetWindowRect(self.window)
        self.capture_img(self.window, self.curimg)
        time.sleep(2)
        matchedScroe, poction = self.search_position(self.curimg, image)
        print(matchedScroe, self.baselinscore)
        self.sig.emit(str(matchedScroe) + ',' + str(self.baselinscore))
        if matchedScroe >= self.baselinscore:
            win32gui.SetForegroundWindow(self.window)            
            xcurpoc = mainPos[0] + poction[0] + 50
            ycurpoc = mainPos[1] + poction[1] + 50
            self.simulate_mouse(xcurpoc, ycurpoc)
            if mark == 2 :
                self.simulate_mouse(xcurpoc, ycurpoc)
            time.sleep(1) 

    def start_job(self,job):
        riChang = self.curdir + r"\image\StartJob\Location_RiChangHuoDong.png"
        #活动点击
        win32gui.SetForegroundWindow(self.window)
        time.sleep(5)
        pyautogui.keyDown('altleft')
        pyautogui.press('c')
        pyautogui.keyUp('altleft')
        time.sleep(2)
        #日常点击
        mainPos = win32gui.GetWindowRect(self.window)
        self.capture_img(self.window, self.curimg)
        matchedScroe, poction = self.search_position(self.curimg, riChang)
        if matchedScroe >= self.baselinscore:
            win32gui.SetForegroundWindow(self.window)
            xcurpoc = mainPos[0] + poction[0] + 30
            ycurpoc = mainPos[1] + poction[1] + 50
            self.simulate_mouse(xcurpoc, ycurpoc)
            time.sleep(1)
            self.roll_mouse(xcurpoc + 300,ycurpoc + 100)
            time.sleep(1)
        # 任务点击
        mainPos = win32gui.GetWindowRect(self.window)
        self.capture_img(self.window, self.curimg)
        matchedScroe, poction = self.search_position(self.curimg, job)
        if matchedScroe >= self.baselinscore:
            win32gui.SetForegroundWindow(self.window)
            xcurpoc = mainPos[0] + poction[0] + 300
            ycurpoc = mainPos[1] + poction[1] + 50
            self.simulate_mouse(xcurpoc, ycurpoc)
            time.sleep(1)
        else:
            #未检测到任务，关闭窗口
            print("未检测到任务，关闭任务窗口")
            self.sig.emit("未检测到任务，关闭任务窗口")
            pyautogui.keyDown('altleft')
            pyautogui.press('c')
            pyautogui.keyUp('altleft')
            time.sleep(2)

    def close_Windows(self):
        print("前置窗口检测中...")
        self.sig.emit("前置窗口检测中...")   
        for filename in os.listdir(self.closeTips):
            curfilename = os.path.join(self.closeTips, filename)
            mainPos = win32gui.GetWindowRect(self.window)
            self.capture_img(self.window, self.curimg)
            matchedScroe, poction = self.search_position(self.curimg, curfilename)
            if matchedScroe >= self.baselinscore:
                win32gui.SetForegroundWindow(self.window)
                print(matchedScroe, self.baselinscore)
                print("该任务已匹配：", filename)
                print("检测到其他任务提示，进行关闭!")
                self.sig.emit("检测到其他任务提示，进行关闭:" + filename)
                xcurpoc = mainPos[0] + poction[0] + 20
                ycurpoc = mainPos[1] + poction[1] + 40
                self.simulate_mouse(xcurpoc, ycurpoc)
                time.sleep(2)
                break

    def run(self):
        try:
            self.handle = ctypes.windll.kernel32.OpenThread(win32con.PROCESS_ALL_ACCESS, False, int(QThread.currentThreadId()))
        except Exception as e:
            print('Get Thread Handle Failed',e)
        
        print(int(QThread.currentThreadId()))
        
        processRunning = True
        for window in self.allWindows:
            #processRunning 为False时，跳出任务执行
            if not processRunning:
                break
            
            self.window = window
            self.sig.emit("目标窗口ID为:" + str(self.window))
            #激活任务窗口
            time.sleep(5)
            win32gui.ShowWindow(self.window, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.window)

            modestr = self.mode[0]
            for item in self.mode:
                if item != modestr:
                    modestr += "," + item
            self.sig.emit("当前选择的任务序列为:" + modestr)
            
            #若任务包含抓鬼或者副本，判断是否启用了后续任务，若启用了后续任务，完成该两项任务后队长自动退队
            #默认情况下退出组队为False，只有包含了后续任务时才为True
            quitTeamEnable = False
            if len(self.mode) > 2:
                if "2" in self.mode or "1" in self.mode:
                    quitTeamEnable = True
            elif len(self.mode) ==2:
                if "2" in self.mode and "1" in self.mode:
                    quitTeamEnable = False
                elif "2" in self.mode or "1" in self.mode:
                    quitTeamEnable = True

            curDateTime = QDateTime.currentDateTime().toSecsSinceEpoch()
            while curDateTime < self.startTime:
                curDateTime = QDateTime.currentDateTime().toSecsSinceEpoch()
                print("任务计划时间未到，等待中...")
                self.sig.emit("计划任务时间未到，等待中...")
                time.sleep(60)

            print("双开模式:" + str(self.enableDoubleStart))
            self.sig.emit("双开模式:"  + str(self.enableDoubleStart))
            print("组队跟随模式:" + str(self.enablePlayerMode))
            self.sig.emit("组队跟随模式:"  + str(self.enablePlayerMode))
            print("组队退出模式:" + str(quitTeamEnable))
            self.sig.emit("组队退出模式:"  + str(quitTeamEnable))

            quitTeam = self.curdir + r"\image\StartJob\Location_QuitTeam.png"
            teamNotAll = self.curdir + r"\image\StartJob\Location_Team_NotAll.png"
            teamZhuZhan = self.curdir + r"\image\StartJob\Location_Team_ZhuZhan.png"
            
            #操作之前先关闭窗口
            self.close_Windows()
            
            #仅启用跟随时，判断队员不足时退出队伍，继续单人任务
            while self.enablePlayerMode:
                win32gui.SetForegroundWindow(self.window)
                time.sleep(2)
                pyautogui.keyDown('altleft')
                pyautogui.press('t')
                pyautogui.keyUp('altleft')
                time.sleep(2)
                self.capture_img(self.window,self.curimg)
                matchedScroe, poction = self.search_position(self.curimg, teamZhuZhan)
                matchedScroe1, poction1 = self.search_position(self.curimg, teamNotAll)
                if matchedScroe >= self.baselinscore or matchedScroe1 >= baselinscore:
                    print("队员成员已不足，自行退队！")
                    self.sig.emit("队员成员已不足，自行退队！")    
                    self.enablePlayerMode = False
                    self.click_Image(quitTeam)
                    self.close_Windows()
                else:
                    print("组队状态检测中...")
                    self.sig.emit("组队状态检测中...")
                    self.close_Windows()    

            #若启用了双开，当切换到第二个号时退出队伍
            if self.enableDoubleStart and self.window != self.allWindows[0]:
                print("切换到第二个账号，准备退出队伍！")
                self.sig.emit("切换到第二个账号，准备退出队伍！")
                win32gui.SetForegroundWindow(self.window)
                time.sleep(2)
                pyautogui.keyDown('altleft')
                pyautogui.press('t')
                pyautogui.keyUp('altleft')
                time.sleep(2)
                self.click_Image(quitTeam)
                self.close_Windows()                 

            for jobitem in self.mode:
                if jobitem == "11":
                    self.sig.emit("师门任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    shiMenjob = self.curdir + r"\image\StartJob\StartJob_ShiMen.png"
                    shiMenCloseTips = self.curdir + r"\image\StartJob\ShiMen_CloseTips.png"
                    self.start_job(shiMenjob)
                    time.sleep(5)
                    shimenIdle = 0
                    while shimenIdle < 8:                   
                        mainPos = win32gui.GetWindowRect(self.window)                
                        print("当前师门空闲次数:" + str(shimenIdle))
                        self.sig.emit("当前师门空闲次数:" + str(shimenIdle))
                        for filename in os.listdir(self.shiMen):
                            if filename != "Answer":
                                curfilename = os.path.join(self.shiMen, filename) 
                                self.capture_img(self.window, self.curimg)                       
                                matchedScroe, poction = self.search_position(self.curimg, curfilename)
                                if matchedScroe >= self.baselinscore:
                                    shimenIdle = 0
                                    if filename == "Shimen_AFighting.png":
                                        print("师门任务战斗中...")
                                        self.sig.emit("师门任务战斗中...")
                                        time.sleep(10)
                                        break
                                    elif filename == "Shimen_ShangChengGoumai.png":
                                        print("检测到师门商城购买！")
                                        self.sig.emit("检测到师门商城购买！")
                                        self.close_Windows()
                                        pyautogui.keyDown('altleft')
                                        pyautogui.press('y')
                                        pyautogui.keyUp('altleft')
                                        time.sleep(2)
                                        shiMenCurrentRW = self.curdir + r"\image\StartJob\ShiMen_DQRenWu.png"
                                        shiMenFQRW = self.curdir + r"\image\StartJob\ShiMen_FQRW.png"
                                        shiMenFQRWConform = self.curdir + r"\image\StartJob\ShiMen_FQRWConform.png"
                                        shiMenFQXuanZe = self.curdir + r"\image\StartJob\ShiMen_FQXuanZe.png"
                                        print("师门任务放弃处理！")
                                        self.sig.emit("师门任务放弃处理！")
                                        self.click_Image(shiMenCurrentRW)
                                        time.sleep(2)
                                        self.click_Image(shiMenFQXuanZe)
                                        time.sleep(2)
                                        self.click_Image(shiMenFQRW)
                                        time.sleep(2)
                                        self.click_Image(shiMenFQRWConform)
                                        time.sleep(2)
                                        self.click_Image(shiMenFQRWConform)
                                        time.sleep(2)
                                        pyautogui.keyDown('altleft')
                                        pyautogui.press('y')
                                        pyautogui.keyUp('altleft')
                                        shimenIdle = 10
                                        break
                                    elif filename == "ShiMen_Chuti.png":
                                        #进入答题模式
                                        win32gui.SetForegroundWindow(self.window)
                                        print("师门任务准备答题。")
                                        self.sig.emit("师门任务准备答题。")
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc,ycurpoc)
                                        #开始答题
                                        shiMenAnswer = self.shiMen + r"\Answer"
                                        for filename in os.listdir(shiMenAnswer):
                                            curfilename = os.path.join(shiMenAnswer, filename) 
                                            self.capture_img(self.window, self.curimg)                       
                                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                                            if matchedScroe >= self.baselinscore:
                                                win32gui.SetForegroundWindow(self.window)
                                                print("师门任务答题中...")
                                                self.sig.emit("师门任务答题中...")
                                                xcurpoc = mainPos[0] + poction[0] + 50
                                                ycurpoc = mainPos[1] + poction[1] + 50
                                                self.simulate_mouse(xcurpoc,ycurpoc)
                                                time.sleep(2)
                                                self.click_Image(shiMenCloseTips)
                                                break
                                        break
                                    else:
                                        win32gui.SetForegroundWindow(self.window)
                                        print(matchedScroe, baselinscore)
                                        print("师门任务操作中")
                                        self.sig.emit("师门任务操作中")
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc,ycurpoc)
                                        time.sleep(2)
                                        break
                                else:
                                    print("师门任务检查中:" + filename)
                                    self.sig.emit("师门任务检查中:" + filename)
                        #查找任务图标
                        if shimenIdle > 1:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(2)
                                #查找师门任务图标
                                shiMenLocation = self.curdir + r"\image\StartJob\Location_shiMen.png"
                                self.capture_img(self.window, self.curimg)
                                matchedScroe, poction = self.search_position(self.curimg, shiMenLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("查找师门任务文字：", shiMenLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("点击师门任务处理!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(2)             
                        if shimenIdle > 3:
                            self.close_Windows()
                        shimenIdle += 1
                    print("师门任务结束")
                    self.sig.emit("师门任务结束")            
                elif jobitem == "4":
                    self.sig.emit("秘境任务即将开始...")
                    time.sleep(5)
                    self.close_Windows()
                    miJingjob = self.curdir + r"\image\StartJob\StartJob_MiJing.png"
                    self.start_job(miJingjob)
                    time.sleep(5)
                    miJingIdle = 0
                    miJingNum = 0
                    while miJingIdle < 8:
                        for filename in os.listdir(self.miJing):
                            curfilename = os.path.join(self.miJing, filename)
                            mainPos = win32gui.GetWindowRect(self.window)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                miJingIdle = 0                        
                                print(matchedScroe, self.baselinscore)
                                if filename == "MiJing_AFighting.png":
                                    print("秘境战斗中...")
                                    self.sig.emit("秘境战斗中...")
                                    time.sleep(15)                                  
                                    break
                                elif filename == "MiJing_StartFighint.png":
                                    if miJingNum < self.miJingCount:
                                        print("秘境点击战斗...")
                                        self.sig.emit("秘境点击战斗...")
                                        win32gui.SetForegroundWindow(window)
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc, ycurpoc)   
                                        miJingNum += 1
                                        print("当前头领挑战数量:" + str(miJingNum))
                                        self.sig.emit("当前头领挑战数量:" + str(miJingNum))                                    
                                        time.sleep(3)
                                        break
                                    else:
                                        #离开秘境
                                        miJingLiKai = self.curdir + r"\image\StartJob\MiJing_LiKai.png"
                                        self.capture_img(self.window, self.curimg)
                                        matchedScroe, poction = self.search_position(self.curimg, miJingLiKai)
                                        if matchedScroe >= self.baselinscore:
                                            print("秘境战斗结束，离开秘境！")
                                            self.sig.emit("秘境战斗结束，离开秘境！")
                                            win32gui.SetForegroundWindow(window)
                                            xcurpoc = mainPos[0] + poction[0] + 50
                                            ycurpoc = mainPos[1] + poction[1] + 50
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            miJingIdle = 10
                                            break                                          
                                elif filename == "MiJing_ShiBai.png":
                                    #离开秘境
                                    print("秘境挑战失败...")
                                    self.sig.emit("秘境挑战失败...")
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)                                      
                                    time.sleep(3)
                                    miJingLiKai = self.curdir + r"\image\StartJob\MiJing_LiKai.png"
                                    self.capture_img(self.window, self.curimg)
                                    matchedScroe, poction = self.search_position(self.curimg, miJingLiKai)
                                    if matchedScroe >= self.baselinscore:
                                        print("秘境战斗失败，离开秘境！")
                                        self.sig.emit("秘境战斗失败，离开秘境！")
                                        win32gui.SetForegroundWindow(window)
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc, ycurpoc)
                                        self.simulate_mouse(xcurpoc, ycurpoc)
                                        miJingIdle = 10
                                        break 
                                elif filename == "MiJing_ZJinRu.png":
                                    print("进入秘境...")
                                    self.sig.emit("进入秘境...")
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 60
                                    ycurpoc = mainPos[1] + poction[1] - 20
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(3)
                                    break                                
                                else:
                                    print("该任务已匹配:" + filename)
                                    self.sig.emit("该任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(3)
                                    break
                            else:
                                print("秘境任务检查中:" + filename)
                                print(matchedScroe, self.baselinscore)
                                self.sig.emit("秘境任务检查中:" + filename)                        
                        if miJingIdle > 3:
                            self.close_Windows()
                        miJingIdle += 1
                    print("秘境任务结束")
                    self.sig.emit("秘境任务结束")
                elif jobitem == "5":
                    self.sig.emit("打图任务即将开始...")
                    time.sleep(5)
                    self.close_Windows()
                    datujob = self.curdir + r"\image\StartJob\StartJob_DaTu.png"
                    datuCloseTips = self.curdir + r"\image\StartJob\DaTu_DianXiaoEr.png"
                    self.start_job(datujob)
                    time.sleep(5)
                    datuIdle = 0
                    while datuIdle < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        for filename in os.listdir(self.daTu):
                            curfilename = os.path.join(self.daTu, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                datuIdle = 0
                                if filename == "DaTu_JobStart.png":
                                    print("打图任务进行中...")
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("该任务已匹配：", filename)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    break
                                elif filename == "DaTu_Fighting.png":
                                    print("打图任务战斗中...")
                                    self.sig.emit("打图任务战斗中...")
                                    time.sleep(10)
                                    break
                                elif filename == "DaTu_LQRW.png":
                                    print("领取打图任务！")
                                    self.sig.emit("领取打图任务！")
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    self.click_Image(datuCloseTips)
                                    break
                                else:
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    break
                            else:
                                print("打图任务检测中:"+ filename)
                                self.sig.emit("打图任务检测中:" + filename)
                        #查找任务图标
                        if datuIdle > 2:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(2)
                                #查找打图任务图标
                                daTuLocation = self.curdir + r"\image\DaTu\DaTu_JobStart.png"
                                self.capture_img(self.window, self.curimg)
                                matchedScroe, poction = self.search_position(self.curimg, daTuLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("查找打图任务文字：", daTuLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("点击打图任务处理!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(2)                    
                        if datuIdle > 3:
                            self.close_Windows()
                        datuIdle += 1                            
                    print("打图任务结束")
                    self.sig.emit("打图任务结束")
                elif jobitem == "2":
                    if self.enableDoubleStart and self.window == self.allWindows[1]:
                        continue
                    self.sig.emit("副本任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    fuben_ico = list()
                    fuben_ico.append(self.curdir + r"\image\StartJob\FuBen\FuBen_LLS_PT.png")
                    fuben_ico.append(self.curdir + r"\image\StartJob\FuBen\FuBen_LSJ_PT.png")
                    fuben_ico.append(self.curdir + r"\image\StartJob\FuBen\FuBen_LYRM_PT.png")
                    fuben_ico.append(self.curdir + r"\image\StartJob\FuBen\FuBen_LYRM_XS.png")
                    fuben_ico.append(self.curdir + r"\image\StartJob\FuBen\FuBen_THDQ_XS.png")
                    fuBenRW = self.curdir + r"\image\FuBen\FuBen_FXuanZe.png"
                    #进入副本
                    fuBenStart = True
                    while fuBenStart:
                        for item in fuben_ico:
                            print(item)
                            self.start_job(item)
                            print("副本进入匹配中:" + item)
                            self.sig.emit("副本进入匹配中:" + item)                            
                            time.sleep(2)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, fuBenRW)
                            if matchedScroe >= self.baselinscore:
                                fuBenStart = False
                                break
                    time.sleep(5)
                    fuBen_InputICO = list() 
                    fuBen_InputICO.append(self.curdir + r"\image\StartJob\FuBen\FuBen_Input_LYRM_PT.png")
                    fuBen_InputICO.append(self.curdir + r"\image\StartJob\FuBen\FuBen_Input_LLS_PT.png")
                    fuBen_InputICO.append(self.curdir + r"\image\StartJob\FuBen\FuBen_Input_LSJ_PT.png")
                    fuBen_InputICO.append(self.curdir + r"\image\StartJob\FuBen\FuBen_Input_THDQ_PT.png")
                    fuBenIdle = 0
                    fuBenNum = 0
                    while fuBenIdle < 8:
                        print("当前的副本空闲次数为：", fuBenIdle)
                        for filename in os.listdir(self.fuBen):
                            curfilename = os.path.join(self.fuBen, filename)
                            self.capture_img(self.window, self.curimg)
                            mainPos = win32gui.GetWindowRect(self.window)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                fuBenIdle = 0
                                if filename == "FuBen_AFighting.png" or filename == "FuBen_AFZhenFa.png":
                                    print("副本战斗中...")
                                    self.sig.emit("副本战斗中...")
                                    time.sleep(10)
                                    break
                                elif filename == "FuBen_FXuanZe.png":
                                    win32gui.SetForegroundWindow(self.window)                                    
                                    print("进入副本...")
                                    self.sig.emit("进入副本...")
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(5)
                                    #根据当前次数进入相应副本
                                    self.capture_img(self.window, self.curimg)
                                    if fuBenNum < 2:
                                        curFuBen = fuBen_InputICO[fuBenNum]
                                        matchedScroe, poction = self.search_position(self.curimg, curFuBen)
                                        if matchedScroe >= self.baselinscore:
                                            #fuBenCount 为3的情况下，第三次进入副本时，fuBenNum为2
                                            if fuBenNum < self.fuBenCount:                                            
                                                win32gui.SetForegroundWindow(self.window)
                                                print(matchedScroe, self.baselinscore)
                                                print("进入副本")
                                                self.sig.emit("进入副本,当前副本轮数为:"+str(fuBenNum + 1))
                                                xcurpoc = mainPos[0] + poction[0] + 50
                                                ycurpoc = mainPos[1] + poction[1] + 230
                                                self.simulate_mouse(xcurpoc, ycurpoc)
                                                fuBenNum += 1
                                    else:
                                        curFuBen = fuBen_InputICO[fuBenNum]
                                        curFuBen1 = fuBen_InputICO[fuBenNum + 1]
                                        matchedScroe, poction = self.search_position(self.curimg, curFuBen)
                                        matchedScroe1, poction1 = self.search_position(self.curimg, curFuBen1)
                                        if matchedScroe >= self.baselinscore:
                                            #fuBenCount 为3的情况下，第三次进入副本时，fuBenNum为2                                          
                                            win32gui.SetForegroundWindow(self.window)
                                            print(matchedScroe, self.baselinscore)
                                            print("进入副本")
                                            self.sig.emit("进入副本,当前副本轮数为:"+str(fuBenNum + 1))
                                            xcurpoc = mainPos[0] + poction[0] + 50
                                            ycurpoc = mainPos[1] + poction[1] + 230
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            fuBenNum += 1
                                        elif matchedScroe1 >= self.baselinscore:                                        
                                            #fuBenCount 为3的情况下，第三次进入副本时，fuBenNum为2                                           
                                            win32gui.SetForegroundWindow(self.window)
                                            print(matchedScroe, self.baselinscore)
                                            print("进入副本")
                                            self.sig.emit("进入副本,当前副本轮数为:"+str(fuBenNum + 1))
                                            xcurpoc = mainPos[0] + poction1[0] + 50
                                            ycurpoc = mainPos[1] + poction1[1] + 230
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            fuBenNum += 1
                                    break
                                elif filename == "FuBen_ZFinish.png":
                                    print("当前副本结束...")
                                    self.sig.emit("当前副本结束...")
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(5)
                                    print(fuBenNum)
                                    #再次进入副本
                                    if fuBenNum < self.fuBenCount:
                                        print("开始下一轮副本,当前轮数为:" + str(fuBenNum))
                                        self.sig.emit("开始下一轮副本,当前轮数为:" + str(fuBenNum))                                    
                                        fuBenStart = True
                                        while fuBenStart:
                                            for item in fuben_ico:
                                                print(item)
                                                self.start_job(item)
                                                print("副本进入匹配中:" + item)
                                                self.sig.emit("副本进入匹配中:" + item)
                                                time.sleep(2)
                                                self.capture_img(self.window, self.curimg)
                                                matchedScroe, poction = self.search_position(self.curimg, fuBenRW)
                                                if matchedScroe >= self.baselinscore:
                                                    fuBenStart = False
                                                    break
                                    else:
                                        fuBenIdle = 8
                                        break                                   
                                elif filename == "FuBen_ZZDoing.png":
                                    print("使用副本默认任务处理...")
                                    self.sig.emit("使用副本默认任务处理...")
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 10
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(5)
                                    break
                                else:
                                    print("副本任务已匹配:" + filename)
                                    self.sig.emit("副本任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("副本任务检查中:" + filename)
                                self.sig.emit("副本任务检查中:" + filename)
                                print(matchedScroe, self.baselinscore)
                        if fuBenIdle > 3:
                            self.close_Windows()
                        fuBenIdle += 1                            
                    print("副本任务结束")
                    self.sig.emit("副本任务结束")
                    #如果包含副本，则在副本结束后退出队伍
                    if quitTeamEnable:
                        print("副本结束，退出组队进入单人任务！")
                        self.sig.emit("副本结束，退出组队进入单人任务！")
                        pyautogui.keyDown('altleft')
                        pyautogui.press('t')
                        pyautogui.keyUp('altleft')
                        time.sleep(2)
                        self.click_Image(quitTeam)
                        self.close_Windows()            
                elif jobitem == "3":
                    self.sig.emit("押镖任务即将开始...")
                    time.sleep(5)
                    self.close_Windows()
                    yabiaojob = self.curdir + r"\image\StartJob\StartJob_YaBiao.png"
                    self.start_job(yabiaojob)
                    time.sleep(5)
                    yaBiaoCount = 0
                    yaBiaoIdle = 0
                    while yaBiaoCount < 3 and yaBiaoIdle < 8:
                        for filename in os.listdir(self.yaBiao):
                            curfilename = os.path.join(self.yaBiao, filename)
                            self.capture_img(self.window, self.curimg)
                            mainPos = win32gui.GetWindowRect(self.window)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                yaBiaoIdle = 0
                                print(matchedScroe, self.baselinscore)
                                if filename == "YaBiao_ARuning.png":
                                    print("押镖进行中...")
                                    self.sig.emit("押镖进行中...")
                                    time.sleep(10)
                                    break
                                elif filename == "YaBiao_AFighting.png":
                                    print("押镖战斗中...")
                                    self.sig.emit("押镖战斗中...")
                                    time.sleep(10)
                                    break                           
                                elif filename == "YaBiao_Conform.png":
                                    yaBiaoCount += 1
                                    self.sig.emit("押镖任务即将开始,当前轮次为:"+ str(yaBiaoCount))
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 100
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    break
                                else:
                                    print("该任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 40
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    break
                            else:
                                print("运镖任务检查中:" + filename)
                                self.sig.emit("运镖任务检查中:" + filename)
                        if yaBiaoIdle > 3:
                            self.close_Windows()
                        yaBiaoIdle += 1
                    #押镖最后一次领取任务就退出循环，需要检测当前押镖任务是否完成
                    yaBiaoEndCheck = True
                    while yaBiaoEndCheck:
                        self.capture_img(self.window, self.curimg)
                        matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                        if matchedScroe >= self.baselinscore:
                            yaBiaoEndCheck = False
                            print("检测到最后一轮押镖任务完成，进入下一个任务环节！")
                            self.sig.emit("检测到最后一轮押镖任务完成，进入下一个任务环节！")
                        else:
                            print("等待最后一轮押镖任务完成！")
                            self.sig.emit("等待最后一轮押镖任务完成！")
                            time.sleep(10)                            
                    print("运镖任务结束")
                    self.sig.emit("运镖任务结束")
                elif jobitem == "1":
                    if self.enableDoubleStart and self.window == self.allWindows[1]:
                        continue    
                    self.sig.emit("抓鬼任务开始...")
                    time.sleep(5)
                    # 任务菜单检测中并点击
                    self.close_Windows()
                    zhuaguijob = self.curdir + r"\image\StartJob\StartJob_ZhuaGui.png"
                    zhuaGuiCloseTips = self.curdir + r"\image\StartJob\ZhuaGui_ZhongKui.png"
                    self.start_job(zhuaguijob)
                    time.sleep(5)
                    zhuaguiidle=0
                    curzhuaGuiCount = 0
                    while zhuaguiidle < 8 and curzhuaGuiCount < self.zhuaGuiCount:
                        # 抓鬼检测中
                        mainPos = win32gui.GetWindowRect(self.window)
                        for filename in os.listdir(self.zhuaGuidir):
                            curfilename = os.path.join(self.zhuaGuidir, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                zhuaguiidle = 0
                                print(matchedScroe, self.baselinscore)
                                print("该任务已匹配：", filename)
                                if filename == "ZhuaGui_Fighting.png":
                                    print("抓鬼战斗中...")
                                    self.sig.emit("抓鬼战斗中...")
                                    time.sleep(10)
                                    break
                                elif filename == "ZhuaGui_LQRW.png":
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    self.click_Image(zhuaGuiCloseTips)
                                    break
                                elif filename == "ZhuaGui_NextGo.png":
                                    curzhuaGuiCount += 1
                                    self.sig.emit("当前抓鬼轮数为:" + str(curzhuaGuiCount))
                                    if curzhuaGuiCount >= self.zhuaGuiCount:
                                        zhuaguiidle = 10
                                        break
                                    else:
                                        win32gui.SetForegroundWindow(self.window)
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 100
                                        self.simulate_mouse(xcurpoc, ycurpoc)
                                        time.sleep(1)
                                        break
                                else:
                                    # 结束当前轮抓鬼任务，点击确认按钮
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                                    break
                            else:
                                print("抓鬼任务检查中:" + filename)
                                self.sig.emit("抓鬼任务检查中:" + filename)
                                time.sleep(0.5)
                        if zhuaguiidle > 2:
                            #查找任务图标                    
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("抓鬼任务查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(2)
                                #查找抓鬼任务图标
                                self.capture_img(self.window, self.curimg)
                                matchedScroe, poction = self.search_position(self.curimg, self.zgLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("定位到抓鬼任务：", self.zgLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("使用抓鬼默认任务处理!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)                        
                                    time.sleep(2)                       
                        if zhuaguiidle > 3:
                            self.close_Windows()
                        zhuaguiidle += 1
                    print("抓鬼任务结束")
                    self.sig.emit("抓鬼任务结束")
                    #如果不包含副本，则在完成抓鬼后队长退出队伍
                    if quitTeamEnable == True and "2" not in self.mode:
                        print("抓鬼结束，退出组队进入单人任务！")
                        self.sig.emit("抓鬼结束，退出组队进入单人任务！")
                        pyautogui.keyDown('altleft')
                        pyautogui.press('t')
                        pyautogui.keyUp('altleft')
                        time.sleep(2)
                        self.click_Image(quitTeam)
                        self.close_Windows() 
                elif jobitem == "7":
                    self.sig.emit("帮派任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    bangPaijob = self.curdir + r"\image\StartJob\StartJob_BangPai.png"
                    self.start_job(bangPaijob)
                    time.sleep(5)
                    bangPaiidle = 0
                    while bangPaiidle < 8:
                        for filename in os.listdir(self.bangPai):
                            mainPos = win32gui.GetWindowRect(self.window)
                            self.capture_img(self.window, self.curimg)
                            curfilename = os.path.join(self.bangPai, filename)                            
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                bangPaiidle = 0
                                if filename == "BangPai_AFighting.png":
                                    self.sig.emit("帮派任务战斗中...")
                                    print("帮派任务战斗中...")
                                    time.sleep(10)
                                    break
                                elif filename == "BangPai_ZZQingLong.png" or filename == "BangPai_ZZZhuQue.png" or filename == "BangPai_ZZXuanWu.png":
                                    self.sig.emit("帮派默认任务已匹配:"+ filename)
                                    print("帮派默认任务已匹配:"+ filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc,ycurpoc)
                                    self.simulate_mouse(xcurpoc,ycurpoc)
                                    time.sleep(1)
                                    break
                                else:
                                    self.sig.emit("该任务已匹配:"+ filename)
                                    print("该任务已匹配:"+ filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc,ycurpoc)
                                    time.sleep(1)
                                    break
                            else:                                                        
                                print("帮派任务检查中:", filename)
                                self.sig.emit("帮派任务检查中:"+ filename)
                        if bangPaiidle > 2:                            
                            mainPos = win32gui.GetWindowRect(self.window)
                            self.capture_img(self.window, self.curimg)
                            #关闭左下角任务提示
                            bangPaiTipsClose = self.curdir + r"\image\StartJob\ShiMen_CloseTips.png"
                            matchedScroe, poction = self.search_position(self.curimg, bangPaiTipsClose)
                            if matchedScroe >= self.baselinscore:
                                win32gui.SetForegroundWindow(self.window)
                                xcurpoc = mainPos[0] + poction[0] + 50
                                ycurpoc = mainPos[1] + poction[1] + 50
                                print("帮派任务左下角Tips关闭中...")
                                self.sig.emit("帮派任务左下角任务关闭中...")
                                self.simulate_mouse(xcurpoc,ycurpoc)
                                time.sleep(1)
                            #滑动任务查找帮派任务
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("任务图标查找中...")
                                self.sig.emit("任务图标查找中...")
                                win32gui.SetForegroundWindow(self.window)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(2)
                                #查找帮派任务图标
                                bangPaiIco = list()
                                bangPaiIco1 = self.curdir + r"\image\BangPai\BangPai_ZZQingLong.png"
                                bangPaiIco2 = self.curdir + r"\image\BangPai\BangPai_ZZXuanWu.png"
                                bangPaiIco3 = self.curdir + r"\image\BangPai\BangPai_ZZZhuQue.png"
                                bangPaiIco.append(bangPaiIco1)
                                bangPaiIco.append(bangPaiIco2)
                                bangPaiIco.append(bangPaiIco3)
                                for item in bangPaiIco:
                                    mainPos = win32gui.GetWindowRect(self.window)
                                    self.capture_img(self.window, self.curimg)
                                    matchedScroe, poction = self.search_position(self.curimg, item)
                                    if matchedScroe >= self.baselinscore:
                                        print("帮派任务查找处理中:" + item)
                                        self.sig.emit("帮派任务查找处理中:" + item)
                                        win32gui.SetForegroundWindow(self.window)
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc, ycurpoc)                        
                                        time.sleep(1)
                                        break
                        if bangPaiidle > 3:
                            self.close_Windows()
                        bangPaiidle += 1                            
                    print("帮派任务结束")
                    self.sig.emit("帮派任务结束") 
                elif jobitem == "8":
                    self.sig.emit("经验链任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    time.sleep(5)
                    shopingOK = False
                    jingYanLianIdletime = 0
                    while jingYanLianIdletime < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        for filename in os.listdir(self.renWuLian):
                            curfilename = os.path.join(self.renWuLian, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                jingYanLianIdletime =0
                                if filename == "RWL_Fighting.png":
                                    print("经验链任务战斗中...")
                                    self.sig.emit("经验链任务战斗中...")
                                    time.sleep(10)
                                    break
                                elif filename == "RWL_ZZCloseTips.png":
                                    win32gui.SetForegroundWindow(self.window)
                                    xcurpoc = mainPos[0] + poction[0] + 500
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break                                      
                                elif filename == "RWL_PuringYD.png":
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    self.sig.emit("药品购买中..."+ filename)
                                    print("药品购买中...", filename)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    self.close_Windows()
                                    time.sleep(15)
                                    break                                   
                                elif filename == "RWL_ZShangchengClose.png" and shopingOK == False:
                                    print("检测到经验链商城购买!")
                                    self.sig.emit("检测到经验链商城购买!")
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    print("关闭商城")
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(2)
                                    #开始挂机
                                    self.capture_img(self.window, self.curimg)
                                    guajiimge = self.curdir + r"\image\MainUI\Renwulian_Guaji.png"
                                    matchedScroe, poction = self.search_position(self.curimg, guajiimge)
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 30
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    print("打开挂机按钮")
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(2)
                                    self.capture_img(self.window, self.curimg)
                                    guajiimge = self.curdir + r"\image\MainUI\Renwulian_MiGong.png"
                                    matchedScroe, poction = self.search_position(self.curimg, guajiimge)
                                    print(matchedScroe, self.baselinscore)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    # 任务环挂机中
                                    guajiEnd = True
                                    guajiTime = 0
                                    while guajiEnd and guajiTime < 80:
                                        time.sleep(10)
                                        guajiTime += 1
                                        guajiimge = self.curdir + r"\image\RenWuLian\RWL_XunWu.png"
                                        guajitj = self.curdir + r"\image\RenWuLian\RWL_Shangjiao.png"
                                        self.capture_img(self.window, self.curimg)
                                        print("经验链挂机战斗中，当前时长：", guajiTime * 10)
                                        self.sig.emit("经验链挂机战斗中，当前时长："+ str(guajiTime * 10))
                                        matchedScroe, poction = self.search_position(self.curimg, guajiimge)
                                        matchedScroe2, poction = self.search_position(self.curimg, guajitj)
                                        if(matchedScroe >= self.baselinscore or matchedScroe2 >= self.baselinscore):
                                            guajiEnd = False
                                            print(matchedScroe, self.baselinscore)
                                            print("经验链挂机战斗结束")
                                            self.sig.emit("经验链挂机战斗结束")
                                            break
                                    #挂机超时检测
                                    if guajiTime >= 80:
                                        stopMark = True
                                        while stopMark:
                                            self.capture_img(self.window, self.curimg)                                            
                                            matchedScroe, poction = self.search_position(self.curimg, (self.curdir + r"\image\StartJob\Location_NoFighting.png"))
                                            print("经验链挂机超时，战斗结束检测中...")
                                            self.sig.emit("经验链挂机超时，战斗结束检测中...")
                                            self.sig.emit("匹配度为："+str(matchedScroe))
                                            if matchedScroe >= self.baselinscore:
                                                #点击屏幕中央位置
                                                xcurpoc = mainPos[0]  + 600
                                                ycurpoc = mainPos[1]  + 300
                                                print("经验链挂机超时，停止中...")
                                                self.sig.emit("经验链挂机超时，停止中...")
                                                self.simulate_mouse(xcurpoc, ycurpoc)
                                                self.simulate_mouse(xcurpoc, ycurpoc)
                                                time.sleep(3)
                                                self.capture_img(self.window, self.curimg)
                                                matchedScroe, poction = self.search_position(self.curimg, (self.curdir + r"\image\StartJob\Location_NoFighting.png"))
                                                time.sleep(3)
                                                self.capture_img(self.window, self.curimg)
                                                matchedScroe1, poction1 = self.search_position(self.curimg,(self.curdir + r"\image\RenWuLian\RWL_Fighting.png"))
                                                time.sleep(3)
                                                self.capture_img(self.window, self.curimg)
                                                matchedScroe2, poction2 = self.search_position(self.curimg, (self.curdir + r"\image\StartJob\Location_NoFighting.png"))
                                                #在地狱迷宫内，3秒钟后不在战斗中，则退出
                                                if matchedScroe >= self.baselinscore and matchedScroe1 < self.baselinscore and matchedScroe2 >= self.baselinscore:
                                                    shopingOK = True
                                                    break
                                    break
                                elif filename == "RWL_ShopingOK.png":
                                    print(shopingOK)
                                    if shopingOK == True:
                                        print("挂机超时，商城购买！")
                                        self.sig.emit("挂机超时，商城购买！")
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc, ycurpoc)
                                        shopingOK = False
                                        break
                                else:
                                    print("经验链该任务已匹配" +  filename)
                                    win32gui.SetForegroundWindow(window)
                                    time.sleep(0.5)
                                    print(matchedScroe, self.baselinscore)
                                    self.sig.emit("经验链任务操作中:" + filename)
                                    print("经验链任务操作中:" + filename)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("经验链任务检查中:" + filename)
                                self.sig.emit("经验链任务检查中:" + filename)
                        #查找任务图标
                        if jingYanLianIdletime > 2:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("经验链任务查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(2)

                                #查找任务链图标
                                self.capture_img(self.window, self.curimg)
                                matchedScroe, poction = self.search_position(self.curimg, self.rwlLocation)
                                if matchedScroe >= self.baselinscore:
                                    if poction[1] < 500:
                                        print("定位到经验链任务：", self.rwlLocation)
                                        win32gui.SetForegroundWindow(self.window)
                                        print(matchedScroe, self.baselinscore)
                                        print("使用经验链默认任务处理!")
                                        xcurpoc = mainPos[0] + poction[0] + 50
                                        ycurpoc = mainPos[1] + poction[1] + 50
                                        self.simulate_mouse(xcurpoc, ycurpoc)                        
                                        time.sleep(2)
                        if jingYanLianIdletime > 3:
                            self.close_Windows()
                        jingYanLianIdletime += 1                           
                    print("经验链任务结束")
                    self.sig.emit("经验链任务结束") 
                elif jobitem == "9":
                    self.sig.emit("门派闯关任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    menPaijob = self.curdir + r"\image\StartJob\StartJob_MenPai.png"
                    self.start_job(menPaijob)
                    time.sleep(5)
                    chuangGuanIdle = 0
                    while chuangGuanIdle < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        print("当前门派闯关空闲检测次数为:" + chuangGuanIdle)
                        self.sig.emit("当前门派闯关空闲检测次数为:" + str(chuangGuanIdle))
                        for filename in os.listdir(self.menPai):
                            curfilename = os.path.join(self.menPai, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                chuangGuanIdle = 0
                                if filename == "MenPai_Fighting.png":
                                    print("战斗中...")
                                    time.sleep(5)
                                    break
                                else:
                                    print("门派闯关任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, baselinscore)
                                    print("门派闯关任务操作中...")
                                    self.sig.emit("门派闯关任务操作中...")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    continue
                            else:
                                print("门派闯关任务检查中:" + filename)
                                self.sig.emit("门派闯关任务检查中:" + filename)
                        #查找任务图标
                        if chuangGuanIdle > 2:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(1)
                                #查找门派挑战任务
                                self.capture_img(self.window, self.curimg)
                                matchedScroe, poction = self.search_position(self.curimg, self.mpLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("查找门派挑战任务文字：", self.mpLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("点击门派挑战默认任务处理!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                        if chuangGuanIdle > 3:
                            self.close_Windows()
                        chuangGuanIdle += 1
                    print("门派挑战任务结束")
                    self.sig.emit("门派挑战任务结束") 
                elif jobitem == "6":
                    print("挖图任务开始...")
                    self.sig.emit("挖图任务开始...")
                    time.sleep(5)
                    win32gui.SetForegroundWindow(self.window)
                    self.close_Windows()
                    pyautogui.keyDown('altleft')
                    pyautogui.press('e')
                    pyautogui.keyUp('altleft')
                    baoTuZhengli = self.curdir + r"\image\StartJob\WaTu_ZhengLi.png"
                    baoTuImge = self.curdir + r"\image\StartJob\WaTu_BaoTu.png"
                    baoTuShiYong = self.curdir + r"\image\StartJob\WaTu_ShiYong.png"
                    baoTUWuPindown = self.curdir + r"\image\StartJob\WaTu_WuPin.png"                
                    self.click_Image(baoTuZhengli)
                    mainPos = win32gui.GetWindowRect(self.window)
                    self.capture_img(self.window, self.curimg)
                    matchedScroe, poction = self.search_position(self.curimg, baoTUWuPindown)
                    if matchedScroe >= self.baselinscore:
                        print("识别到挖图物品栏")
                        xcurpoc = mainPos[0] + poction[0]
                        ycurpoc = mainPos[1] + poction[1] + 100
                        self.roll_mouse(xcurpoc, ycurpoc)    
                    self.click_Image(baoTuImge)
                    self.click_Image(baoTuShiYong)          
                    waTuIdel = 0
                    while waTuIdel < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        for filename in os.listdir(self.waTu):
                            curfilename = os.path.join(self.waTu, filename)
                            time.sleep(2)
                            self.capture_img(self.window, curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                waTuIdel =0
                                if filename == "Watu_Fighting.png":
                                    print("挖图战斗中...")
                                    self.sig.emit("挖图战斗中...")
                                else:
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("该任务已匹配：", filename)
                                    self.sig.emit("挖图进行中...")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 150
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(5)
                            else:
                                print("挖图任务检查中:"+ filename)
                                self.sig.emit("挖图任务检查中:"+ filename)
                                # 检测是否有打开的窗口进行关闭
                        if waTuIdel >3:
                            self.close_Windows()
                        waTuIdel += 1
                    print("挖图任务结束")
                    self.sig.emit("挖图任务结束") 
                elif jobitem == "10":
                    self.sig.emit("挖矿任务开始...")
                    time.sleep(5)
                    win32gui.SetForegroundWindow(self.window)
                    self.close_Windows()
                    pyautogui.keyDown('altleft')
                    pyautogui.press('m')
                    pyautogui.keyUp('altleft')
                    time.sleep(2)
                    mainPos = win32gui.GetWindowRect(self.window)
                    self.simulate_mouse(mainPos[0] + 770 ,mainPos[1] + 400)
                    #优先使用固定位置方法进行点击
                    #waKuangDongHaiWan = self.curdir + r"\image\StartJob\WaKuang_DongHaiWan.png"
                    #self.click_Image(waKuangDongHaiWan) 
                    closeRenWuTips = self.curdir + r"\image\MainUI\RenWu_Closed.png"                           
                    waKuangCount = 0
                    waKuangIdle = 0
                    while waKuangIdle < 24 and waKuangCount < 40:
                        mainPos = win32gui.GetWindowRect(self.window)
                        self.click_Image(closeRenWuTips)
                        print("当前挖矿空闲次数:",waKuangIdle)
                        self.sig.emit("当前挖矿空闲次数:"+str(waKuangIdle))
                        for filename in os.listdir(self.waKuang):
                            curfilename = os.path.join(self.waKuang, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:                        
                                waKuangIdle = 0
                                print("挖矿任务已匹配：", filename)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                if filename == "WaKuang_Wajue.png":
                                    waKuangCount += 1
                                    print("挖矿触发")
                                    self.sig.emit("当前挖矿次数为：" + str(waKuangCount))
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.sig.emit("挖矿操作中")
                                    self.simulate_mouse(xcurpoc,ycurpoc)
                                    time.sleep(5)
                                    break
                                elif filename == "WaKuang_Doing.png":
                                    print("采矿中...")
                                    self.sig.emit("采矿中...")
                                    time.sleep(3)
                                    break
                                else:
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.sig.emit("挖矿操作中")
                                    self.simulate_mouse(xcurpoc,ycurpoc)
                                    time.sleep(1)
                                    break
                            else:
                                print("挖矿任务检查中:" + filename)
                                self.sig.emit("挖矿任务检查中:" + filename)
                        waKuangIdle += 1
                        if waKuangIdle > 3:                    
                            self.close_Windows()
                    print("挖矿任务结束")
                    self.sig.emit("挖矿任务结束") 
                elif jobitem == "12":
                    self.sig.emit("海底寻宝任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    xunBaojob = self.curdir + r"\image\StartJob\StartJob_XunBao.png"
                    self.start_job(xunBaojob)
                    time.sleep(5)
                    chuangGuanIdle = 0
                    while chuangGuanIdle < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        print("当前海底寻宝任务空闲检测次数为:" + str(chuangGuanIdle))
                        self.sig.emit("当前海底寻宝任务空闲检测次数为:" + str(chuangGuanIdle))
                        for filename in os.listdir(self.xunBao):
                            curfilename = os.path.join(self.xunBao, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                chuangGuanIdle = 0
                                if filename == "XunBao_AFighting.png":
                                    print("海底寻宝战斗中...")
                                    self.sig.emit("海底寻宝战斗中...")
                                    time.sleep(5)
                                    break
                                elif filename == "XunBao_ZIco.png":
                                    print("点击海底寻宝任务:" + filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, baselinscore)
                                    print("海底寻宝任务操作中...")
                                    self.sig.emit("海底寻宝任务操作中...")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    #等待
                                    getNext= True
                                    while getNext:
                                        self.capture_img(self.window, self.curimg)
                                        xunBao1 = self.curdir + r"\image\XunBao\XunBao_XunBaoLing.png"
                                        xunBao2 = self.curdir + r"\image\XunBao\XunBao_PuTong.png"
                                        matchedScroe1, poction1 = self.search_position(self.curimg, xunBao1)
                                        matchedScroe2, poction2 = self.search_position(self.curimg, xunBao2)
                                        print(matchedScroe1,matchedScroe2)
                                        if matchedScroe1 >= self.baselinscore:
                                            win32gui.SetForegroundWindow(self.window)
                                            print(matchedScroe, self.baselinscore)
                                            print("领取任务！")
                                            xcurpoc = mainPos[0] + poction1[0] + 50
                                            ycurpoc = mainPos[1] + poction1[1] + 50
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            getNext = False
                                        elif matchedScroe2 >= self.baselinscore:
                                            win32gui.SetForegroundWindow(self.window)
                                            print(matchedScroe, self.baselinscore)
                                            print("进入战斗!")
                                            xcurpoc = mainPos[0] + poction2[0] + 50
                                            ycurpoc = mainPos[1] + poction2[1] + 50
                                            self.simulate_mouse(xcurpoc, ycurpoc)
                                            getNext = False
                                        else:
                                            time.sleep(2)
                                    break
                                else:
                                    print("海底寻宝任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, baselinscore)
                                    print("海底寻宝任务操作中...")
                                    self.sig.emit("海底寻宝任务操作中...")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("海底寻宝任务检查中:" + filename)
                                self.sig.emit("海底寻宝任务检查中:" + filename)
                        #查找任务图标
                        if chuangGuanIdle > 2:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(1)
                                #查找海底寻宝任务
                                self.capture_img(self.window, self.curimg)
                                XunBaoLocation = self.curdir + r"\image\XunBao\XunBao_ZIco.png"
                                matchedScroe, poction = self.search_position(self.curimg, XunBaoLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("查找海底寻宝任务文字：", XunBaoLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("点击海底寻宝默认任务!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                        if chuangGuanIdle > 3:
                            self.close_Windows()
                        chuangGuanIdle += 1
                    print("海底寻宝任务结束")
                    self.sig.emit("海底寻宝任务结束") 
                elif jobitem == "13":
                    self.sig.emit("迷魂塔任务开始...")
                    time.sleep(5)
                    self.close_Windows()
                    miHunTaob = self.curdir + r"\image\StartJob\StartJob_MiHunTa.png"
                    self.start_job(miHunTaob)
                    time.sleep(5)
                    miHunTaIdle = 0
                    while miHunTaIdle < 8:
                        mainPos = win32gui.GetWindowRect(self.window)
                        print("当前迷魂塔任务空闲检测次数为:" + str(miHunTaIdle))
                        self.sig.emit("当前迷魂塔任务空闲检测次数为:" + str(miHunTaIdle))
                        for filename in os.listdir(self.miHunTa):
                            curfilename = os.path.join(self.miHunTa, filename)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                miHunTaIdle = 0
                                if filename == "MiHunTa_AFighting.png":
                                    print("迷魂塔战斗中...")
                                    self.sig.emit("迷魂塔战斗中...")
                                    time.sleep(5)
                                    break
                                else:
                                    win32gui.SetForegroundWindow(self.window)
                                    print("迷魂塔任务已匹配:" + filename)
                                    print(matchedScroe, baselinscore)
                                    self.sig.emit("迷魂塔任务操作中...")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("迷魂塔任务检查中:" + filename)
                                self.sig.emit("迷魂塔任务检查中:" + filename)
                        #查找任务图标
                        if miHunTaIdle > 2:
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                            if matchedScroe >= self.baselinscore:
                                print("查找任务图标：", self.rwClick)
                                win32gui.SetForegroundWindow(self.window)
                                print(matchedScroe, self.baselinscore)
                                xcurpoc = mainPos[0] + poction[0] + 200
                                ycurpoc = mainPos[1] + poction[1] + 200
                                self.roll_mouse(xcurpoc,ycurpoc)
                                time.sleep(1)
                                #查找迷魂塔任务
                                self.capture_img(self.window, self.curimg)
                                XunBaoLocation = self.curdir + r"\image\MiHunTa\MiHunTa_ZDoing.png"
                                matchedScroe, poction = self.search_position(self.curimg, XunBaoLocation)
                                if matchedScroe >= self.baselinscore:
                                    print("查找迷魂塔任务文字：", XunBaoLocation)
                                    win32gui.SetForegroundWindow(self.window)
                                    print(matchedScroe, self.baselinscore)
                                    print("点击迷魂塔默认任务!")
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    time.sleep(1)
                        if miHunTaIdle > 3:
                            self.close_Windows()
                        miHunTaIdle += 1
                    print("迷魂塔任务结束")
                    self.sig.emit("迷魂塔任务结束") 
                elif jobitem == "14":
                    self.sig.emit("初级贸易任务即将开始...")
                    time.sleep(5)
                    self.close_Windows()
                    #查找初级贸易进入到贸易任务
                    mainPos = win32gui.GetWindowRect(self.window)
                    self.capture_img(self.window, self.curimg)
                    matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                    if matchedScroe >= self.baselinscore:
                        print("查找任务图标：", self.rwClick)
                        win32gui.SetForegroundWindow(self.window)
                        print(matchedScroe, self.baselinscore)
                        xcurpoc = mainPos[0] + poction[0] + 200
                        ycurpoc = mainPos[1] + poction[1] + 200
                        self.roll_mouse(xcurpoc,ycurpoc)
                        time.sleep(1)
                        #查找初级贸易任务
                        self.capture_img(self.window, self.curimg)
                        matchedScroe, poction = self.search_position(self.curimg, self.cjMaoYiLocation)
                        if matchedScroe >= self.baselinscore:
                            print("查找初级贸易文字：", self.cjMaoYiLocation)
                            win32gui.SetForegroundWindow(self.window)
                            print(matchedScroe, self.baselinscore)
                            print("点击初级贸易任务处理!")
                            xcurpoc = mainPos[0] + poction[0] + 50
                            ycurpoc = mainPos[1] + poction[1] + 50
                            self.simulate_mouse(xcurpoc, ycurpoc)
                            time.sleep(10)
                    #进入初级贸易任务处理
                    cjMaoyiIdel = 0
                    while cjMaoyiIdel < 8:
                        for filename in os.listdir(self.cjMaoyi):
                            curfilename = os.path.join(self.cjMaoyi, filename)
                            mainPos = win32gui.GetWindowRect(self.window)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                cjMaoyiIdel = 0                        
                                print(matchedScroe, self.baselinscore)
                                if filename == "CJMaoyi_Fighting.png":
                                    print("初级贸易战斗中...")
                                    self.sig.emit("初级贸易战斗中...")
                                    time.sleep(15)                                  
                                    break
                                elif filename == "CJMaoYi_ShangChengGouMai.png":
                                    print("初级贸易商城购买...")
                                    self.sig.emit("初级贸易商城购买...")
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)                               
                                    break                                        
                                elif filename == "CJMaoYi_ZDoing.png" or filename == "CJMaoYi_Z_Doing.png":
                                    print("初级贸易任务中...")
                                    self.sig.emit("初级贸易任务中...")
                                    time.sleep(3)
                                    break                                
                                else:
                                    print("初级贸易任务已匹配:" + filename)
                                    self.sig.emit("初级贸易任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("初级贸易任务检查中:" + filename)
                                print(matchedScroe, self.baselinscore)
                                self.sig.emit("初级贸易任务检查中:" + filename)                        
                        if cjMaoyiIdel > 3:
                            self.close_Windows()
                        cjMaoyiIdel += 1
                    print("初级贸易任务结束")
                    self.sig.emit("初级贸易任务结束")                    
                elif jobitem == "15":
                    self.sig.emit("高级贸易任务即将开始...")
                    time.sleep(5)
                    self.close_Windows()
                    #查找高级贸易进入到贸易任务
                    mainPos = win32gui.GetWindowRect(self.window)
                    self.capture_img(self.window, self.curimg)
                    matchedScroe, poction = self.search_position(self.curimg, self.rwClick)
                    if matchedScroe >= self.baselinscore:
                        print("查找任务图标：", self.rwClick)
                        win32gui.SetForegroundWindow(self.window)
                        print(matchedScroe, self.baselinscore)
                        xcurpoc = mainPos[0] + poction[0] + 200
                        ycurpoc = mainPos[1] + poction[1] + 200
                        self.roll_mouse(xcurpoc,ycurpoc)
                        time.sleep(1)
                        #查找高级贸易任务
                        self.capture_img(self.window, self.curimg)
                        matchedScroe, poction = self.search_position(self.curimg, self.gjMaoYiLocation)
                        print(matchedScroe)
                        if matchedScroe >= self.baselinscore:
                            print("查找高级贸易文字：", self.gjMaoYiLocation)
                            win32gui.SetForegroundWindow(self.window)
                            print(matchedScroe, self.baselinscore)
                            print("点击高级贸易任务处理!")
                            xcurpoc = mainPos[0] + poction[0] + 50
                            ycurpoc = mainPos[1] + poction[1] + 50
                            self.simulate_mouse(xcurpoc, ycurpoc)
                            time.sleep(1)
                    #进入高级贸易任务处理
                    cjMaoyiIdel = 0
                    while cjMaoyiIdel < 8:
                        for filename in os.listdir(self.gjMaoyi):
                            curfilename = os.path.join(self.gjMaoyi, filename)
                            mainPos = win32gui.GetWindowRect(self.window)
                            self.capture_img(self.window, self.curimg)
                            matchedScroe, poction = self.search_position(self.curimg, curfilename)
                            if matchedScroe >= self.baselinscore:
                                cjMaoyiIdel = 0                        
                                print(matchedScroe, self.baselinscore)
                                if filename == "GJMaoyi_AFighting.png":
                                    print("高级贸易战斗中...")
                                    self.sig.emit("高级贸易战斗中...")
                                    time.sleep(15)                                  
                                    break
                                elif filename == "GJMaoYi_ShangChengGouMai.png":
                                    print("高级贸易商城购买...")
                                    self.sig.emit("高级贸易商城购买...")
                                    xuQiu = self.curdir + r"\image\GJMaoYi\GJMaoYi_ShangChengGouMai_xuqiu.png"                                    
                                    win32gui.SetForegroundWindow(window)
                                    self.click_Image(xuQiu)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)                               
                                    break                                        
                                elif filename == "GJMaoYi_ZDoing.png" or filename == "GJMaoYi_Z_Doing.png":
                                    print("高级贸易任务中...")
                                    self.sig.emit("高级贸易任务中...")
                                    time.sleep(3)
                                    break
                                elif filename == "GJMaoYi_End.png":
                                    print("高级贸易任务已全部完成")
                                    self.sig.emit("高级贸易任务已全部完成")
                                    self.close_Windows()
                                    cjMaoyiIdel = 10
                                    time.sleep(3)
                                    break
                                else:
                                    print("高级贸易任务已匹配:" + filename)
                                    self.sig.emit("高级贸易任务已匹配:" + filename)
                                    win32gui.SetForegroundWindow(window)
                                    xcurpoc = mainPos[0] + poction[0] + 50
                                    ycurpoc = mainPos[1] + poction[1] + 50
                                    self.simulate_mouse(xcurpoc, ycurpoc)
                                    break
                            else:
                                print("高级贸易任务检查中:" + filename)
                                print(matchedScroe, self.baselinscore)
                                self.sig.emit("高级贸易任务检查中:" + filename)                        
                        if cjMaoyiIdel > 3:
                            self.close_Windows()
                        cjMaoyiIdel += 1
                    print("高级贸易任务结束")
                    self.sig.emit("高级贸易任务结束") 
            print("当前账号任务执行结束。")
            self.sig.emit("当前账号任务执行结束。")
            #若双开最小化当前任务窗口,并执行下一个窗口任务，否则不再执行下一个任务。
            if self.enableDoubleStart:
                win32gui.ShowWindow(self.window, win32con.SW_MINIMIZE)
            else:
                processRunning = False
        print("所有账号任务执行结束。")
        self.sig.emit("所有账号任务执行结束。")

if __name__ == "__main__":

    baselinscore = 0.8
    title = '《梦幻西游》手游'
    curdir = os.path.split(os.path.realpath(__file__))[0]
    curimg = curdir + r'\image\temp\curimg.jpg'   

    application = QApplication(sys.argv)
    myWin = MyMainForm(title)
    myWin.show()
    sys.exit(application.exec_())
