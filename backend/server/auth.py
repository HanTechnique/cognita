import jwt
from fastapi import Depends, HTTPException
from jwt import PyJWTError
import requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.modules.metadata_store.prismastore import PrismaStore
from backend.types.user import CreateUserDto  # Import your user creation DTO
from backend.types.team import CreateTeamDto, TeamType
from backend.modules.metadata_store.client import get_client
from fastapi.responses import JSONResponse
from backend.logger import logger
from datetime import datetime, timezone

AUTH0_DOMAIN = 'hantech.auth0.com'
API_IDENTIFIER = 'JDDLTMncmXxrfSlAaFAtSygbkEETFYga'
ALGORITHMS = ['RS256']

# Fetch public keys from Auth0 (only needs to be done once)
def get_jwk_keys():
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()['keys']

jwks = get_jwk_keys()

# Utility function to verify and decode the JWT token
def verify_jwt(token: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
        
        rsa_key = {}
        for key in jwks:
            if key['kid'] == unverified_header['kid']:
                rsa_key = key  # Assign the entire key, not just the dict

        if rsa_key:
            # Extract 'n' and 'e' values for the RSA key
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk({
                'kty': rsa_key['kty'],
                'kid': rsa_key['kid'],
                'use': rsa_key['use'],
                'n': rsa_key['n'],
                'e': rsa_key['e']
            })

            payload = jwt.decode(
                token,
                key=public_key,  # Use the constructed public_key here
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        else:
            raise HTTPException(status_code=401, detail="Invalid token: Key ID not found")

    except PyJWTError as jwtError:
        print(str(jwtError))
        raise HTTPException(status_code=401, detail="Token validation failed")

# Dependency to extract and verify the token
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = verify_jwt(token)  # Decode the token

    # Extract user information from the token
    auth0_id = user_data.get('sub')
    name = user_data.get('name')
    email = user_data.get('email')



    if auth0_id and name and email:  # Check if necessary information is present

        # Create the user if they don't exist (using a DTO for data validation)
        user_dto = CreateUserDto(auth0_id=auth0_id, name=name, email=email)
        user_created = await signup(user_dto)

        if user_created: # Log only if the user has been created for the first time
            logger.info(f"New user signed up: {auth0_id}")


    return user_data  # Return the decoded token data (or user data from db if you prefer)

async def signup(user_data: CreateUserDto):
    """Signs up a new user, creates a team and assigns the free plan."""
    try:
        client = await get_client()

        # 1. Check if user with the given auth0_id already exists.
        existing_user = await client.db.user.find_first(where={'auth0_id': user_data.auth0_id})
        if existing_user:
            return False

        # 2. Create the new user
        new_user = await client.db.user.create(data=user_data.model_dump(exclude_unset=True))

        # 3. Get or create the free plan (assuming you have a predefined free plan)
        free_plan = await client.db.plan.find_first(where={'name': 'Free'})  # Replace 'Free' with your free plan identifier
        if not free_plan:
            raise HTTPException(status_code=500, detail="Free plan not found!")  # Should not happen in normal operation

        # 4. Create a new team
        team_data = CreateTeamDto(
            name=f"{new_user.name}'s Team",  # Or any other suitable team name generation logic
            type=TeamType.personal,
            plan_id=free_plan.id,
            owner_id=new_user.auth0_id,
        )
        new_team = await client.db.team.create(data=team_data.model_dump())


        # 5. Add the user to the newly created team (UserOnTeam association)
        await client.db.useronteam.create(
            data={
                'user_id': new_user.id, 
                'team_id': new_team.id,
                'joined_at': datetime.now(timezone.utc),  # Set joined_at to the current UTC time
                'role': 'ADMIN', # Or another default role
            }
        )

        return True


    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        logger.exception(f"Failed to sign up user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
