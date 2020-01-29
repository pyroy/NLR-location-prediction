from tkinter import Tk, RIGHT, BOTH, RAISED, LEFT, NORMAL
from tkinter.ttk import Frame, Button, Style, Label

class Example(Frame):

    def __init__(self):
        super().__init__()
        self.initUI()

    def changetext1(self):
        self.label1.config(text = "bruh 1")

    def changetext2(self):
        self.label1.config(text = "kaas anders met een pet op")

    def changetext3(self):
        self.label1.config(text = "ypur mom gay")
	
    def changetext4(self):    
        self.label1.config(text = "waarschijnlijk op het malieveld en anders op de snelweg")

    def initUI(self):

        #Actual code

        self.master.title("bruh moment")
        self.pack(fill=BOTH, expand=True)

        frame = Frame(self)
        frame.pack()

        button1 = Button(frame, text="knopje 1", command=self.changetext1)
        button1.pack(side=LEFT, padx=10)

        button2 = Button(frame, text="knopje 2", command=self.changetext2)
        button2.pack(side=LEFT, padx=10)

        button3 = Button(frame, text="knopje 3000", command=self.changetext3)
        button3.pack(side=LEFT, padx=10)

        button4 = Button(frame, text="Tractor",command=self.changetext4)
        button4.pack(side=LEFT, padx=10)

        #een frame is een nieuw deel dus in dit geval een new line

        frame2 = Frame(self)
        frame2.pack()

        #hier staat een self. voor de widget zodat we m opslaan in de class
        #om m te accessen in de changetext functies

        self.label1 = Label(frame2, text="test", state=NORMAL)
        self.label1.pack(side=LEFT, padx=10)

        #einde actual code


#geometry geeft window size aan
def main():
    root = Tk()
    root.geometry("500x500")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()
