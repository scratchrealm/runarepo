import runarepo

def main():
    output = runarepo.run('./repo', use_docker=True)
    print('========================================')
    print(output.console_lines)

if __name__ == '__main__':
    main()