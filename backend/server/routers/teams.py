from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.server.auth import get_current_user
from backend.logger import logger
from backend.modules.metadata_store.client import get_client
from typing import Dict, Any

router = APIRouter(prefix="/v1/teams", tags=["teams"])

@router.get("/users")
async def get_users_in_team(team_id: int, user: dict = Depends(get_current_user)):
    """Get all users in the team owned by the current user."""
    try:
        client = await get_client()

        # Fetch the team owned by the user
        team = await client.db.team.find_first(where={'owner_id': user['sub'], 'id': team_id})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Fetch users associated with the team
        users_in_team = await client.db.useronteam.find_many(
            where={'team_id': team.id},
            include={'users': True}  # Include user details
        )

        # Extract user data from the results
        user_data = [user_team.users.model_dump() for user_team in users_in_team]

        return JSONResponse(content={'users': user_data})

    except Exception as e:
        logger.exception(f"Failed to get users in team: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/")
async def get_users_in_team(user: dict = Depends(get_current_user)):
    """Get all users in the team owned by the current user."""
    try:
        client = await get_client()

        # Fetch the team owned by the user
        team = await client.db.team.find_first(where={'owner_id': user['sub']})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return JSONResponse(content={'team': team.model_dump()})

    except Exception as e:
        logger.exception(f"Failed to get users in team: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all/teams")
async def get_all_teams(user: dict = Depends(get_current_user)):
    """Get all teams."""
    try:
        client = await get_client()

        # Fetch the teams
        teams = await client.db.team.find_many()
        team_data = [team.model_dump() for team in teams]

        return JSONResponse(content={'teams': team_data})

    except Exception as e:
        logger.exception(f"Failed to get teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))