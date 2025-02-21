import subprocess
import os
import textwrap

# box_chars = [
#     '\u2500',  # ─
#     '\u2502',  # │
#     '\u250C',  # ┌
#     '\u2510',  # ┐
#     '\u2514',  # └
#     '\u2518',  # ┘
#     '\u251C',  # ├
#     '\u2524',  # ┤
#     '\u252C',  # ┬
#     '\u2534',  # ┴
#     '\u253C',  # ┼
#     '\u2588',  # █
# ]

# for char in box_chars:
#     print(char, end=' ')
# print()

def clear_term():
    os.system('clear')
    

def get_terminal_size(): 
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)

def draw_box(rows, columns):
    #for i in range(columns):
    #print(f"{'\u2500' * columns}")
    print(f"\033[{2};0H{'¦'}{' ' * (columns - 2)}{'¦'}")
    print(f"{'┌' + '─' * (columns - 2) + '┐'}")
  
    print(f"{'|'}")
    print("\033[1;31mThis text is red and bold!\033[0m")


def main():
    clear_term()
    rows, columns = get_terminal_size()
    draw_box(rows, columns)
    print(str(rows) + " " + str(columns))



if __name__ == "__main__":
    main()
    