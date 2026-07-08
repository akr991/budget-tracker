import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import RegionEnum
from app.models.finance import Debt, ExpenseEntry, GoldHolding, IncomeEntry, Investment, Loan
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
def export_csv(
    region: RegionEnum,
    module: str = Query(pattern="^(incomes|expenses|loans|debts|investments|gold)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    model_map = {
        "incomes": IncomeEntry,
        "expenses": ExpenseEntry,
        "loans": Loan,
        "debts": Debt,
        "investments": Investment,
        "gold": GoldHolding,
    }

    model = model_map.get(module)
    if not model:
        raise HTTPException(status_code=400, detail="Invalid module")

    rows = db.query(model).filter(model.user_id == user.id, model.region == region).all()

    output = io.StringIO()
    writer = csv.writer(output)

    if rows:
        columns = [column.name for column in model.__table__.columns]
        writer.writerow(columns)
        for row in rows:
            writer.writerow([getattr(row, col) for col in columns])
    else:
        writer.writerow(["message"])
        writer.writerow(["No data found"])

    output.seek(0)
    filename = f"{region.value}_{module}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
