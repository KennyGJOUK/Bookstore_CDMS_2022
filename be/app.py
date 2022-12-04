
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from be import serve


if __name__ == "__main__":
    serve.be_run()
