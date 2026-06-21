import sys
from core.orchestrator import Orchestrator

def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║        ControlProbe v1.0              ║
    ║  Adaptive Security Control Validator  ║
    ╚═══════════════════════════════════════╝
    """)

    orchestrator = Orchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
