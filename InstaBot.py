import tkinter
from module import tkinter_data


class MyButton(tkinter.Button):
    def __init__(self, master, row, *args, **kwargs):
        super(MyButton, self).__init__(master, *args, **kwargs)
        self.button_row = row


class InstaBot:
    win = tkinter.Tk()
    win.title('NameWin')
    win.geometry('500x300')
    mode = [tkinter.IntVar() for i in range(len(list(tkinter_data.account_dict)))]
    btn = [tkinter.Button() for j in range(len(list(tkinter_data.account_dict)))]

    @staticmethod
    def create_label(name):
        return tkinter.Label(InstaBot.win,
                             text=tkinter_data.account_dict[str(name)]['name'],
                             bg='gray',
                             anchor='w',
                             width=17)

    @staticmethod
    def create_radiobutton(i, j):
        return tkinter.Radiobutton(InstaBot.win,
                                   text=tkinter_data.button_dict[f'radio{j}']['text'],
                                   variable=InstaBot.mode[i],
                                   value=i + j)

    @staticmethod
    def create_button_start(row):
        return MyButton(InstaBot.win, row, text='Старт')

    def create_menu(self):
        for name in tkinter_data.account_dict:
            self.create_label(name).grid()
        for i in range(len(list(tkinter_data.account_dict))):
            self.create_button_start(i).grid(row=i, column=3)
            for j in range(2):
                self.create_radiobutton(i, j).grid(row=i, column=j + 1)

    def start(self):
        self.create_menu()
        InstaBot.win.mainloop()


bot = InstaBot()
bot.start()
