from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.finance import BudgetCategory, Transaction, Budget, TransactionType
from app.schemas.finance import (
    BudgetCategoryCreate, BudgetCategoryOut,
    TransactionCreate, TransactionUpdate, TransactionOut,
    BudgetCreate, BudgetOut,
)
from app.schemas.common import PageResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/finance", tags=["财务管理"])


@router.get("/categories", response_model=list[BudgetCategoryOut])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetCategory)
        .where(BudgetCategory.user_id == current_user.id)
        .order_by(BudgetCategory.sort_order)
    )
    return [BudgetCategoryOut.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=BudgetCategoryOut)
async def create_category(
    data: BudgetCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = BudgetCategory(user_id=current_user.id, **data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return BudgetCategoryOut.model_validate(cat)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetCategory).where(
            BudgetCategory.id == category_id, BudgetCategory.user_id == current_user.id
        )
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    await db.delete(cat)
    return {"message": "删除成功"}


@router.get("/transactions", response_model=PageResult[TransactionOut])
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    count_query = select(func.count(Transaction.id)).where(Transaction.user_id == current_user.id)

    if type:
        query = query.where(Transaction.type == type)
        count_query = count_query.where(Transaction.type == type)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
        count_query = count_query.where(Transaction.category_id == category_id)
    if start_date:
        query = query.where(Transaction.occur_date >= start_date)
        count_query = count_query.where(Transaction.occur_date >= start_date)
    if end_date:
        query = query.where(Transaction.occur_date <= end_date)
        count_query = count_query.where(Transaction.occur_date <= end_date)
    if keyword:
        query = query.where(Transaction.description.contains(keyword))
        count_query = count_query.where(Transaction.description.contains(keyword))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    result = await db.execute(
        query.order_by(Transaction.occur_date.desc(), Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = [TransactionOut.model_validate(t) for t in result.scalars().all()]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/transactions", response_model=TransactionOut)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txn = Transaction(user_id=current_user.id, **data.model_dump())
    db.add(txn)
    await db.flush()
    await db.refresh(txn)
    return TransactionOut.model_validate(txn)


@router.put("/transactions/{txn_id}", response_model=TransactionOut)
async def update_transaction(
    txn_id: int,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="记录不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    await db.flush()
    await db.refresh(txn)
    return TransactionOut.model_validate(txn)


@router.delete("/transactions/{txn_id}")
async def delete_transaction(
    txn_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(txn)
    return {"message": "删除成功"}


@router.get("/summary")
async def finance_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = [Transaction.user_id == current_user.id]
    if start_date:
        filters.append(Transaction.occur_date >= start_date)
    if end_date:
        filters.append(Transaction.occur_date <= end_date)

    income_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(and_(*filters, Transaction.type == TransactionType.INCOME))
    )
    expense_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(and_(*filters, Transaction.type == TransactionType.EXPENSE))
    )

    return {
        "income": float(income_result.scalar()),
        "expense": float(expense_result.scalar()),
        "balance": float(income_result.scalar()) - float(expense_result.scalar()),
    }


@router.post("/budgets", response_model=BudgetOut)
async def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    budget = Budget(user_id=current_user.id, **data.model_dump())
    db.add(budget)
    await db.flush()
    await db.refresh(budget)
    return BudgetOut.model_validate(budget)


@router.get("/budgets", response_model=list[BudgetOut])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id).order_by(Budget.created_at.desc())
    )
    return [BudgetOut.model_validate(b) for b in result.scalars().all()]
