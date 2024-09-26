import React from 'react'
import icon from '@/assets/img/errors/404.svg'
import { useAuth0 } from "@auth0/auth0-react";
import LogoutButton from "@/components/LogoutButton";
import LoginButton from "@/components/LoginButton";

const Home = () => {
  const { isAuthenticated } = useAuth0();
  return (
    <div className="w-full h-screen grid place-items-center">
      <div className="flex flex-col sm:flex-row gap-4 items-center sm:pb-72">
        <img src={icon} />
        <div className="divider sm:divider-horizontal" />
        <div className="flex flex-col gap-2">
          <h2 className="font-inter font-black text-6xl">Home Page</h2>
          <div className="font-semibold">
            You are currently in the home page.
            {isAuthenticated && (
              <>
                <br />
                If you want to go to the dashboard please click the below link.
                <br />
                <a
                  className="link text-primary"
                  href="/dashboard"
                >
                  Dashboard
                </a>
                <br />
                If you want to go to logout please click the below link.
                <br />
                <LogoutButton></LogoutButton>
              </>
            )}

            {!isAuthenticated && (
              <>
                <br />
                If you want to go to login please click the below link.
                <br />
                <LoginButton></LoginButton>
              </>
            )}
            
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
