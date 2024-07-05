from prompt_toolkit import prompt, Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.formatted_text import FormattedText
from colorama import init as colorama_init, Fore, Style
from tabulate import tabulate
from procmanager.tui_helpers import generate_log_table

colorama_init()
kb = KeyBindings()

@kb.add('c-c')
@kb.add('c-q')
@kb.add('q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

#buffer1= Buffer()

#static_text = FormattedTextControl(text='Hello world')
static_text = FormattedTextControl(text=FormattedText([('fg:green','Hello world')]))
container = VSplit([
  # One window that holds the BufferControl with the default buffer on
    # the left.
#    Window(content=BufferControl(buffer=buffer1)),

    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
#    Window(width=1, char='|'),

    # Display the text 'Hello world' on the right.
    Window(content=static_text),
])
def refresh(app):
    offset = 0
    #rows, properties = generate_log_table(top_down=True, ptk=True, limit=300, offset=offset)
    rows, properties = generate_log_table(top_down=True, ptk=False, limit=300, offset=offset)
    #print(tabulate(rows))
    #import time
    #time.sleep(3)
    #rows = [("",row) for row in tabulate(rows)]
    #print(tabulate(rows))
    #import time
    #time.sleep(3)
    #quit()
    #static_text.text = tabulate(rows)
    #static_text.text = FormattedText(tabulate(rows))
    from prompt_toolkit import print_formatted_text, ANSI
    #print_formatted_text(FormattedText(rows))
    #rows, properties = generate_log_table(top_down=True )
    #print_formatted_text(ANSI(tabulate(rows)))
    #quit()
    #static_text.text = FormattedText(rows)
    static_text.text = ANSI(tabulate(rows))
    #print(dir(container))
    from prompt_toolkit.layout.dimension import D
    return
    from datetime import datetime
    dates = []
    dss = []
    for i in range(60):
        date_str = str(datetime.now()) * 3 
        dss.append(("fg:green", date_str))
        dss.append(("fg:red", date_str))
        dss.append(("", '\n'))
        dates.append(date_str)
        dates.append(f'{Fore.GREEN}')
        dates.append(f'fg:green')
        dates.append(date_str)
        dates.append(f'{Style.RESET_ALL}')
        dates.append('\n')
    #static_text.text = '\n'.join(dates)
    static_text.text = FormattedText(dss)
#text = prompt('Give me some input: ')
#print('You said: %s' % text)

def run_app():
    layout = Layout(container)
    app = Application(layout=layout, full_screen=True, key_bindings=kb, refresh_interval=1.5, on_invalidate=refresh)
    refresh(app)
    #app.create_background_task(refresh)
    app.run()

if __name__ == '__main__':
    run_app()
