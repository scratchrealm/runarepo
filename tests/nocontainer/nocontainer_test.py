import json
import runarepo
import kachery_client as kc

def main():
    with kc.TemporaryDirectory() as tmpdir:
        params = {
            'sleep_sec': 4
        }
        params_fname = tmpdir + '/params.json'
        with open(params_fname, 'w') as f:
            json.dump(params, f)
        inputs = [
            runarepo.Input(name='INPUT_PARAMS', path=params_fname)
        ]
        output = runarepo.run('./repo', inputs=inputs)
        print('========================================')
        print(output.retcode)
        print(output.console_lines)

if __name__ == '__main__':
    main()