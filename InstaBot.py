import tkinter
from module import tkinter_data


class MyButton(tkinter.Button):
    def __init__(self, master, row, *args, **kwargs):
        super(MyButton, self).__init__(master, *args, **kwargs)
        self.row = row
        self.account_name = tkinter_data.account_dict[str(row)]['login']


class MyRadio(tkinter.Radiobutton):
    def __init__(self, master, row: int, column: int, *args, **kwargs):
        super(MyRadio, self).__init__(master, *args, **kwargs)
        self.mode = None
        self.row = row
        self.column = column


class InstaBot:
    win = tkinter.Tk()
    win.title('NameWin')
    win.geometry('500x300')
    mode = [tkinter.IntVar() for i in range(len(list(tkinter_data.account_dict)))]

    def __init__(self):
        self.button = []
        for i in range(len(list(tkinter_data.account_dict))):
            btn = MyButton(InstaBot.win, i, text='Старт')
            # btn.config(command=lambda button=btn: self.press_button(button))
            self.button.append(btn)

        self.radiobutton = []
        for i in range(len(list(tkinter_data.account_dict))):
            radiobutton = tkinter.IntVar()
            temp = []
            for j in range(2):
                radio = MyRadio(InstaBot.win, row=i, column=j,
                                text=tkinter_data.button_dict[f'radio{j}']['text'],
                                variable=radiobutton,
                                value=i + j)
                radio.config(command=lambda rd=radio: self.select_mode(rd))
                temp.append(radio)
            self.radiobutton.append(temp)


    @staticmethod
    def select_mode(radio: MyRadio):
        if radio.column:
            radio.mode = 'uns'
        else:
            radio.mode = 'sub'
        print(radio.mode)

    @staticmethod
    def create_label(name):
        return tkinter.Label(InstaBot.win,
                             text=tkinter_data.account_dict[str(name)]['login'],
                             bg='gray',
                             anchor='w',
                             width=17)

    def create_menu(self):
        for name in tkinter_data.account_dict:
            self.create_label(name).grid()
        for i in range(len(list(tkinter_data.account_dict))):
            btn = self.button[i]
            btn.grid(row=i, column=3)
            for j in range(2):
                radio = self.radiobutton[i][j]
                radio.grid(row=i, column=j + 1)

    def start(self):
        self.create_menu()
        InstaBot.win.mainloop()


bot = InstaBot()
bot.start()
