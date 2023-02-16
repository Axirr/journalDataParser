from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DATE, INT, Date

class Base(DeclarativeBase):
    pass

class Daily_Data(Base):
    __tablename__ = "daily_data"

    # date: Mapped[Date] = mapped_column(DATE)
    date: Mapped[Date] = mapped_column(DATE, primary_key=True)

    programmingMinutes: Mapped[int] = mapped_column(INT)
    TVminutes: Mapped[int] = mapped_column(INT)
    recreationMinutes: Mapped[int] = mapped_column(INT)
    gameMinutes: Mapped[int] = mapped_column(INT)
    productiveMinutes: Mapped[int] = mapped_column(INT)
    walkingMinutes: Mapped[int] = mapped_column(INT)

    insomniaRating: Mapped[int] = mapped_column(INT)

    def __repr__(self):
        return f"date={self.date}  progMin={self.programmingMinutes}  tvMin={self.TVminutes}  recMin={self.recreationMinutes}  gameMin={self.gameMinutes}  prodMin={self.productiveMinutes}  walkMin={self.walkingMinutes}  insomniaRating={self.insomniaRating}" 