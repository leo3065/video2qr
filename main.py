import tkinter as tk
import tkinter.ttk as ttk
import re

from typing import Optional


def parse_timestamp(string: str) -> Optional[float]:
    value = None
    string = string.strip()
    if re.fullmatch(r'\d+|\d+\.\d+|\.\d+', string):
        value = float(string)
        return round(value, 3)
    elif match := re.fullmatch(r'(\d+:)?(\d+)(\.\d+)?', string):
        minutes, seconds, milis = match.groups('')
        minutes = int(minutes[:-1]) if minutes else 0
        seconds = float(seconds + milis)
        return round(minutes*60 + seconds, 3)
    
    return None

class TextFrame(ttk.Labelframe):
    def __init__(self, *args, **kwargs):
        super(TextFrame, self).__init__(*args, **kwargs)
        self.setup_interfaces()

    def setup_interfaces(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        
        ## row 0 and row 1
        text_grid = self.text_grid = ttk.Treeview(
            self, columns=('time', 'text'), displaycolumns=('time', 'text'),
            selectmode='browse')
        text_grid.grid(row=0, column=0, columnspan=4, pady=2)
        
        text_grid.column('#0', width=10, stretch=0)
        text_grid.column('time', width=60, stretch=0, anchor=tk.E)
        text_grid.column('text', width=480, stretch=1, anchor=tk.W)
        text_grid.heading('time', text='Time', anchor=tk.CENTER)
        text_grid.heading('text', text='Text', anchor=tk.W)
        text_grid.bind('<<TreeviewSelect>>', lambda _: self.update_entry())
        
        scroll_vert = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=text_grid.yview)
        scroll_hori = ttk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=text_grid.xview)
        scroll_vert.grid(row=0, column=4, sticky=tk.NS)
        scroll_hori.grid(row=1, column=0, columnspan=4, sticky=tk.EW)
        text_grid['yscrollcommand'] = scroll_vert.set
        text_grid['xscrollcommand'] = scroll_hori.set
        
        ## row 2
        add_button = self.add_button = ttk.Button(
            self, text='+', width=2, command=self.add_row)
        add_button.grid(row=2, column=0, padx=2, pady=2)
        
        remove_button = self.remove_button = ttk.Button(
            self, text='-', width=2, command=self.del_row)
        remove_button.grid(row=2, column=1, padx=2, pady=2)
        
        ## row 3
        ttk.Label(self, text='Time: ').grid(
            row=3, column=0, columnspan=2, padx=2, pady=2)
        
        time_var = self.time_var = tk.StringVar()
        time_entry = self.time_entry = ttk.Entry(
            self, width=10, justify=tk.RIGHT, state=tk.DISABLED,
            textvariable=time_var)
        time_entry.grid(row=3, column=2, padx=2, pady=2, sticky=tk.W)
        time_entry.bind('<Return>', self.entry_entered)
        
        ## row 4
        ttk.Label(self, text='Text: ').grid(
            row=4, column=0, columnspan=2, padx=2, pady=2)
        
        text_var = self.text_var = tk.StringVar()
        text_entry = self.text_entry = ttk.Entry(
            self, width=60, justify=tk.LEFT, state=tk.DISABLED,
            textvariable=text_var)
        text_entry.grid(row=4, column=2, padx=2, pady=2, sticky=tk.EW)
        text_entry.bind('<Return>', self.entry_entered)
    
    def add_row(self):
        index = 0
        value = ['0.000', '']
        
        selected = self.text_grid.selection()
        if selected:
            selected = selected[0]
            index = self.text_grid.index(selected) + 1
            value[0] = self.text_grid.set(selected, 'time')
        
        item_id = self.text_grid.insert('', index, value=value)
        self.text_grid.selection_set(item_id)
    
    def del_row(self):
        selected = self.text_grid.selection()
        if not selected:
            return
        
        selected = selected[0]
        select_to_be = None
        if item := self.text_grid.prev(selected):
            select_to_be = item
        elif item := self.text_grid.next(selected):
            select_to_be = item
        
        self.text_grid.delete(selected)
        
        if select_to_be:
            self.text_grid.selection_set(select_to_be)
    
    def update_entry(self):
        selected = self.text_grid.selection()
        if not selected:
            selected = None
        else:
            selected = selected[0]
        
        if not selected:
            self.time_var.set('')
            self.time_entry['state'] = tk.DISABLED
            self.text_var.set('')
            self.text_entry['state'] = tk.DISABLED
        else:
            self.time_var.set(self.text_grid.set(selected, 'time'))
            self.time_entry['state'] = tk.ACTIVE
            self.text_var.set(self.text_grid.set(selected, 'text'))
            self.text_entry['state'] = tk.ACTIVE
    
    def entry_entered(self, event=None):
        validated = False
        if event.widget is self.time_entry:
            val = parse_timestamp(self.time_var.get())
            if val is not None:
                validated = True
        else:
            validated = True
        
        if validated:
            self.update_row()
    
    def update_row(self):
        selected = self.text_grid.selection()
        if not selected:
            return
        
        selected = selected[0]
        time = parse_timestamp(self.time_var.get())
        self.time_var.set(f'{time:.3f}')
        self.text_grid.set(selected, 'time', f'{time:.3f}')
        self.text_grid.set(selected, 'text', self.text_var.get())
        self.sort_rows()
    
    def sort_rows(self):
        items = list(self.text_grid.get_children())
        
        item_val = []
        for item in items:
            time = float(self.text_grid.set(item, 'time'))
            index = self.text_grid.index(item)
            item_val.append((time, index, item))
        
        item_val.sort()
        for index, (_, _, item) in enumerate(item_val):
            self.text_grid.move(item, '', index)


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.resizable(False, False)
        self.setup_interfaces()

    def setup_interfaces(self):
        # text frame
        text_frame = self.text_frame = TextFrame(self, text='Texts')
        text_frame.grid(row=0, column=1, padx=5, pady=5)


if __name__ == '__main__':
    app = App()
    app.mainloop()
