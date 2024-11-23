from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.server.auth import get_current_user
from backend.logger import logger
from backend.modules.metadata_store.client import get_client
from decimal import Decimal

router = APIRouter(prefix="/v1/plans", tags=["plans"])

@router.get("/all/plans")
async def get_all_plans(user: dict = Depends(get_current_user)):
    """Get all teams."""
    try:
        client = await get_client()

        # Fetch the plans
        plans = await client.db.plan.find_many()
        # Convert Decimal objects to floats or strings before JSON serialization
        plan_data = [
            {k: float(v) if isinstance(v, Decimal) else v for k, v in plan.model_dump().items()}  # Convert Decimals to float
            for plan in plans
        ]

        return JSONResponse(content={'plan_data': plan_data})

    except Exception as e:
        logger.exception(f"Failed to get plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/initialize")
async def initialize(user: dict = Depends(get_current_user)):
    """Initialize all plans."""
    try:
        client = await get_client()

        # Check if plans already exist to avoid duplicates
        free_plan = await client.db.plan.find_first(where={'name': 'Free'})
        basic_plan = await client.db.plan.find_first(where={'name': 'Basic'})

        if not free_plan:
            await client.db.plan.create(
                data={
                    'name': 'Free',
                    'price': 0,
                    'requestsPerDay': [100],  # Or appropriate data type for your schema
                    'models': ['4o-mini'],      # Adapt to your schema
                }
            )
            print('Free plan created.')
        else:
            print("Free plan already exists.")

        if not basic_plan:
            await client.db.plan.create(
                data={
                    'name': 'Basic',
                    'price': 5,        # Or 5.00 if decimal
                    'requestsPerDay': [1000,100],  # Or appropriate data type
                    'models': ['4o-mini', '4o'], # Adapt as needed
                }
            )
            print('Basic plan created.')
        else:
            print("Basic plan already exists.")

        return JSONResponse(content={'status': "OK"})

    except Exception as e:
        logger.exception(f"Failed to get plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))
