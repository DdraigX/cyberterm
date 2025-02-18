import subprocess
import os

def get_terminal_size(): 
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)

def draw_box(rows, columns):
    #for i in range(columns):
    print(f"{'-' * columns}")
    print(f"{'|' * rows}")
    


def main():
    rows, columns = get_terminal_size()
    draw_box(rows, columns)
    print(str(rows) + " " + str(columns))



if __name__ == "__main__":
    main()
