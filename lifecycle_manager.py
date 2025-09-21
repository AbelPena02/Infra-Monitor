import time
from app import app
from db import db, Server
from servers import _ensure_sim_for_dbserver

def main():
    with app.app_context():
        try:
            while True:
                print("Updating simulated server states...")
                servers = Server.query.all()
                for server in servers:
                    sim = _ensure_sim_for_dbserver(server)
                    sim.update()
                db.session.commit()
                print("Server states updated. Waiting 10 seconds...")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nLifecycle manager stopped by user.")

if __name__ == "__main__":
    main()
