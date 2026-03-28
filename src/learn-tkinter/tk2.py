import tkinter as tk

win=tk.Tk() #生成一个主窗口对象
win.title("带退出按钮的窗口")
win.geometry('500x260') #窗口大小

#退出按钮事件处理函数
def my_quit():
    win.quit()
    win.destroy()

#退出按钮对象添加
but_quit=tk.Button(win,text="退出",command=my_quit,width=20,height=4)
but_quit.pack()

win.mainloop() #进入消息循环