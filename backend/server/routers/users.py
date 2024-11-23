from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.server.auth import get_current_user
from backend.logger import logger
from backend.modules.metadata_store.client import get_client
from typing import Dict, Any

router = APIRouter(prefix="/v1/users", tags=["users"])

# DELETE - DELETE /users/me/team/users/{user_id} (Remove user from team)
@router.delete("/{user_id}", response_model=Dict[str, Any])
async def remove_user(user_id: int):
    """Remove a user from the current user's team."""
    try:
        client = await get_client()
        deleted_user = await client.db.user.delete(where={'id': user_id})

        if not deleted_user:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(content={"message": "User removed"}) # Or return 204 No Content

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to remove user from team: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_user_profile(user: dict = Depends(get_current_user)):
    """Get all users in the team owned by the current user."""
    try:
        client = await get_client()

        # Fetch the team owned by the user
        user = await client.db.user.find_first(where={'auth0_id': user['sub']})
        if not user:
            raise HTTPException(status_code=404, detail="Team not found")

        return JSONResponse(content={'user': user.model_dump()})

    except Exception as e:
        logger.exception(f"Failed to get users in team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all/users")
async def get_all_users_in_team(user: dict = Depends(get_current_user)):
    """Get all users in the team owned by the current user."""
    try:
        client = await get_client()

        # Fetch the team owned by the user
        users = await client.db.user.find_many()
        user_data = [user.model_dump() for user in users]

        return JSONResponse(content={'users': user_data})

    except Exception as e:
        logger.exception(f"Failed to get users in team: {e}")
        raise HTTPException(status_code=500, detail=str(e))