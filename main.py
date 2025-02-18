import subprocess
import os
import textwrap


def clear_screen()
    

def get_terminal_size(): 
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)

def draw_box(rows, columns):
    #for i in range(columns):
    #print(f"{'\u2500' * columns}")
    print(f"\033[{2};0H{'¦'}{' ' * (columns - 2)}{'¦'}")
    print(f"{"─" * columns}")
    "─"
    print(f"{'|'}")
    print("\033[1;31mThis text is red and bold!\033[0m")


def main():
    rows, columns = get_terminal_size()
    draw_box(rows, columns)
    print(str(rows) + " " + str(columns))



if __name__ == "__main__":
    main()
