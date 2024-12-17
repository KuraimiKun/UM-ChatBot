import time
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from chatbot import chat
from PIL import Image, ImageTk
import emoji
from datetime import datetime

DIMS = "800x600"

class RoundedButton(Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, bg, command=None):
        Canvas.__init__(self, parent, borderwidth=0, relief="flat", highlightthickness=0)
        self.command = command
        self.configure(width=width, height=height, bg=bg)
        self.normal_color = color
        self.hover_color = self.adjust_color_brightness(color, 1.2)
        
        # Create rounded rectangle button
        self.rect = self.create_rounded_rect(padding, padding, width-padding, height-padding, 
                                           cornerradius, fill=color, outline=color)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def adjust_color_brightness(self, color, factor):
        # Convert hex to RGB, adjust brightness, convert back to hex
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        new_rgb = tuple(min(255, int(c * factor)) for c in rgb)
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'

    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.normal_color)

    def on_click(self, e):
        if self.command is not None:
            self.command()

class ChatInterface(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        
        # Enhanced color scheme
        self.primary_color = "#1a1a2e"  # Darker blue
        self.secondary_color = "#ffffff"  # Pure white
        self.accent_color = "#0066ff"    # Bright blue
        self.message_bg_user = "#e3f2fd"  # Light blue
        self.message_bg_bot = "#f5f5f5"   # Light grey
        self.font = "Helvetica 10"
        
        # Configure master window
        self.master.configure(bg=self.primary_color)
        
        # Enhanced header
        self.header_frame = Frame(self.master, bg=self.primary_color, height=70)
        self.header_frame.pack(fill=X)
        self.header_frame.pack_propagate(False)  # Force height
        
        # Add gradient effect to header
        self.header_canvas = Canvas(self.header_frame, bg=self.primary_color, 
                                  height=70, bd=0, highlightthickness=0)
        self.header_canvas.pack(fill=X)
        
        # Load and resize bot icon
        icon_size = 40
        original_icon = Image.open('img/bot.png')
        resized_icon = original_icon.resize((icon_size, icon_size))
        self.bot_icon = ImageTk.PhotoImage(resized_icon)
        
        # Add bot icon to header
        self.icon_label = Label(self.header_frame, image=self.bot_icon, bg=self.primary_color)
        self.icon_label.pack(side=LEFT, padx=20)
        
        # Enhanced title
        self.title_label = Label(self.header_frame, text="AI Assistant", 
                               font="Helvetica 18 bold", 
                               bg=self.primary_color, 
                               fg=self.secondary_color)
        self.title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Simplified menu
        menu = Menu(self.master)
        self.master.config(menu=menu, bd=0)
        
        # File menu
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Clear Chat", command=self.clear_chat)
        file.add_command(label="Exit", command=self.chatexit)
        
        # About menu
        help_option = Menu(menu, tearoff=0)
        menu.add_cascade(label="About", menu=help_option)
        help_option.add_command(label="About Chatbot", command=self.msg)
        
        # Enhanced chat area
        self.text_frame = Frame(self.master, bd=0, bg=self.secondary_color)
        self.text_frame.pack(expand=True, fill=BOTH, padx=20, pady=10)

        # Custom scrollbar style
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0, width=12)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT, pady=5)

        # Enhanced text box with custom tag configuration
        self.text_box = Text(self.text_frame, 
            yscrollcommand=self.text_box_scrollbar.set,
            state=DISABLED,
            bd=0,
            padx=20,
            pady=20,
            spacing3=15,
            wrap=WORD,
            bg=self.secondary_color,
            font=self.font,
            relief=FLAT,
            width=10,
            height=1)
            
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # Enhanced input area with rounded corners
        self.input_frame = Frame(self.master, bg=self.primary_color, pady=15)
        self.input_frame.pack(fill=X, padx=20, pady=(0, 20))

        # Rounded input field
        self.entry_field = Entry(self.input_frame,
            font="Helvetica 11",
            bd=0,
            bg=self.secondary_color,
            fg=self.primary_color,
            relief=FLAT)
        self.entry_field.pack(fill=X, side=LEFT, expand=True, ipady=10, padx=(0, 10))

        # Modern send button with hover effect
        self.send_button = Button(self.input_frame,
            text="Send",
            font="Helvetica 11 bold",
            width=10,
            relief=FLAT,
            bg=self.accent_color,
            fg=self.secondary_color,
            command=lambda: self.send_message_insert(None),
            activebackground=self.accent_color,
            activeforeground=self.secondary_color,
            cursor="hand2")
        self.send_button.pack(side=RIGHT, ipady=8)
        
        # Bind return key
        self.master.bind("<Return>", self.send_message_insert)
        
        # Status label
        self.sent_label = Label(self.input_frame, 
            font="Helvetica 7", 
            text="No messages sent.", 
            bg=self.primary_color, 
            fg=self.secondary_color)
        self.sent_label.pack(side=LEFT, padx=5)

        # Configure message tags with enhanced styling
        self.text_box.tag_configure("user_label", foreground="#1976D2", 
                                  font="Helvetica 10 bold", spacing1=10)
        self.text_box.tag_configure("bot_label", foreground="#43A047", 
                                  font="Helvetica 10 bold", spacing1=10)
        self.text_box.tag_configure("timestamp", foreground="#9e9e9e", 
                                  font="Helvetica 8", spacing1=5)
        self.text_box.tag_configure("user_message", 
                                  background=self.message_bg_user,
                                  lmargin1=40, lmargin2=40, rmargin=20,
                                  spacing1=5, spacing2=5,
                                  relief=SOLID, borderwidth=0)
        self.text_box.tag_configure("bot_message",
                                  background=self.message_bg_bot,
                                  lmargin1=40, lmargin2=40, rmargin=20,
                                  spacing1=5, spacing2=5,
                                  relief=SOLID, borderwidth=0)

    def send_message_insert(self, message):
        user_input = self.entry_field.get()
        if not user_input:
            return
            
        self.entry_field.delete(0, END)
        current_time = datetime.now().strftime("%I:%M %p")
            
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, "\n")
        
        # User message with timestamp
        self.text_box.insert(END, f"You • {current_time}\n", "user_label")
        self.text_box.insert(END, f"{user_input}\n", "user_message")
        
        # Bot response with timestamp
        response = chat(user_input)
        self.text_box.insert(END, f"\nBot • {current_time}\n", "bot_label")
        self.text_box.insert(END, f"{response}\n", "bot_message")
        
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        
        self.last_sent_label(str(time.strftime("Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))

    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.last_sent_label(date="No messages sent.")
        self.text_box.delete(1.0, END)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    def chatexit(self):
        exit()

    def msg(self):
        tkinter.messagebox.showinfo("NLP - Neural Network based chatbot")

    def last_sent_label(self, date):

        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.input_frame,  # Changed from entry_frame to input_frame
            font="Helvetica 7", 
            text=date, 
            bg=self.primary_color, 
            fg=self.secondary_color)
        self.sent_label.pack(side=LEFT, padx=5)

root=Tk()
ob = ChatInterface(root)
root.geometry(DIMS)
root.title("UM-Bot_Assistant")

img = PhotoImage(file = 'img/bot.png') 
root.iconphoto(False, img)

root.mainloop()

