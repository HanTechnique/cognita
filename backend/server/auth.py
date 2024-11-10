import jwt
from fastapi import Depends, HTTPException
from jwt import PyJWTError
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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
    return verify_jwt(token)
