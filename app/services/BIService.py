from app.repositories.BIRepository import BIRepository
class BIService:

    def __init__(self, db: Session):
        self.repository = BIRepository