import runarepo

def main():
    output = runarepo.run('./repo', use_singularity=True, image='docker://python:3.8')
    print('========================================')
    print(output.console_lines)

if __name__ == '__main__':
    main()